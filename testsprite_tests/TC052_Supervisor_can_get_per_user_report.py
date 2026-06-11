import requests

BASE_URL = "http://localhost:8000/api/v1"
SUPERVISOR_EMAIL = "supervisor@seguridaddeoro.co"
SUPERVISOR_PASSWORD = "Password123!"
TIMEOUT = 30

def test_supervisor_can_get_per_user_report():
    # Authenticate as supervisor to get JWT token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": SUPERVISOR_EMAIL, "password": SUPERVISOR_PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}: {login_resp.text}"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert isinstance(access_token, str) and access_token, "Missing or empty access_token"
    except Exception as e:
        raise AssertionError(f"Failed to login as supervisor: {e}")

    # Use Bearer token to get per-user report
    report_users_url = f"{BASE_URL}/reports/users"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        resp = requests.get(report_users_url, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Expected 200 OK but got {resp.status_code}: {resp.text}"
        resp_json = resp.json()
        assert "items" in resp_json, "'items' field missing in response JSON"
        assert isinstance(resp_json["items"], list), f"'items' is not an array but {type(resp_json['items'])}"
    except Exception as e:
        raise AssertionError(f"Failed to get per-user report: {e}")

test_supervisor_can_get_per_user_report()