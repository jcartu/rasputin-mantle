from __future__ import annotations

import subprocess

import pytest
from sandbox.backend import LocalDockerBackend


def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


class TestLocalDockerBackendLifecycle:
    """Test LocalDockerBackend: create, exec_code, read, write, list_files, destroy."""

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_create_and_destroy(self) -> None:
        """Test creating and destroying a sandbox container."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        assert session_id
        assert len(session_id) == 16  # uuid4().hex[:16]

        # Verify container exists by running a simple command
        result = backend.exec_code(session_id, "print('test')")
        assert result.exit_code == 0
        assert "test" in result.stdout

        # Cleanup
        backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_exec_code_hello_world(self) -> None:
        """Test executing Python code that prints 'hello'."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            result = backend.exec_code(session_id, "print('hello')")
            assert result.exit_code == 0
            assert "hello" in result.stdout
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_exec_code_with_error(self) -> None:
        """Test executing code that raises an error."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            result = backend.exec_code(session_id, "raise ValueError('test error')")
            assert result.exit_code != 0
            assert "ValueError" in result.stderr or "ValueError" in result.stdout
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_write_and_read_file(self) -> None:
        """Test writing a file to sandbox and reading it back."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            # Write a file
            test_content = "Hello from sandbox!"
            backend.write(session_id, "/workspace/test.txt", test_content)

            # Read it back
            read_content = backend.read(session_id, "/workspace/test.txt")
            assert read_content == test_content
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_list_files_confirms_write(self) -> None:
        """Test that list_files confirms a written file exists."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            # Write a file
            backend.write(session_id, "/workspace/myfile.txt", "content")

            # List files in workspace
            files = backend.list_files(session_id, "/workspace")
            assert "myfile.txt" in files
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_multiple_files_and_operations(self) -> None:
        """Test multiple write/read/list operations in sequence."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            # Write multiple files
            backend.write(session_id, "/workspace/file1.txt", "content1")
            backend.write(session_id, "/workspace/file2.txt", "content2")

            # List files
            files = backend.list_files(session_id, "/workspace")
            assert "file1.txt" in files
            assert "file2.txt" in files

            # Read both files
            content1 = backend.read(session_id, "/workspace/file1.txt")
            content2 = backend.read(session_id, "/workspace/file2.txt")
            assert content1 == "content1"
            assert content2 == "content2"

            # Execute code that uses the files
            result = backend.exec_code(
                session_id,
                """
with open('/workspace/file1.txt') as f:
    print(f.read())
""",
            )
            assert result.exit_code == 0
            assert "content1" in result.stdout
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_exec_code_with_multiple_statements(self) -> None:
        """Test executing multi-line Python code."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        try:
            code = """
x = 10
y = 20
print(f'Sum: {x + y}')
"""
            result = backend.exec_code(session_id, code)
            assert result.exit_code == 0
            assert "Sum: 30" in result.stdout
        finally:
            backend.destroy(session_id)

    @pytest.mark.skipif(not docker_available(), reason="Docker not available")
    def test_destroy_cleans_up_resources(self) -> None:
        """Test that destroy() removes container and volume."""
        backend = LocalDockerBackend()
        session_id = backend.create()

        # Verify container exists
        result = backend.exec_code(session_id, "print('exists')")
        assert result.exit_code == 0

        # Destroy
        backend.destroy(session_id)

        # Verify container is gone (exec should fail)
        result = subprocess.run(
            ["docker", "exec", f"mantle-sandbox-{session_id}", "echo", "test"],
            capture_output=True,
            timeout=5,
        )
        assert result.returncode != 0
