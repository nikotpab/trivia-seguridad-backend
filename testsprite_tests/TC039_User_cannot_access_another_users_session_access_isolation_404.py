import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TEST_PASSWORD = "Password123!"
TIMEOUT = 30

def login(email: str, password: str) -> str:
    url = f"{BASE_URL}/auth/login"
    payload = {"email": email, "password": password}
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    assert "access_token" in data and isinstance(data["access_token"], str) and data["access_token"]
    return data["access_token"]

def create_user(admin_token: str, email: str, full_name: str = None, role: str = "guarda", password: str = TEST_PASSWORD) -> int:
    url = f"{BASE_URL}/users"
    headers = {"Authorization": f"Bearer {admin_token}"}
    if full_name is None:
        full_name = "TC039 User"
    payload = {
        "email": email,
        "full_name": full_name,
        "role": role,
        "password": password
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    assert "user" in data and "id" in data["user"]
    return data["user"]["id"]

def start_session(user_token: str, topic_id: int = 1, num_questions: int = 5) -> dict:
    url = f"{BASE_URL}/game/sessions"
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"topic_id": topic_id, "num_questions": num_questions}
    resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    assert "session" in data and "id" in data["session"]
    return data

def delete_user(admin_token: str, user_id: int):
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
    # Accept 200 or 404 if already deleted
    if resp.status_code not in (200, 404):
        resp.raise_for_status()

def test_user_cannot_access_another_users_session_TC039():
    timestamp = int(time.time() * 1000)
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    email_a = f"g.tc039a.{timestamp}@seguridaddeoro.co"
    email_b = f"g.tc039b.{timestamp}@seguridaddeoro.co"

    user_a_id = None
    user_b_id = None

    try:
        # Create user A and B
        user_a_id = create_user(admin_token, email_a)
        user_b_id = create_user(admin_token, email_b)

        # Log in as user A and start a session
        token_a = login(email_a, TEST_PASSWORD)
        session_resp = start_session(token_a, topic_id=1, num_questions=5)
        session_id = session_resp["session"]["id"]

        # Log in as user B
        token_b = login(email_b, TEST_PASSWORD)

        # User B tries to access User A's session
        url = f"{BASE_URL}/game/sessions/{session_id}"
        headers = {"Authorization": f"Bearer {token_b}"}
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)

        # Assert 404 status code with expected error message 'Partida no encontrada'
        assert resp.status_code == 404
        error_json = resp.json()
        # The error message may be in a key like 'error' or 'message'
        error_messages = []
        if isinstance(error_json, dict):
            for v in error_json.values():
                if isinstance(v, str):
                    error_messages.append(v.lower())
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            error_messages.append(item.lower())
        combined_errors = " ".join(error_messages)
        assert "partida no encontrada" in combined_errors

    finally:
        # Clean up users
        if user_a_id:
            try:
                delete_user(admin_token, user_a_id)
            except Exception:
                pass
        if user_b_id:
            try:
                delete_user(admin_token, user_b_id)
            except Exception:
                pass

test_user_cannot_access_another_users_session_TC039()