from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from gateway.app import app
from gateway.config import settings
from gateway.routes.sessions import store


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'version': '0.1.0'}


def test_session_crud() -> None:
    store.clear()
    client = TestClient(app)
    created = client.post('/api/sessions')
    assert created.status_code == 200
    session = created.json()
    assert session['status'] == 'active'
    assert session['cost_tokens'] == 0
    assert session['cost_dollars'] == 0.0
    fetched = client.get(f"/api/sessions/{session['session_id']}")
    assert fetched.status_code == 200
    assert fetched.json()['session_id'] == session['session_id']
    listed = client.get('/api/sessions')
    assert listed.status_code == 200
    assert [item['session_id'] for item in listed.json()] == [session['session_id']]


def test_skills_listing(tmp_path: Path) -> None:
    skills_root = tmp_path / 'skills'
    skill_dir = skills_root / 'demo'
    skill_dir.mkdir(parents=True)
    skill_md = (
        '---\n'
        'name: demo\n'
        'description: Demo skill\n'
        'version: 0.1.0\n'
        'capability: demo\n'
        'license: MIT\n'
        'metadata:\n'
        '  hermes:\n'
        '    tags: [test]\n'
        '---\n'
        '\n'
        '# Demo\n'
        '\n'
        'This is a markdown playbook \u2014 invoke via bash, not skill_mcp()'
    )
    (skill_dir / 'SKILL.md').write_text(skill_md, encoding='utf-8')
    original_skills_dir = settings.skills_dir
    settings.skills_dir = str(skills_root)
    try:
        client = TestClient(app)
        response = client.get('/api/skills')
    finally:
        settings.skills_dir = original_skills_dir
    assert response.status_code == 200
    body = response.json()
    assert body['skills'][0]['name'] == 'demo'
    assert body['skills'][0]['trust_level'] == 'bundled'


def test_cost_ceiling_middleware_returns_402_on_exceeded() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/health',
        headers={'X-Session-Id': 'session-cost-test', 'X-Session-Cost': '{"tokens": 0, "dollars": 41.0}'},
    )
    assert response.status_code == 402
    assert response.json()['error'] == 'cost_ceiling_exceeded'
