import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
GUARDA_PASSWORD = "Password123!"


def test_tc043_using_lifeline_without_type_is_rejected():
    timestamp = int(time.time() * 1000)
    new_email = f"g.tc043.{timestamp}@seguridaddeoro.co"
    headers = {"Content-Type": "application/json"}

    # Step 1: Admin login to get token
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
        headers=headers,
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    admin_token = resp.json().get("access_token")
    assert admin_token, "Admin login missing access_token"

    admin_auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    # Step 2: Create a new guarda user with unique email
    create_user_payload = {
        "email": new_email,
        "full_name": "TC043 User",
        "role": "guarda",
        "password": GUARDA_PASSWORD,
    }
    resp = requests.post(
        f"{BASE_URL}/users",
        json=create_user_payload,
        headers=admin_auth_headers,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 201, f"Failed to create guarda user: {resp.text}"
    user_id = resp.json().get("user", {}).get("id")
    assert user_id, "Created user missing id"

    # Step 3: Log in as the new guarda user
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": new_email, "password": GUARDA_PASSWORD},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200, f"Guarda user login failed: {resp.text}"
    guarda_token = resp.json().get("access_token")
    assert guarda_token, "Guarda login missing access_token"
    guarda_auth_headers = {
        "Authorization": f"Bearer {guarda_token}",
        "Content-Type": "application/json",
    }

    # Step 4: Start a game session with topic_id 1 and num_questions (default 5)
    start_session_payload = {"topic_id": 1, "num_questions": 5}
    resp = requests.post(
        f"{BASE_URL}/game/sessions",
        json=start_session_payload,
        headers=guarda_auth_headers,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 201, f"Failed to start game session: {resp.text}"
    session = resp.json().get("session")
    assert session and "id" in session, "Session creation response missing session id"
    session_id = session["id"]

    try:
        # Step 5: Attempt to use lifeline without type in POST body
        resp = requests.post(
            f"{BASE_URL}/game/sessions/{session_id}/lifeline",
            json={},  # empty body
            headers=guarda_auth_headers,
            timeout=TIMEOUT,
        )
        assert (
            resp.status_code == 422
        ), f"Expected 422 on lifeline without type, got {resp.status_code}: {resp.text}"
        # Validate error message mentions 'type es obligatorio'
        error_msg = resp.text.lower()
        assert (
            "type" in error_msg and "obligatorio" in error_msg
        ), f"Error message does not mention 'type es obligatorio': {resp.text}"

    finally:
        # Cleanup: Delete the created user to avoid leftover data
        resp = requests.delete(
            f"{BASE_URL}/users/{user_id}",
            headers=admin_auth_headers,
            timeout=TIMEOUT,
        )
        # We allow either 200 or 404 if already deleted
        assert resp.status_code in (200, 404), f"User cleanup failed: {resp.text}"


test_tc043_using_lifeline_without_type_is_rejected()