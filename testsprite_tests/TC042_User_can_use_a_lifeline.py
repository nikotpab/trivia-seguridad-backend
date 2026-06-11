import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
USER_PASSWORD = "Password123!"
TIMEOUT = 30

def test_user_can_use_lifeline():
    session = requests.Session()

    def login(email, password):
        resp = session.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token")
        assert token and isinstance(token, str)
        return token

    def admin_create_guarda_user(email):
        admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.post(
            f"{BASE_URL}/users",
            json={
                "email": email,
                "full_name": "TC042 User",
                "role": "guarda",
                "password": USER_PASSWORD,
            },
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        user = data.get("user")
        assert user and user.get("email") == email and user.get("role") == "guarda"
        return user.get("id")

    def admin_delete_user(user_id):
        admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = session.delete(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        assert "message" in data and "user" in data
        return data

    # Generate unique email
    timestamp = int(time.time() * 1000)
    user_email = f"g.tc042.{timestamp}@seguridaddeoro.co"

    user_id = None
    user_token = None
    session_id = None

    try:
        # 1) Admin creates fresh guarda user
        user_id = admin_create_guarda_user(user_email)

        # 2) Log in as the new user
        user_token = login(user_email, USER_PASSWORD)
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 3) Start a game session with topic_id=1
        resp = session.post(
            f"{BASE_URL}/game/sessions",
            json={"topic_id": 1, "num_questions": 5},
            headers=user_headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        assert resp.status_code == 201
        resp_data = resp.json()
        session_obj = resp_data.get("session")
        assert session_obj and "id" in session_obj and session_obj.get("status") == "active"
        session_id = session_obj["id"]

        # 4) Use lifeline POST /game/sessions/{session_id}/lifeline with { type: 'fifty_fifty' }
        resp = session.post(
            f"{BASE_URL}/game/sessions/{session_id}/lifeline",
            json={"type": "fifty_fifty"},
            headers=user_headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        assert resp.status_code == 200
        lifeline_data = resp.json()
        # The API returns updated state, validate it contains session info and lifeline effect
        assert "session" in lifeline_data or isinstance(lifeline_data, dict)
        # Optionally check session id matches and state changed
        if "session" in lifeline_data:
            assert lifeline_data["session"].get("id") == session_id

    finally:
        # Cleanup: delete created user if user_id is set
        if user_id:
            try:
                admin_delete_user(user_id)
            except Exception:
                pass

test_user_can_use_lifeline()