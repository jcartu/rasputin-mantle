from __future__ import annotations

from fastapi.testclient import TestClient
from gateway.app import app

client = TestClient(app)

def test_playbook_save_load() -> None:
    # Save a playbook
    save_response = client.post(
        "/api/playbooks",
        json={
            "session_id": "test-session-123",
            "title": "My Custom Playbook",
            "description": "A test playbook",
        },
    )
    assert save_response.status_code == 200
    saved_playbook = save_response.json()
    assert saved_playbook["title"] == "My Custom Playbook"
    assert saved_playbook["created_by"] == "you"
    playbook_id = saved_playbook["id"]

    # Load the playbook
    get_response = client.get(f"/api/playbooks/{playbook_id}")
    assert get_response.status_code == 200
    loaded_playbook = get_response.json()
    assert loaded_playbook["id"] == playbook_id
    assert loaded_playbook["title"] == "My Custom Playbook"

    # List playbooks includes the saved one
    list_response = client.get("/api/playbooks")
    assert list_response.status_code == 200
    playbooks = list_response.json()
    assert any(p["id"] == playbook_id for p in playbooks)
