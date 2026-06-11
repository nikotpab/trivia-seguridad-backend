import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
USER_PASSWORD = "Password123!"
TIMEOUT = 30

def test_TC044_user_can_abandon_session():
    timestamp = int(time.time() * 1000)
    new_user_email = f"g.tc044.{timestamp}@seguridaddeoro.co"
    headers = {"Content-Type": "application/json"}

    # Helper to login and return access token and user id
    def login(email, password):
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password}, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
        data = resp.json()
        token = data.get("access_token")
        user = data.get("user")
        assert token and user and user.get("id")
        return token, user.get("id")

    # Helper to create a new user as admin returns user_id
    def create_user(admin_token, email, full_name, role, password):
        resp = requests.post(f"{BASE_URL}/users",
                             headers={"Authorization": f"Bearer {admin_token}", **headers},
                             json={
                                 "email": email,
                                 "full_name": full_name,
                                 "role": role,
                                 "password": password
                             },
                             timeout=TIMEOUT)
        assert resp.status_code == 201, f"User creation failed: {resp.text}"
        user = resp.json().get("user")
        assert user and user.get("email") == email and user.get("role") == role
        return user.get("id")

    # Helper to delete user (logical deactivate)
    def delete_user(admin_token, user_id):
        resp = requests.delete(f"{BASE_URL}/users/{user_id}",
                               headers={"Authorization": f"Bearer {admin_token}", **headers},
                               timeout=TIMEOUT)
        # Accept 200 OK or 404 if already deleted
        assert resp.status_code in (200, 404)

    admin_token, _ = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    user_id = create_user(admin_token, new_user_email, "TC044 User", "guarda", USER_PASSWORD)
    try:
        user_token, _ = login(new_user_email, USER_PASSWORD)

        # Start a game session with topic_id 1 and num_questions not specified in TC044 but must start a session
        session_start_payload = {"topic_id": 1, "num_questions": 5}
        resp = requests.post(f"{BASE_URL}/game/sessions",
                             headers={"Authorization": f"Bearer {user_token}", **headers},
                             json=session_start_payload,
                             timeout=TIMEOUT)
        assert resp.status_code == 201, f"Failed to start session: {resp.text}"
        resp_json = resp.json()
        session = resp_json.get("session")
        assert session and session.get("id") and session.get("status") == "active"
        session_id = session.get("id")

        # Abandon the session
        abandon_url = f"{BASE_URL}/game/sessions/{session_id}/abandon"
        resp = requests.post(abandon_url,
                             headers={"Authorization": f"Bearer {user_token}", **headers},
                             timeout=TIMEOUT)
        assert resp.status_code == 200, f"Failed to abandon session: {resp.text}"
        final_state = resp.json()
        # Validate that final state returned and contains session id equal to abandoned one
        assert final_state and ("id" in final_state or "session" in final_state), "Invalid final state structure"
        # If wrapped under "session" key, check id matches
        if "session" in final_state:
            assert final_state["session"].get("id") == session_id
        else:
            # Direct top-level id should match session_id
            assert final_state.get("id") == session_id
    finally:
        delete_user(admin_token, user_id)

test_TC044_user_can_abandon_session()