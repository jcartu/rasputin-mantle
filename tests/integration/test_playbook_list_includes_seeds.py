from __future__ import annotations

from fastapi.testclient import TestClient
from gateway.app import app

client = TestClient(app)

def test_playbook_list_includes_seeds() -> None:
    response = client.get("/api/playbooks")
    assert response.status_code == 200
    playbooks = response.json()
    
    # Should include the 8 seed playbooks
    seed_ids = [
        "competitor-analysis",
        "literature-review",
        "landing-page",
        "internal-dashboard",
        "meeting-recap",
        "weekly-news-digest",
        "daily-standup",
        "weekly-report",
    ]
    
    for seed_id in seed_ids:
        assert any(p["id"] == seed_id for p in playbooks), f"Missing seed playbook: {seed_id}"
