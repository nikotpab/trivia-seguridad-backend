import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
DEFAULT_PASSWORD = "Password123!"
TIMEOUT = 30


def login(email: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def admin_create_user(email: str, full_name: str, password: str) -> dict:
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "email": email,
        "full_name": full_name,
        "role": "guarda",
        "password": password,
    }
    resp = requests.post(f"{BASE_URL}/users", json=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["user"]


def admin_delete_user(user_id: int):
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers, timeout=TIMEOUT)
    if resp.status_code not in (200, 404):
        resp.raise_for_status()


def start_session(user_token: str, topic_id: int, num_questions: int) -> dict:
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"topic_id": topic_id, "num_questions": num_questions}
    resp = requests.post(
        f"{BASE_URL}/game/sessions", json=payload, headers=headers, timeout=TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()


def answer_without_choice_id(user_token: str, session_id: int) -> requests.Response:
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = requests.post(
        f"{BASE_URL}/game/sessions/{session_id}/answer", json={}, headers=headers, timeout=TIMEOUT
    )
    return resp


def test_answering_without_choice_id_is_rejected():
    timestamp = int(time.time() * 1000)
    user_email = f"g.tc041.{timestamp}@seguridaddeoro.co"
    user_password = DEFAULT_PASSWORD
    user_full_name = "TC041 User"

    # Create user via admin and login as that user
    user = admin_create_user(user_email, user_full_name, user_password)
    user_id = user["id"]
    try:
        user_token = login(user_email, user_password)
        # Start a session for topic_id=1 with 5 questions (num_questions arbitrary >0)
        session_resp = start_session(user_token, topic_id=1, num_questions=5)
        session_id = session_resp["session"]["id"]

        # POST to answer endpoint with empty body (no choice_id)
        resp = answer_without_choice_id(user_token, session_id)

        # Validate response HTTP 422 with correct error message
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}"
        json_data = resp.json()
        assert isinstance(json_data, dict), "Response is not a JSON object"
        error_msg = (
            json_data.get("error") or
            json_data.get("message") or
            json_data.get("detail") or
            ""
        )
        assert "choice_id es obligatorio" in error_msg, f"Expected error 'choice_id es obligatorio' in response but got: {json_data}"

    finally:
        # Clean up: delete created user to keep environment clean
        admin_delete_user(user_id)


test_answering_without_choice_id_is_rejected()