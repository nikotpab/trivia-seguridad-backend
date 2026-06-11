import requests

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

def test_non_admin_cannot_list_users():
    login_url = f"{BASE_URL}/auth/login"
    users_url = f"{BASE_URL}/users"
    # Credentials for guarda user (non-admin)
    login_data = {
        "email": "guarda1@seguridaddeoro.co",
        "password": "Password123!"
    }
    try:
        # Login as guarda1 to get access token
        login_resp = requests.post(login_url, json=login_data, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        login_json = login_resp.json()
        token = login_json.get("access_token")
        assert token and isinstance(token, str) and len(token) > 0, "Access token missing or empty"

        headers = {
            "Authorization": f"Bearer {token}"
        }
        # Attempt to list users with non-admin token
        users_resp = requests.get(users_url, headers=headers, timeout=TIMEOUT)
        # Should receive 403 Forbidden
        assert users_resp.status_code == 403, f"Expected 403, got {users_resp.status_code}"
        users_json = users_resp.json()
        error_msg = users_json.get("error") or users_json.get("message") or ""
        assert "No tienes permisos para esta operación" in error_msg, f"Unexpected error message: {error_msg}"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_non_admin_cannot_list_users()