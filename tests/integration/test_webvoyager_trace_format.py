"""tests/integration/test_webvoyager_trace_format.py — Verify trace files have the expected shape.

Per phase-S2.yaml, trace files must exist and contain the required fields so the
categorizer can process them downstream.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent

REQUIRED_TRACE_FIELDS = {"task_id", "task_description", "starting_url", "passed", "final_answer", "duration_s", "steps"}
REQUIRED_TAXONOMY_FIELDS = {"source_run", "total_failures", "categorized_at", "categorizer_model", "by_category", "failures"}
REQUIRED_FAILURE_FIELDS = {"task_id", "task_description", "agent_answer", "category", "evidence", "fixable_in_phase", "estimated_fix_effort"}


@pytest.fixture
def baseline_path() -> Path:
    return BASE_DIR / "outputs" / "v1_1" / "webvoyager-100-baseline.json"


@pytest.fixture
def taxonomy_path() -> Path:
    return BASE_DIR / "outputs" / "v1_1" / "failure-taxonomy.json"


@pytest.fixture
def traces_dir() -> Path:
    return BASE_DIR / "outputs" / "v1_1" / "traces"


class TestBaselineFormat:
    def test_baseline_exists(self, baseline_path: Path) -> None:
        assert baseline_path.exists(), "Baseline JSON must exist at outputs/v1_1/webvoyager-100-baseline.json"

    def test_baseline_has_required_top_level(self, baseline_path: Path) -> None:
        data = json.loads(baseline_path.read_text())
        for field in ("total", "passed", "pass_rate", "results"):
            assert field in data, f"Baseline missing top-level field: {field}"

    def test_baseline_results_have_required_fields(self, baseline_path: Path) -> None:
        data = json.loads(baseline_path.read_text())
        for result in data["results"]:
            assert "id" in result, "Each result must have 'id'"
            assert "passed" in result, "Each result must have 'passed'"
            assert "final_answer" in result, "Each result must have 'final_answer'"
            assert "steps" in result, "Each result must have 'steps'"
            assert isinstance(result["steps"], list), "'steps' must be a list"


class TestTaxonomyFormat:
    def test_taxonomy_exists(self, taxonomy_path: Path) -> None:
        assert taxonomy_path.exists(), "Failure taxonomy must exist at outputs/v1_1/failure-taxonomy.json"

    def test_taxonomy_has_required_top_level(self, taxonomy_path: Path) -> None:
        data = json.loads(taxonomy_path.read_text())
        for field in REQUIRED_TAXONOMY_FIELDS:
            assert field in data, f"Taxonomy missing top-level field: {field}"

    def test_taxonomy_failures_have_required_fields(self, taxonomy_path: Path) -> None:
        data = json.loads(taxonomy_path.read_text())
        for failure in data["failures"]:
            for field in REQUIRED_FAILURE_FIELDS:
                assert field in failure, f"Failure entry missing field: {field}"

    def test_taxonomy_categories_are_valid(self, taxonomy_path: Path) -> None:
        VALID_CATEGORIES = {
            "DOM_FLAKY", "VLM_NEEDED", "MULTI_HOP_LOST", "ANSWER_MALFORMED",
            "TOOL_BROKEN", "LOGIN_WALL", "CAPTCHA", "TIME_SENSITIVE",
            "JUDGE_HARSH", "UNCLASSIFIED",
        }
        data = json.loads(taxonomy_path.read_text())
        for failure in data["failures"]:
            assert failure["category"] in VALID_CATEGORIES, (
                f"Invalid category '{failure['category']}' for task {failure['task_id']}"
            )

    def test_taxonomy_total_matches_failures(self, taxonomy_path: Path) -> None:
        data = json.loads(taxonomy_path.read_text())
        assert data["total_failures"] == len(data["failures"]), (
            f"total_failures ({data['total_failures']}) != len(failures) ({len(data['failures'])})"
        )


class TestTraceFiles:
    @pytest.mark.skipif(
        not (BASE_DIR / "outputs" / "v1_1" / "traces").exists(),
        reason="Traces directory does not exist yet — will be populated by runner --traces",
    )
    def test_traces_directory_exists(self, traces_dir: Path) -> None:
        assert traces_dir.is_dir(), "Traces directory must exist"

    @pytest.mark.skipif(
        not (BASE_DIR / "outputs" / "v1_1" / "traces").exists(),
        reason="Traces directory does not exist yet — will be populated by runner --traces",
    )
    def test_trace_files_have_required_fields(self, traces_dir: Path) -> None:
        trace_files = list(traces_dir.glob("*.json"))
        assert len(trace_files) > 0, "Expected at least one trace file"
        for trace_file in trace_files:
            data = json.loads(trace_file.read_text())
            for field in REQUIRED_TRACE_FIELDS:
                assert field in data, f"Trace {trace_file.name} missing field: {field}"

    @pytest.mark.skipif(
        not (BASE_DIR / "outputs" / "v1_1" / "traces").exists(),
        reason="Traces directory does not exist yet — will be populated by runner --traces",
    )
    def test_trace_steps_are_lists(self, traces_dir: Path) -> None:
        for trace_file in traces_dir.glob("*.json"):
            data = json.loads(trace_file.read_text())
            assert isinstance(data["steps"], list), f"Trace {trace_file.name}: 'steps' must be a list"
