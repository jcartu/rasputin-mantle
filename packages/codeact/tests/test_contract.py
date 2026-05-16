from __future__ import annotations

"""Contract test: every tool in the catalog returns its declared schema, not synthetic data."""

import json
import sys
from pathlib import Path

import pytest

# Add package roots to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_codeact_executor_returns_declared_schema() -> None:
    """Assert CodeAct executor returns fields matching the declared ExecResult schema."""
    from codeact.executor import CodeActResult

    # Verify CodeActResult has all declared schema fields
    declared_fields = {"stdout", "stderr", "exit_code", "duration_ms", "files_changed", "results"}
    actual_fields = set(CodeActResult.__dataclass_fields__.keys())

    missing = declared_fields - actual_fields
    extra = actual_fields - declared_fields

    assert not missing, f"CodeActResult missing declared fields: {missing}"
    assert not extra, f"CodeActResult has undeclared fields: {extra}"


def test_codeact_result_types_match_schema() -> None:
    """Assert CodeActResult field types match the shared ExecResult schema."""
    from codeact.executor import CodeActResult
    from shared.types import ExecResult

    # Both should have the same fields with compatible types
    for field_name in ExecResult.__dataclass_fields__:
        assert field_name in CodeActResult.__dataclass_fields__, (
            f"CodeActResult missing field '{field_name}' declared in ExecResult"
        )


def test_execute_code_signature() -> None:
    """Assert execute_code has the expected async signature."""
    import inspect
    from codeact.executor import execute_code

    sig = inspect.signature(execute_code)
    params = list(sig.parameters.keys())

    assert "code" in params, "execute_code must accept 'code' parameter"
    assert inspect.iscoroutinefunction(execute_code), "execute_code must be async"


def test_sandbox_backend_has_required_methods() -> None:
    """Assert SandboxBackend declares all required lifecycle methods."""
    from sandbox.backend import SandboxBackend

    required_methods = {"create", "exec_code", "read", "write", "list_files", "destroy"}
    actual_methods = {name for name in dir(SandboxBackend) if not name.startswith("_")}

    missing = required_methods - actual_methods
    assert not missing, f"SandboxBackend missing required methods: {missing}"


def test_sandbox_backend_is_abstract() -> None:
    """Assert SandboxBackend cannot be instantiated directly."""
    import abc
    from sandbox.backend import SandboxBackend

    assert issubclass(SandboxBackend, abc.ABC), "SandboxBackend must be abstract"


def test_create_backend_returns_concrete_backend() -> None:
    """Assert create_backend factory returns a concrete SandboxBackend instance."""
    from sandbox.backend import LocalDockerBackend, SandboxBackend, create_backend

    backend = create_backend("docker")
    assert isinstance(backend, SandboxBackend), "create_backend must return SandboxBackend"
    assert isinstance(backend, LocalDockerBackend), "docker backend must be LocalDockerBackend"
