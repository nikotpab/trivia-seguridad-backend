import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
REQUEST_TIMEOUT = 30


def test_TC040_user_can_submit_answer_in_session():
    session = requests.Session()

    def admin_login():
        resp = session.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token")
        assert token and isinstance(token, str)
        return token

    def admin_create_user(admin_token, email, password):
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_payload = {
            "email": email,
            "full_name": "TC040 User",
            "role": "guarda",
            "password": password,
        }
        resp = session.post(
            f"{BASE_URL}/users", json=new_user_payload, headers=headers, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        assert resp.status_code == 201
        user = data.get("user")
        assert user and user.get("email") == email and user.get("role") == "guarda"
        return user

    def user_login(email, password):
        resp = session.post(
            f"{BASE_URL}/auth/login", json={"email": email, "password": password}, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("access_token")
        assert token and isinstance(token, str)
        return token

    def start_session(user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        payload = {"topic_id": 1, "num_questions": 5}
        resp = session.post(
            f"{BASE_URL}/game/sessions", json=payload, headers=headers, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        assert resp.status_code == 201
        assert "session" in data and "id" in data["session"]
        assert "question" in data and "choices" in data["question"]
        assert isinstance(data["question"]["choices"], list) and len(data["question"]["choices"]) > 0
        return data["session"]["id"], data["question"]["choices"][0]["id"]

    def submit_answer(user_token, session_id, choice_id):
        headers = {"Authorization": f"Bearer {user_token}"}
        payload = {"choice_id": choice_id}
        resp = session.post(
            f"{BASE_URL}/game/sessions/{session_id}/answer",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        assert resp.status_code == 200
        assert "result" in data
        result = data["result"]
        assert isinstance(result.get("is_correct"), bool)
        assert isinstance(result.get("points_awarded"), (int, float))

    # Begin test flow:
    timestamp = int(time.time() * 1000)
    new_email = f"g.tc040.{timestamp}@seguridaddeoro.co"
    new_password = "Password123!"
    admin_token = admin_login()

    user = None
    user_token = None
    session_id = None

    try:
        user = admin_create_user(admin_token, new_email, new_password)
        user_token = user_login(new_email, new_password)
        session_id, choice_id = start_session(user_token)
        submit_answer(user_token, session_id, choice_id)
    finally:
        if user and "id" in user:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                resp = session.delete(
                    f"{BASE_URL}/users/{user['id']}", headers=headers, timeout=REQUEST_TIMEOUT
                )
                # Deletion might logically deactivate user, no assertion on status code to avoid masking main test.
            except Exception:
                pass


test_TC040_user_can_submit_answer_in_session()