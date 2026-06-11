import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_cannot_deactivate_own_account():
    # Step 1: Log in as admin to get token and user id
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}: {login_resp.text}"
    login_data = login_resp.json()
    access_token = login_data.get("access_token")
    user = login_data.get("user")
    assert access_token and isinstance(access_token, str) and len(access_token) > 0, "Missing or invalid access_token"
    assert user and isinstance(user, dict) and "id" in user, "Missing user id in login response"
    own_id = user["id"]

    # Step 2: Attempt to delete own user account
    delete_url = f"{BASE_URL}/users/{own_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    delete_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)

    # Expected: HTTP 422 with error message 'No puedes desactivar tu propia cuenta'
    assert delete_resp.status_code == 422, f"Expected 422 but got {delete_resp.status_code}: {delete_resp.text}"
    try:
        resp_json = delete_resp.json()
    except Exception:
        resp_json = {}
    error_msg = resp_json.get("error") or resp_json.get("message") or ""
    assert "No puedes desactivar tu propia cuenta" in error_msg, f"Expected error message not found, got: {error_msg}"

test_admin_cannot_deactivate_own_account()