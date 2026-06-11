import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_create_topic_without_name_is_rejected():
    # Authenticate as admin to get token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token and isinstance(token, str), "No access_token in login response"

    # Prepare headers with bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Attempt to create a topic without name
    topic_url = f"{BASE_URL}/topics"
    topic_payload = {"description": "x"}  # No "name" field

    resp = requests.post(topic_url, json=topic_payload, headers=headers, timeout=TIMEOUT)

    # Assert we get HTTP 422 error with expected error message
    assert resp.status_code == 422, f"Expected HTTP 422, got {resp.status_code}, response: {resp.text}"
    json_resp = resp.json()
    error_msg = (
        json_resp.get("error")
        or json_resp.get("message")
        or json_resp.get("detail")
        or ""
    ).lower()
    assert "name es obligatorio" in error_msg, f"Expected error message 'name es obligatorio', got: {json_resp}"


test_create_topic_without_name_is_rejected()