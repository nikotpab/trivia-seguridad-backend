import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_create_user_with_duplicate_email_is_rejected():
    login_url = f"{BASE_URL}/auth/login"
    users_url = f"{BASE_URL}/users"

    # Step 1: Authenticate as admin to get JWT token
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data = login_response.json()
    token = login_data.get("access_token")
    assert token and isinstance(token, str) and len(token) > 0, "Missing access_token in login response"

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Attempt to create a user with duplicate email 'admin@seguridaddeoro.co'
    user_payload = {
        "email": "admin@seguridaddeoro.co",
        "full_name": "Dup",
        "role": "guarda",
        "password": "Password123!"
    }
    create_response = requests.post(users_url, json=user_payload, headers=headers, timeout=TIMEOUT)
    assert create_response.status_code == 409, f"Expected 409 Conflict but got {create_response.status_code}"

    resp_json = create_response.json()
    error_msg = resp_json.get("error") or resp_json.get("message") or ""
    assert "Ya existe un usuario con ese email" in error_msg, \
        f"Expected error message 'Ya existe un usuario con ese email' but got: {error_msg}"


test_create_user_with_duplicate_email_is_rejected()