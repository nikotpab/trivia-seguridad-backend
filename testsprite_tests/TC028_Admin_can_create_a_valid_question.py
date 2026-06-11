import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_can_create_valid_question():
    # Authenticate as admin and get JWT token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    access_token = login_data.get("access_token")
    assert access_token and isinstance(access_token, str) and access_token.strip() != ""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Prepare payload: topic_id 1, text "Pregunta QA?", difficulty "media", 4 choices one correct
    question_payload = {
        "topic_id": 1,
        "text": "Pregunta QA?",
        "difficulty": "media",
        "choices": [
            {"text": "Opción 1", "is_correct": False},
            {"text": "Opción 2", "is_correct": False},
            {"text": "Opción 3", "is_correct": True},
            {"text": "Opción 4", "is_correct": False},
        ],
    }

    # Create the question
    create_resp = requests.post(
        f"{BASE_URL}/questions",
        json=question_payload,
        headers=headers,
        timeout=TIMEOUT,
    )

    assert create_resp.status_code == 201, f"Create question failed: {create_resp.text}"
    create_data = create_resp.json()
    question = create_data.get("question")
    assert question is not None, "Response missing 'question' object"
    assert question.get("topic_id") == 1, "topic_id mismatch"
    assert question.get("text") == "Pregunta QA?", "text mismatch"
    assert question.get("difficulty") == "media", "difficulty mismatch"
    choices = question.get("choices")
    assert isinstance(choices, list) and len(choices) == 4, "choices must be an array of 4 elements"
    correct_choices = [c for c in choices if c.get("is_correct") is True]
    assert len(correct_choices) == 1, "There must be exactly one correct choice"

    # Cleanup: delete the created question
    question_id = question.get("id")
    if question_id:
        try:
            delete_resp = requests.delete(
                f"{BASE_URL}/questions/{question_id}",
                headers=headers,
                timeout=TIMEOUT,
            )
            assert (
                delete_resp.status_code == 200
            ), f"Failed to delete question id {question_id}: {delete_resp.text}"
        except Exception as e:
            # Log or raise if needed
            raise e

test_admin_can_create_valid_question()