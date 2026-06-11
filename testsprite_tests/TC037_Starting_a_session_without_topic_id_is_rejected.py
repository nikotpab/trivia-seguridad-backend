import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TEST_PASSWORD = "Password123!"
TIMEOUT = 30


def test_start_session_without_topic_id_rejected():
    timestamp = int(time.time() * 1000)
    unique_email = f"g.tc037.{timestamp}@seguridaddeoro.co"

    # Admin login to create a new guarda user
    admin_login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert admin_login_resp.status_code == 200, "Admin login failed"
    admin_token = admin_login_resp.json().get("access_token")
    assert admin_token and isinstance(admin_token, str)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a new guarda user with a unique email
    create_user_resp = requests.post(
        f"{BASE_URL}/users",
        json={
            "email": unique_email,
            "full_name": "TC037 User",
            "role": "guarda",
            "password": TEST_PASSWORD,
        },
        headers=admin_headers,
        timeout=TIMEOUT,
    )
    assert create_user_resp.status_code == 201, "User creation failed"
    user_id = create_user_resp.json().get("user", {}).get("id")
    assert user_id is not None, "Created user ID not found"

    try:
        # Login as the newly created guarda user
        user_login_resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": unique_email, "password": TEST_PASSWORD},
            timeout=TIMEOUT,
        )
        assert user_login_resp.status_code == 200, "User login failed"
        user_token = user_login_resp.json().get("access_token")
        assert user_token and isinstance(user_token, str)
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Attempt to start a game session with empty body (missing topic_id)
        session_resp = requests.post(
            f"{BASE_URL}/game/sessions", json={}, headers=user_headers, timeout=TIMEOUT
        )
        assert session_resp.status_code == 422, (
            f"Expected 422 status code for missing topic_id, got {session_resp.status_code}"
        )
        resp_json = session_resp.json()
        error_msg = (
            resp_json.get("error")
            or resp_json.get("message")
            or resp_json.get("detail")
            or ""
        )
        assert "topic_id es obligatorio" in error_msg.lower(), (
            f"Expected error message about missing topic_id, got: {error_msg}"
        )
    finally:
        # Clean up: delete the created user
        requests.delete(f"{BASE_URL}/users/{user_id}", headers=admin_headers, timeout=TIMEOUT)


test_start_session_without_topic_id_rejected()