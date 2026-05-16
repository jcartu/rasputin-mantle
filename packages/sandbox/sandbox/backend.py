from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from sandbox.errors import SandboxBackendUnavailable, SandboxExecError

EXEC_TIMEOUT_SECONDS = 120
E2B_STUB_MESSAGE = (
    "E2B backend is stubbed for Phase 0/1. Set E2B_API_KEY and MANTLE_SANDBOX_BACKEND=e2b for Phase 2+."
)


@dataclass
class SandboxExecResult:
    stdout: str
    stderr: str
    exit_code: int


class SandboxBackend(ABC):
    @abstractmethod
    def create(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def exec_code(self, session_id: str, code: str) -> SandboxExecResult:
        raise NotImplementedError

    @abstractmethod
    def read(self, session_id: str, path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def write(self, session_id: str, path: str, data: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_files(self, session_id: str, path: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def destroy(self, session_id: str) -> None:
        raise NotImplementedError


def _container_name(session_id: str) -> str:
    return f"mantle-sandbox-{session_id}"


def _volume_name(session_id: str) -> str:
    return f"mantle-work-{session_id}"


def _run(command: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, check=False, text=True, timeout=EXEC_TIMEOUT_SECONDS)
    if check and result.returncode != 0:
        output = result.stderr or result.stdout
        raise SandboxExecError(output.strip())
    return result


class LocalDockerBackend(SandboxBackend):
    def create(self) -> str:
        session_id = uuid.uuid4().hex[:16]
        _run(["docker", "volume", "create", _volume_name(session_id)], check=True)
        _run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                _container_name(session_id),
                "-v",
                f"{_volume_name(session_id)}:/workspace",
                "python:3.12-slim",
                "sleep",
                "infinity",
            ],
            check=True,
        )
        return session_id

    def exec_code(self, session_id: str, code: str) -> SandboxExecResult:
        temp_dir = Path(tempfile.mkdtemp(prefix="mantle-codeact-"))
        temp_file = temp_dir / ".codeact_tmp.py"
        try:
            temp_file.write_text(code, encoding="utf-8")
            _run(["docker", "cp", str(temp_file), f"{_container_name(session_id)}:/workspace/.codeact_tmp.py"], check=True)
            result = _run(["docker", "exec", _container_name(session_id), "python3", "/workspace/.codeact_tmp.py"])
            return SandboxExecResult(stdout=result.stdout, stderr=result.stderr, exit_code=result.returncode)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def read(self, session_id: str, path: str) -> str:
        temp_dir = Path(tempfile.mkdtemp(prefix="mantle-read-"))
        try:
            _run(["docker", "cp", f"{_container_name(session_id)}:{path}", str(temp_dir)], check=True)
            return (temp_dir / PurePosixPath(path).name).read_text(encoding="utf-8")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def write(self, session_id: str, path: str, data: str) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="mantle-write-"))
        temp_file = temp_dir / PurePosixPath(path).name
        try:
            temp_file.write_text(data, encoding="utf-8")
            _run(["docker", "exec", _container_name(session_id), "mkdir", "-p", str(PurePosixPath(path).parent)], check=True)
            _run(["docker", "cp", str(temp_file), f"{_container_name(session_id)}:{path}"], check=True)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def list_files(self, session_id: str, path: str) -> list[str]:
        result = _run(["docker", "exec", _container_name(session_id), "ls", path], check=True)
        return [entry.strip() for entry in result.stdout.splitlines() if entry.strip()]

    def destroy(self, session_id: str) -> None:
        _run(["docker", "rm", "-f", _container_name(session_id)])
        _run(["docker", "volume", "rm", _volume_name(session_id)])


class E2BBackend(SandboxBackend):
    def create(self) -> str:
        if os.environ.get("MANTLE_E2B") != "1":
            raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)

    def exec_code(self, session_id: str, code: str) -> SandboxExecResult:
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)

    def read(self, session_id: str, path: str) -> str:
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)

    def write(self, session_id: str, path: str, data: str) -> None:
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)

    def list_files(self, session_id: str, path: str) -> list[str]:
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)

    def destroy(self, session_id: str) -> None:
        raise SandboxBackendUnavailable(E2B_STUB_MESSAGE)


def create_backend(backend: str | None = None) -> SandboxBackend:
    selected = backend or os.environ.get("MANTLE_SANDBOX_BACKEND", "docker")
    if selected == "docker":
        return LocalDockerBackend()
    if selected == "e2b":
        return E2BBackend()
    raise ValueError(f"Unsupported sandbox backend: {selected}")
