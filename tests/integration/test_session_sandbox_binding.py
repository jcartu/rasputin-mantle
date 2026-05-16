from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from gateway.routes.sessions import create_session, delete_session, exec_code_route
from gateway.sessions import SessionStore
from shared.schemas import ExecRequestSchema
from shared.types import SessionInfo, SessionStatus


@pytest.fixture
def mock_backend():
    """Mock sandbox backend for testing."""
    backend = MagicMock()
    backend.create.return_value = "test-sandbox-id-12345"
    backend.exec_code.return_value = MagicMock(stdout="output", stderr="", exit_code=0)
    backend.destroy.return_value = None
    return backend


@pytest.fixture
def session_store():
    """Fresh session store for each test."""
    store = SessionStore()
    return store


@pytest.mark.asyncio
async def test_create_session_spawns_sandbox(mock_backend):
    """Test that create_session spawns a sandbox and returns sandbox_id."""
    with patch("gateway.routes.sessions.create_backend", return_value=mock_backend):
        with patch("gateway.routes.sessions.store", SessionStore()):
            result = await create_session()

            # Verify backend.create() was called
            mock_backend.create.assert_called_once()

            # Verify sandbox_id is set in response
            assert result.sandbox_id == "test-sandbox-id-12345"
            assert result.status == SessionStatus.ACTIVE
            assert result.session_id is not None
            assert result.created_at > 0


@pytest.mark.asyncio
async def test_exec_code_uses_session_sandbox_id(mock_backend):
    """Test that exec_code_route uses the session's sandbox_id."""
    store = SessionStore()
    session_id = "test-session-123"
    sandbox_id = "test-sandbox-456"

    # Create a session with a sandbox_id
    session = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=sandbox_id,
    )
    store.create(session)

    with patch("gateway.routes.sessions.create_backend", return_value=mock_backend):
        with patch("gateway.routes.sessions.store", store):
            request = ExecRequestSchema(session_id=session_id, code="print('hello')")
            result = await exec_code_route(session_id, request)

            # Verify backend.exec_code was called with correct sandbox_id
            mock_backend.exec_code.assert_called_once_with(sandbox_id, "print('hello')")

            # Verify result is returned
            assert result.stdout == "output"
            assert result.exit_code == 0


@pytest.mark.asyncio
async def test_delete_session_destroys_sandbox(mock_backend):
    """Test that delete_session destroys the sandbox."""
    store = SessionStore()
    session_id = "test-session-789"
    sandbox_id = "test-sandbox-999"

    # Create a session with a sandbox_id
    session = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=sandbox_id,
    )
    store.create(session)

    with patch("gateway.routes.sessions.create_backend", return_value=mock_backend):
        with patch("gateway.routes.sessions.store", store):
            result = await delete_session(session_id)

            # Verify backend.destroy was called with correct sandbox_id
            mock_backend.destroy.assert_called_once_with(sandbox_id)

            # Verify session is removed from store
            assert store.get(session_id) is None

            # Verify response
            assert result == {"status": "deleted"}


@pytest.mark.asyncio
async def test_delete_session_without_sandbox(mock_backend):
    """Test that delete_session handles sessions without sandbox_id gracefully."""
    store = SessionStore()
    session_id = "test-session-no-sandbox"

    # Create a session without a sandbox_id
    session = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=None,
    )
    store.create(session)

    with patch("gateway.routes.sessions.create_backend", return_value=mock_backend):
        with patch("gateway.routes.sessions.store", store):
            result = await delete_session(session_id)

            # Verify backend.destroy was NOT called
            mock_backend.destroy.assert_not_called()

            # Verify session is removed from store
            assert store.get(session_id) is None

            # Verify response
            assert result == {"status": "deleted"}


@pytest.mark.asyncio
async def test_exec_code_fails_without_sandbox_id(mock_backend):
    """Test that exec_code_route fails if session has no sandbox_id."""
    from fastapi import HTTPException

    store = SessionStore()
    session_id = "test-session-no-sandbox"

    # Create a session without a sandbox_id
    session = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=None,
    )
    store.create(session)

    with patch("gateway.routes.sessions.create_backend", return_value=mock_backend):
        with patch("gateway.routes.sessions.store", store):
            request = ExecRequestSchema(session_id=session_id, code="print('hello')")

            with pytest.raises(HTTPException) as exc_info:
                await exec_code_route(session_id, request)

            # Verify error details
            assert exc_info.value.status_code == 500
            assert "no_sandbox" in str(exc_info.value.detail)
