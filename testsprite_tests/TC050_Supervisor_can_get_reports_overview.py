import requests

BASE_URL = "http://localhost:8000/api/v1"
SUPERVISOR_EMAIL = "supervisor@seguridaddeoro.co"
SUPERVISOR_PASSWORD = "Password123!"
TIMEOUT = 30

def test_supervisor_can_get_reports_overview():
    login_url = f"{BASE_URL}/auth/login"
    overview_url = f"{BASE_URL}/reports/overview"

    # Authenticate as supervisor
    login_payload = {
        "email": SUPERVISOR_EMAIL,
        "password": SUPERVISOR_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    assert login_resp.status_code == 200, f"Expected 200 on login, got {login_resp.status_code}"

    login_data = login_resp.json()
    access_token = login_data.get("access_token")
    assert access_token and isinstance(access_token, str) and access_token.strip(), "Missing or invalid access_token in login response"

    # Access reports overview with Bearer token
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        overview_resp = requests.get(overview_url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET reports overview request failed: {e}"

    assert overview_resp.status_code == 200, f"Expected 200 on GET /reports/overview, got {overview_resp.status_code}"

    overview_data = overview_resp.json()
    assert isinstance(overview_data, dict), "Overview response is not a JSON object"

test_supervisor_can_get_reports_overview()