import requests

BASE_URL = "http://localhost:8000/api/v1"
SUPERVISOR_EMAIL = "supervisor@seguridaddeoro.co"
SUPERVISOR_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc053_supervisor_user_detail_non_existent_user_404():
    # Authenticate as supervisor to get token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": SUPERVISOR_EMAIL,
        "password": SUPERVISOR_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Expected 200 but got {login_resp.status_code} on login"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert access_token and isinstance(access_token, str), "No access_token in login response"
    except Exception as e:
        assert False, f"Login request failed: {e}"

    # Perform GET on non-existent user report
    user_id = 999999
    url = f"{BASE_URL}/reports/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        assert False, f"GET /reports/users/{user_id} request failed: {e}"

    assert resp.status_code == 404, f"Expected 404 but got {resp.status_code}"
    try:
        resp_json = resp.json()
    except Exception as e:
        assert False, f"Response is not JSON: {e}"

    error_msg = resp_json.get("error") or resp_json.get("message")
    assert error_msg == "Usuario no encontrado", f"Expected error 'Usuario no encontrado' but got '{error_msg}'"

test_tc053_supervisor_user_detail_non_existent_user_404()