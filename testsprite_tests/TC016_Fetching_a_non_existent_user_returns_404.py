import requests

BASE_URL = "http://localhost:8000"
API_BASE_PATH = "/api/v1"
LOGIN_ENDPOINT = f"{BASE_URL}{API_BASE_PATH}/auth/login"
USER_ENDPOINT = f"{BASE_URL}{API_BASE_PATH}/users/999999"
TIMEOUT = 30

def test_fetch_non_existent_user_returns_404():
    # Step 1: Login as admin to get the token
    login_payload = {
        "email": "admin@seguridaddeoro.co",
        "password": "Password123!"
    }
    try:
        login_resp = requests.post(LOGIN_ENDPOINT, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert access_token and isinstance(access_token, str), "access_token missing or invalid"
    except Exception as e:
        assert False, f"Exception during login: {e}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Step 2: Fetch non-existent user with ID 999999
    try:
        resp = requests.get(USER_ENDPOINT, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        assert False, f"Exception during fetch user request: {e}"

    assert resp.status_code == 404, f"Expected 404 status code but got {resp.status_code}"

    try:
        resp_json = resp.json()
    except Exception as e:
        assert False, f"Response is not valid JSON: {e}"

    # Validate error message
    error_msg = resp_json.get("error") or resp_json.get("message") or ""
    assert "Usuario no encontrado" in error_msg, f"Expected error 'Usuario no encontrado' in response but got: {resp_json}"

test_fetch_non_existent_user_returns_404()