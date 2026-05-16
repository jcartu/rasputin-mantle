"""Rasputin Mantle Orchestrator.

Coordinates the execution of protocol phases and manages the overall build lifecycle.

Boot sequence:
  1. Load .env (python-dotenv)
  2. Validate required env vars
  3. Instantiate agents (Auditor, Planner, Executor)
  4. Ping each agent for connectivity
  5. Load or initialize state from JSON file

Cycle:
  1. Load phase rubric
  2. Run planner to decompose rubric into tickets
  3. Dispatch executor per ticket
  4. Run mechanical floor (make verify-phase-RN)
  5. Call auditor (Opus) for verdict
  6. Update state
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from protocol.agents.auditor import Auditor
from protocol.agents.executor import Executor
from protocol.agents.planner import Planner
from protocol.state import State

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for Rasputin Mantle protocol execution."""

    def __init__(
        self,
        state_file: str = "state.json",
        phase: str = "R0",
        dry_run: bool = False,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            state_file: Path to the JSON state file.
            phase: Current phase identifier (e.g., 'R0').
            dry_run: If True, skip actual execution and only validate config.
        """
        self.state_file = state_file
        self.phase = phase
        self.dry_run = dry_run
        self.state = State(state_file)
        self.auditor: Auditor | None = None
        self.planner: Planner | None = None
        self.executor: Executor | None = None

    def _load_env(self) -> dict[str, str]:
        """Load environment variables from .env file.

        Returns:
            Dict of loaded environment variables.

        Raises:
            RuntimeError: If required env vars are missing after loading.
        """
        # Load from .env in project root
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded .env from %s", env_path)
        else:
            logger.warning("No .env file found, using system environment")

        # Validate required env vars
        required = {
            "ANTHROPIC_API_KEY": "Anthropic API key for auditor",
            "VLLM_BASE_URL": "vLLM base URL for planner/executor",
        }
        missing = []
        for key, desc in required.items():
            val = os.environ.get(key)
            if not val:
                missing.append(f"{key} ({desc})")

        if missing:
            raise RuntimeError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        return {k: os.environ.get(k, "") for k in required}

    def _validate_config(self) -> dict[str, Any]:
        """Validate that all required configuration is present.

        Returns:
            Dict with validated configuration values.
        """
        config = {
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "vllm_base_url": os.environ.get("VLLM_BASE_URL", ""),
            "vllm_api_key": os.environ.get("VLLM_API_KEY", "dummy"),
            "vllm_model": os.environ.get("VLLM_MODEL", "qwen3.6-27b"),
            "phase": self.phase,
            "state_file": self.state_file,
        }
        return config

    def boot(self) -> dict[str, Any]:
        """Boot the orchestrator.

        Loads .env, validates config, instantiates agents, pings each agent,
        and loads state from the JSON file.

        Returns:
            Dict with boot status and agent connectivity results.

        Raises:
            RuntimeError: If required env vars are missing.
        """
        # Load environment
        self._load_env()
        config = self._validate_config()

        # Load state
        self.state.load()
        logger.info("State loaded from %s", self.state.path)

        # Instantiate agents
        self.auditor = Auditor(
            api_key=config["anthropic_api_key"],
            model="claude-opus-4-20250514",
        )
        self.planner = Planner(
            base_url=config["vllm_base_url"],
            model=config["vllm_model"],
            api_key=config["vllm_api_key"],
        )
        self.executor = Executor(
            base_url=config["vllm_base_url"],
            model=config["vllm_model"],
            api_key=config["vllm_api_key"],
        )

        # Ping agents
        results = {
            "auditor": self.auditor.ping(),
            "planner": self.planner.ping(),
            "executor": self.executor.ping(),
        }
        logger.info("Agent ping results: %s", results)

        # Save initial state
        self.state.set("phase", self.phase)
        self.state.set("boot_status", "ok")
        self.state.set("agent_connectivity", results)
        self.state.save()

        return {
            "status": "booted",
            "phase": self.phase,
            "agent_connectivity": results,
        }

    def run_cycle(self) -> dict[str, Any]:
        """Run a single orchestration cycle.

        Executes the main loop: load phase rubric, run planner, dispatch executor,
        run mechanical floor verification, call auditor, update state.

        Returns:
            Dict with cycle results including audit verdict.
        """
        if not self.planner or not self.executor or not self.auditor:
            raise RuntimeError("Orchestrator not booted. Call boot() first.")

        # Load phase rubric
        rubric_path = Path(f"protocol/phases/phase-{self.phase}.yaml")
        if not rubric_path.exists():
            raise RuntimeError(f"Phase rubric not found: {rubric_path}")

        with open(rubric_path) as f:
            rubric_text = f.read()

        # Load prompts
        planner_prompt_path = Path("protocol/prompts/planner.md")
        if not planner_prompt_path.exists():
            raise RuntimeError(f"Planner prompt not found: {planner_prompt_path}")

        with open(planner_prompt_path) as f:
            planner_prompt = f.read()

        # Run planner
        logger.info("Planning phase %s...", self.phase)
        plan_result = self.planner.plan(
            system_prompt=planner_prompt,
            user_message=f"Phase rubric:\n\n{rubric_text}",
        )

        # Run mechanical floor
        logger.info("Running mechanical floor for phase %s...", self.phase)
        verify_result = subprocess.run(
            ["make", f"verify-phase-{self.phase}"],
            capture_output=True,
            text=True,
        )

        if verify_result.returncode != 0:
            logger.warning(
                "Mechanical floor failed for phase %s. Skipping audit.", self.phase
            )
            self.state.set("mechanical_floor", "failed")
            self.state.set("verify_output", verify_result.stdout)
            self.state.save()
            return {
                "status": "mechanical_floor_failed",
                "phase": self.phase,
                "verify_output": verify_result.stdout,
            }

        self.state.set("mechanical_floor", "passed")
        self.state.save()

        # Run auditor
        logger.info("Auditing phase %s...", self.phase)
        auditor_prompt_path = Path("protocol/prompts/auditor-strict.md")
        with open(auditor_prompt_path) as f:
            auditor_prompt = f.read()

        audit_result = self.auditor.audit(
            system_prompt=auditor_prompt,
            user_message=f"Phase rubric:\n\n{rubric_text}\n\nPlan result:\n\n{plan_result['text']}",
        )

        # Update state with audit result
        self.state.set("audit_verdict", audit_result["verdict"])
        self.state.set("audit_reasoning", audit_result["reasoning"])
        self.state.save()

        return {
            "status": "cycle_complete",
            "phase": self.phase,
            "verdict": audit_result["verdict"],
            "reasoning": audit_result["reasoning"],
        }


def main() -> None:
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(description="Rasputin Mantle Orchestrator")
    parser.add_argument(
        "--phase",
        default="R0",
        help="Phase to execute (default: R0)",
    )
    parser.add_argument(
        "--state-file",
        default="state.json",
        help="Path to the state JSON file (default: state.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config without executing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    orchestrator = Orchestrator(
        state_file=args.state_file,
        phase=args.phase,
        dry_run=args.dry_run,
    )

    try:
        result = orchestrator.boot()
        logger.info("Boot result: %s", json.dumps(result, indent=2))

        if args.dry_run:
            logger.info("Dry run complete. Exiting.")
            sys.exit(0)

        result = orchestrator.run_cycle()
        logger.info("Cycle result: %s", json.dumps(result, indent=2))

        if result.get("verdict") == "PERFECT":
            logger.info("Phase %s: PERFECT. Ready to tag.", args.phase)
        else:
            logger.info(
                "Phase %s: %s. Review punch list.",
                args.phase,
                result.get("verdict", "UNKNOWN"),
            )

    except RuntimeError as e:
        logger.error("Orchestrator error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
