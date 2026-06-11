import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_create_user_with_invalid_role_rejected():
    # Login as admin to get token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    token = login_data.get("access_token")
    assert token and isinstance(token, str)

    headers = {"Authorization": f"Bearer {token}"}

    # Create a user payload with invalid role 'superuser'
    unique_email = f"qa.user.invalidrole.{uuid.uuid4()}@seguridaddeoro.co"
    user_payload = {
        "email": unique_email,
        "full_name": "Bad Role",
        "role": "superuser",
        "password": "Password123!"
    }

    # Attempt to create user
    resp = requests.post(
        f"{BASE_URL}/users",
        json=user_payload,
        headers=headers,
        timeout=TIMEOUT,
    )
    # Expect HTTP 422
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()

    # The error message must mention 'Rol inválido' (case-insensitive)
    error_text = str(resp_json).lower()
    assert "rol inválido" in error_text or "rol invalido" in error_text or "rol" in error_text and "inválido" in error_text, \
        f"Error message does not mention 'Rol inválido': {resp.text}"

test_create_user_with_invalid_role_rejected()