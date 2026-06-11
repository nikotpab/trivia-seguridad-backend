import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc018_admin_can_logically_deactivate_user():
    # Authenticate as admin to get access token
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    login_data = login_resp.json()
    token = login_data.get("access_token")
    assert token and isinstance(token, str) and len(token) > 0, "No access_token in login response"
    headers = {"Authorization": f"Bearer {token}"}

    # Create a fresh user with unique email using current timestamp
    timestamp = int(time.time() * 1000)
    new_user_email = f"qa.user.tc018.{timestamp}@seguridaddeoro.co"
    create_payload = {
        "email": new_user_email,
        "full_name": "QA User TC018",
        "role": "guarda",
        "password": "Password123!"
    }
    create_resp = requests.post(f"{BASE_URL}/users", json=create_payload, headers=headers, timeout=TIMEOUT)
    assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
    created_user = create_resp.json().get("user")
    assert created_user is not None, "No user object in creation response"
    user_id = created_user.get("id")
    assert user_id is not None, "Created user has no id"

    try:
        # Delete (logical deactivate) the newly created user
        delete_resp = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
        assert delete_resp.status_code == 200, f"User delete failed: {delete_resp.text}"
        delete_data = delete_resp.json()
        message = delete_data.get("message")
        assert message == "Usuario desactivado", f"Unexpected delete message: {message}"
        user_after_delete = delete_data.get("user")
        assert user_after_delete is not None, "No user object in delete response"
        is_active = user_after_delete.get("is_active")
        assert is_active is False or is_active == False, f"user is_active should be false, got: {is_active}"
    finally:
        # Cleanup: ensure user is deleted if still active
        try:
            get_resp = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
            if get_resp.status_code == 200:
                user_data = get_resp.json().get("user")
                if user_data and user_data.get("is_active", True):
                    requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
        except Exception:
            pass

test_tc018_admin_can_logically_deactivate_user()