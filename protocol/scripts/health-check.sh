#!/usr/bin/env bash
# protocol/scripts/health-check.sh
# Verify support services and external endpoints are reachable.
# Exit 0 if critical services are healthy. Warnings for not-yet-needed services.

set -uo pipefail
if [ -f .env ]; then set -a; . .env; set +a; fi

if [ -t 1 ]; then GREEN="$(tput setaf 2)"; RED="$(tput setaf 1)"; YELLOW="$(tput setaf 3)"; BOLD="$(tput bold)"; RESET="$(tput sgr0)"; else GREEN=""; RED=""; YELLOW=""; BOLD=""; RESET=""; fi
ok()   { printf "  ${GREEN}✓${RESET} %-25s %s\n" "$1" "$2"; }
warn() { printf "  ${YELLOW}!${RESET} %-25s %s\n" "$1" "$2"; warns=$((warns+1)); }
fail() { printf "  ${RED}✗${RESET} %-25s %s\n" "$1" "$2"; fails=$((fails+1)); }

fails=0; warns=0
printf "${BOLD}Health check${RESET}\n"

# Critical: vLLM
if curl -sS -m 5 -H "Authorization: Bearer ${VLLM_API_KEY:-x}" "${VLLM_BASE_URL:-http://127.0.0.1:8000}/v1/models" 2>/dev/null | grep -q '"object"\s*:\s*"list"'; then
  ok "vLLM (qwen3.5-27b-local)" "${VLLM_BASE_URL:-127.0.0.1:8000}"
else
  fail "vLLM" "${VLLM_BASE_URL:-127.0.0.1:8000} unreachable"
fi

# Critical: Anthropic
if [ -n "${ANTHROPIC_API_KEY:-}" ] && [ "$ANTHROPIC_API_KEY" != "__SET_ME__" ]; then
  if curl -sS -m 10 -X POST "https://api.anthropic.com/v1/messages" \
       -H "x-api-key: $ANTHROPIC_API_KEY" \
       -H "anthropic-version: 2023-06-01" \
       -H "content-type: application/json" \
       -d '{"model":"claude-opus-4-7","max_tokens":4,"messages":[{"role":"user","content":"ping"}]}' \
       2>/dev/null | grep -q '"type"\s*:\s*"message"'; then
    ok "Anthropic Opus" "ready"
  else
    fail "Anthropic Opus" "test call failed — check ANTHROPIC_API_KEY"
  fi
else
  fail "ANTHROPIC_API_KEY" "not set"
fi

# Postgres (required for memory)
if docker compose -f infra/compose.dev.yml ps postgres 2>/dev/null | grep -qE 'running|healthy'; then
  ok "Postgres" "compose"
else
  warn "Postgres" "not running — required by R5"
fi

# Neko
if curl -sS -m 5 "http://127.0.0.1:${NEKO_PORT:-8080}/" 2>/dev/null | grep -qi 'neko\|<html'; then
  ok "Neko WebRTC" "127.0.0.1:${NEKO_PORT:-8080}"
else
  warn "Neko WebRTC" "not yet up — required by R4"
fi

# Faster-Whisper
if curl -sS -m 5 "http://127.0.0.1:${FASTER_WHISPER_PORT:-8803}/health" 2>/dev/null | grep -qi 'ok\|ready'; then
  ok "Faster-Whisper STT" "127.0.0.1:${FASTER_WHISPER_PORT:-8803}"
else
  warn "Faster-Whisper STT" "not yet up — required by R6"
fi

# Kokoro
if curl -sS -m 5 "http://127.0.0.1:${KOKORO_PORT:-8804}/health" 2>/dev/null | grep -qi 'ok\|ready'; then
  ok "Kokoro TTS" "127.0.0.1:${KOKORO_PORT:-8804}"
else
  warn "Kokoro TTS" "not yet up — required by R6"
fi

# rasputin-memory
if curl -sS -m 5 "http://127.0.0.1:${RASPUTIN_MEMORY_PORT:-7777}/stats" 2>/dev/null | grep -q '{'; then
  ok "rasputin-memory" "127.0.0.1:${RASPUTIN_MEMORY_PORT:-7777}"
else
  warn "rasputin-memory" "not yet up — required by R5"
fi

echo ""
if [ $fails -eq 0 ]; then
  if [ $warns -eq 0 ]; then
    printf "${GREEN}${BOLD}✓ all healthy${RESET}\n"
  else
    printf "${GREEN}${BOLD}✓ critical services healthy${RESET} ${YELLOW}(${warns} warnings)${RESET}\n"
  fi
  exit 0
else
  printf "${RED}${BOLD}✗ ${fails} critical service(s) down${RESET}\n"
  exit 1
fi
