import os
import pytest
import requests

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")

def is_gateway_running():
    try:
        # Just check if we can connect to the host/port
        requests.get(f"{GATEWAY_URL}/docs", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

@pytest.mark.skipif(not is_gateway_running(), reason="Gateway is not running")
def test_neko_session_binding():
    """
    Test that creating a session via the gateway returns a valid neko_url.
    """
    response = requests.post(f"{GATEWAY_URL}/api/sessions/")
    
    # If the endpoint doesn't exist yet or fails, we still want to assert the expected behavior
    # For the sake of this test, we'll assume a 200 or 201 is success
    assert response.status_code in (200, 201), f"Failed to create session: {response.text}"
    
    data = response.json()
    assert "id" in data, "Session ID missing from response"
    assert "neko_url" in data, "neko_url missing from response"
    
    neko_url = data["neko_url"]
    assert neko_url.startswith("http"), f"Invalid neko_url: {neko_url}"
    
    # Verify the Neko URL is reachable (or at least well-formed if Neko isn't running)
    try:
        neko_response = requests.get(neko_url, timeout=2)
        # We don't strictly assert 200 here because Neko might require auth or not be fully up,
        # but we ensure the connection doesn't completely fail if it's supposed to be up.
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Neko URL {neko_url} is unreachable: {e}")
