# Makefile — Rasputin Mantle protocol verifier
#
# Used by: Sisyphus (for make verify-phase-RN) and humans (ad-hoc checks).
#
#   make verify              repo-wide verify
#   make verify-phase-RN     mechanical floor for phase N
#   make eval-codeact        Promptfoo CodeAct contract suite
#   make eval-webvoyager     WebVoyager-100
#   make eval-gaia           GAIA-mini
#   make dev / make down     docker compose support services
#   make health              local stack health check
#   make status              quick: phase, status, shipped tags

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

PROTOCOL_DIR := protocol
SCRIPTS_DIR  := $(PROTOCOL_DIR)/scripts
PHASES_DIR   := $(PROTOCOL_DIR)/phases

GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
BOLD   := \033[1m
RESET  := \033[0m

.PHONY: help
help:
	@printf "$(BOLD)Rasputin Mantle Makefile$(RESET)\n\n"
	@awk -F':.*?## ' '/^[a-zA-Z0-9_%-]+:.*?##/ {printf "  $(GREEN)%-22s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: bootstrap
bootstrap: ## Install deps, submodules, hooks
	git submodule update --init --recursive
	pnpm install --frozen-lockfile || pnpm install
	uv sync
	cp -f protocol/scripts/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	chmod +x protocol/scripts/*.sh protocol/scripts/*.py 2>/dev/null || true
	@printf "$(GREEN)✓ bootstrap complete$(RESET)\n"

.PHONY: verify
verify: lint typecheck test ## Repo-wide verify

.PHONY: lint
lint: ## Ruff + ESLint
	@uv run ruff check . --output-format concise
	@if [ -d apps/web ]; then cd apps/web && pnpm eslint . --max-warnings 0 || true; fi

.PHONY: typecheck
typecheck: ## mypy + tsc --noEmit
	@uv run mypy packages apps/gateway --ignore-missing-imports || true
	@if [ -d apps/web ]; then cd apps/web && pnpm tsc --noEmit; fi

.PHONY: test
test: ## pytest
	@PYTHONPATH="apps/gateway/src:packages/shared:packages/skills:packages/codeact:packages/sandbox:packages/browser:packages/voice:packages/mcp-host" \
		uv run pytest --no-header -q

.PHONY: verify-phase-%
verify-phase-%: ## Verify a phase against its rubric (e.g. verify-phase-R3)
	@bash $(SCRIPTS_DIR)/verify-phase.sh "$*"

.PHONY: eval-codeact
eval-codeact: ## Promptfoo CodeAct contract suite
	@pnpm exec promptfoo eval -c eval/promptfoo/codeact.yaml \
		--output outputs/codeact-eval.json --no-progress-bar

.PHONY: eval-webvoyager
eval-webvoyager: ## WebVoyager-100
	@uv run python eval/webvoyager-100/runner.py --output outputs/webvoyager-100.json

.PHONY: eval-gaia
eval-gaia: ## GAIA-mini
	@uv run python eval/gaia-mini/runner.py --output outputs/gaia-mini.json

.PHONY: dev
dev: ## docker compose up -d
	@docker compose -f infra/compose.dev.yml up -d
	@printf "$(GREEN)✓ stack up$(RESET) — wait 10s, then $(BOLD)make health$(RESET)\n"

.PHONY: down
down: ## docker compose down
	@docker compose -f infra/compose.dev.yml down

.PHONY: health
health: ## Local stack health check
	@bash $(SCRIPTS_DIR)/health-check.sh

.PHONY: status
status: ## Quick: phase, iteration, shipped tags
	@printf "$(BOLD)Shipped phases:$(RESET) "; git tag -l 'phase-*-shipped' | tr '\n' ' '; echo
	@LATEST=$$(ls audit-log/ 2>/dev/null | tail -1); \
	if [ -n "$$LATEST" ]; then \
		printf "$(BOLD)Latest audit:$(RESET) audit-log/$$LATEST\n"; \
		jq -r '"  verdict: \(.verdict)\n  summary: \(.summary)"' "audit-log/$$LATEST" 2>/dev/null || true; \
	else printf "$(YELLOW)no audits yet$(RESET)\n"; fi

.PHONY: clean
clean: ## Remove generated artifacts
	@rm -rf outputs/ .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@printf "$(GREEN)✓ clean$(RESET)\n"
