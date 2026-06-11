import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
DEFAULT_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc036_user_can_start_game_session():
    # Step 1: Log in as admin
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    admin_token = login_resp.json().get("access_token")
    assert admin_token, "Admin access_token missing"

    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # Step 1: Create a new guarda user with unique email
    timestamp = int(time.time() * 1000)
    new_user_email = f"g.tc036.{timestamp}@seguridaddeoro.co"
    user_payload = {
        "email": new_user_email,
        "full_name": "TC036",
        "role": "guarda",
        "password": DEFAULT_PASSWORD,
    }

    create_resp = requests.post(
        f"{BASE_URL}/users",
        json=user_payload,
        headers=headers_admin,
        timeout=TIMEOUT,
    )
    assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
    user_data = create_resp.json().get("user")
    assert user_data is not None, "User object missing in creation response"
    user_id = user_data.get("id")
    assert user_id is not None, "Created user id missing"

    try:
        # Step 2: Log in as the new user
        login_new_resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": new_user_email, "password": DEFAULT_PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_new_resp.status_code == 200, f"New user login failed: {login_new_resp.text}"
        new_user_token = login_new_resp.json().get("access_token")
        assert new_user_token, "New user access_token missing"
        headers_new_user = {"Authorization": f"Bearer {new_user_token}"}

        # Step 3: Start a game session with topic_id 1, num_questions 5
        session_payload = {"topic_id": 1, "num_questions": 5}
        start_resp = requests.post(
            f"{BASE_URL}/game/sessions",
            json=session_payload,
            headers=headers_new_user,
            timeout=TIMEOUT,
        )

        assert start_resp.status_code == 201, f"Starting game session failed: {start_resp.text}"
        resp_json = start_resp.json()

        # Assert top-level keys 'session' and 'question' present
        assert "session" in resp_json, "'session' key missing in response"
        assert "question" in resp_json, "'question' key missing in response"

        session = resp_json["session"]
        question = resp_json["question"]

        # Assert session.id exists
        session_id = session.get("id")
        assert session_id is not None, "Session id missing"
        # Assert session.status is 'active'
        assert session.get("status") == "active", f"Expected session.status 'active', got {session.get('status')}"
        # Assert session.total_questions equals 5
        assert session.get("total_questions") == 5, f"Expected total_questions 5, got {session.get('total_questions')}"

        # Assert question has 'id'
        question_id = question.get("id")
        assert question_id is not None, "Question id missing"
        # Assert question.choices is a non-empty list
        choices = question.get("choices")
        assert isinstance(choices, list), "'choices' should be a list"
        assert len(choices) > 0, "'choices' list is empty"

    finally:
        # Clean up: delete the created user
        del_resp = requests.delete(
            f"{BASE_URL}/users/{user_id}",
            headers=headers_admin,
            timeout=TIMEOUT,
        )
        # Allow user deactivation or 404 if already deleted
        assert del_resp.status_code in (200, 404), f"Failed to delete user: {del_resp.text}"

test_tc036_user_can_start_game_session()