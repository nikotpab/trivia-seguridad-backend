import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
USER_PASSWORD = "Password123!"
HEADERS_JSON = {"Content-Type": "application/json"}
TIMEOUT = 30

def login(email: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        headers=HEADERS_JSON,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    assert token, "No access_token in login response"
    return token

def create_user(admin_token: str, email: str, full_name: str = None, role: str = "guarda", password: str = USER_PASSWORD):
    body = {
        "email": email,
        "full_name": full_name or email.split("@")[0],
        "role": role,
        "password": password,
    }
    resp = requests.post(
        f"{BASE_URL}/users",
        json=body,
        headers={"Authorization": f"Bearer {admin_token}", **HEADERS_JSON},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    user = data.get("user")
    assert user and user.get("id"), "User creation response missing user or id"
    return user

def start_session(token: str, topic_id: int = 1, num_questions: int = 5):
    body = {"topic_id": topic_id, "num_questions": num_questions}
    resp = requests.post(
        f"{BASE_URL}/game/sessions",
        json=body,
        headers={"Authorization": f"Bearer {token}", **HEADERS_JSON},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    # Expecting a session state with session id possibly under 'id' or 'session' key
    session_id = data.get("id")
    if not session_id and isinstance(data, dict):
        # Try find 'session' key with id inside
        session = data.get("session")
        if session and isinstance(session, dict):
            session_id = session.get("id")
    assert session_id, f"Session creation response missing session id, response: {data}"
    return session_id

def delete_user(admin_token: str, user_id: int):
    resp = requests.delete(
        f"{BASE_URL}/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=TIMEOUT,
    )
    # Accept 200 OK or 404 Not Found (already deleted)
    if resp.status_code not in (200, 404):
        resp.raise_for_status()

def test_TC039_user_cannot_access_another_users_session_rbac_403():
    timestamp = int(time.time() * 1000)
    email_a = f"g.tc039a.{timestamp}@seguridaddeoro.co"
    email_b = f"g.tc039b.{timestamp}@seguridaddeoro.co"

    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    user_a = create_user(admin_token, email_a)
    user_b = create_user(admin_token, email_b)

    token_a = login(email_a, USER_PASSWORD)
    token_b = login(email_b, USER_PASSWORD)

    session_id = None

    try:
        session_id = start_session(token_a, topic_id=1, num_questions=5)

        # User B tries to access User A's session - must be 403 Forbidden
        resp = requests.get(
            f"{BASE_URL}/game/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token_b}"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}, body: {resp.text}"

    finally:
        # Cleanup users
        delete_user(admin_token, user_a["id"])
        delete_user(admin_token, user_b["id"])


test_TC039_user_cannot_access_another_users_session_rbac_403()
