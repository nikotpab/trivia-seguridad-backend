import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc011_admin_can_create_new_user():
    # Login as admin to get access token
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}, response: {login_resp.text}"
    login_json = login_resp.json()
    assert "access_token" in login_json and isinstance(login_json["access_token"], str) and login_json["access_token"], "No access_token returned"
    token = login_json["access_token"]

    # Prepare unique email
    timestamp = int(time.time() * 1000)
    email = f"qa.user.{timestamp}@seguridaddeoro.co"
    user_payload = {
        "email": email,
        "full_name": "QA User",
        "role": "guarda",
        "password": "Password123!"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    user_created = None
    try:
        # Create new user
        resp = requests.post(f"{BASE_URL}/users", json=user_payload, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 201, f"User creation failed with status {resp.status_code}, response: {resp.text}"
        resp_json = resp.json()
        assert "user" in resp_json and isinstance(resp_json["user"], dict), "Response missing user object"
        user = resp_json["user"]
        assert user.get("email") == email, f"Created user email mismatch. Expected {email}, got {user.get('email')}"
        assert user.get("role") == "guarda", f"Created user role mismatch. Expected 'guarda', got {user.get('role')}"
        user_created = user
    finally:
        # Cleanup: delete created user if it was created
        if user_created and "id" in user_created:
            user_id = user_created["id"]
            del_resp = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
            # Accept 200 OK or not found if already deleted
            assert del_resp.status_code in (200, 404), f"Failed to delete user during cleanup. Status: {del_resp.status_code}, Response: {del_resp.text}"

test_tc011_admin_can_create_new_user()