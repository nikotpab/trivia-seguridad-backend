import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
PASSWORD = "Password123!"

def test_TC038_user_can_fetch_own_session_state():
    timeout = 30
    timestamp = int(time.time() * 1000)
    user_email = f"g.tc038.{timestamp}@seguridaddeoro.co"
    headers = {"Content-Type": "application/json"}

    # Helper function to login and get token
    def login(email, password):
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=timeout,
        )
        assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
        data = resp.json()
        token = data.get("access_token")
        assert token and isinstance(token, str), "No access_token in login response"
        return token

    # Helper function to create a user as admin
    def admin_create_user(admin_token, email, password):
        resp = requests.post(
            f"{BASE_URL}/users",
            json={
                "email": email,
                "full_name": "TC038 Test User",
                "role": "guarda",
                "password": password,
            },
            headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
            timeout=timeout,
        )
        assert resp.status_code == 201, f"User creation failed: {resp.status_code} {resp.text}"
        data = resp.json()
        user = data.get("user")
        assert user and user.get("email") == email, "Created user email mismatch"
        return user

    # Login as admin
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    # Create new guarda user for the test
    user = admin_create_user(admin_token, user_email, PASSWORD)

    # Login as the new user
    user_token = login(user_email, PASSWORD)

    # Start a session for topic_id=1, num_questions=5
    start_session_resp = requests.post(
        f"{BASE_URL}/game/sessions",
        json={"topic_id": 1, "num_questions": 5},
        headers={"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"},
        timeout=timeout,
    )
    assert start_session_resp.status_code == 201, f"Failed to start session: {start_session_resp.status_code} {start_session_resp.text}"
    start_session_data = start_session_resp.json()
    session = start_session_data.get("session")
    assert session and "id" in session, "No session id in start session response"
    session_id = session["id"]

    try:
        # Fetch the session state with the user's token
        get_session_resp = requests.get(
            f"{BASE_URL}/game/sessions/{session_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=timeout,
        )
        assert get_session_resp.status_code == 200, f"Fetching session failed: {get_session_resp.status_code} {get_session_resp.text}"
        get_session_data = get_session_resp.json()
        fetched_session = get_session_data.get("session")
        assert fetched_session, "No 'session' object in GET session response"
        assert fetched_session.get("id") == session_id, "Fetched session id does not match started session id"

    finally:
        # Cleanup: delete the user created (logical deactivation)
        requests.delete(
            f"{BASE_URL}/users/{user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=timeout,
        )

test_TC038_user_can_fetch_own_session_state()