import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc014_creating_user_with_missing_required_fields_is_rejected():
    # Login as admin to get token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert "access_token" in login_data and login_data["access_token"], "No access_token in login response"
    token = login_data["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Attempt to create user with missing email and full_name
    user_payload = {
        "role": "guarda"
    }
    resp = requests.post(
        f"{BASE_URL}/users",
        headers=headers,
        json=user_payload,
        timeout=TIMEOUT
    )
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}; response: {resp.text}"
    body = resp.json()
    error_message = ""
    # The error may be in a field, or a top-level message; we check both
    if isinstance(body, dict):
        if "error" in body and isinstance(body["error"], str):
            error_message = body["error"].lower()
        elif "message" in body and isinstance(body["message"], str):
            error_message = body["message"].lower()
        else:
            # If errors are detailed per field
            for v in body.values():
                if isinstance(v, list):
                    error_message = " ".join(map(str, v)).lower()
                    break
                elif isinstance(v, str):
                    error_message = v.lower()
                    break
    assert "email" in error_message and "full_name" in error_message or "email y full_name son obligatorios" in error_message, \
        f"Error message does not contain required fields notice: {error_message}"

test_tc014_creating_user_with_missing_required_fields_is_rejected()