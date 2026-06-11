import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_ENDPOINT = f"{BASE_URL}/auth/login"
REPORT_OVERVIEW_ENDPOINT = f"{BASE_URL}/reports/overview"
LOGIN_EMAIL = "guarda1@seguridaddeoro.co"
LOGIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_guarda_cannot_access_supervisor_reports_rbac_403():
    # Authenticate as guarda user to get JWT token
    login_payload = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    try:
        login_resp = requests.post(LOGIN_ENDPOINT, json=login_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"
    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
    login_json = login_resp.json()
    access_token = login_json.get("access_token")
    assert isinstance(access_token, str) and access_token != "", "Access token missing or empty after login"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Attempt to access supervisor reports overview endpoint
    try:
        response = requests.get(REPORT_OVERVIEW_ENDPOINT, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET reports overview request failed: {e}"

    # Validate that access is forbidden with 403 status code
    assert response.status_code == 403, f"Expected 403 Forbidden but got {response.status_code}"
    # Optionally validate error message in response JSON if present
    try:
        resp_json = response.json()
        error_msg = resp_json.get("error") or resp_json.get("message") or ""
        assert any(keyword in error_msg.lower() for keyword in ["no tienes permisos", "forbidden", "403"]), "Expected error message about permission denied"
    except Exception:
        # Response may not be JSON, skip message assert if so
        pass


test_guarda_cannot_access_supervisor_reports_rbac_403()