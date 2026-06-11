import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_can_logically_deactivate_question():
    # Step 1: Log in as admin to get access token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert access_token and isinstance(access_token, str), "No access_token in login response"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Admin login failed: {e}")

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Step 2: Get list of topics to get a valid topic_id
    topics_url = f"{BASE_URL}/topics"
    try:
        topics_resp = requests.get(topics_url, headers=headers, timeout=TIMEOUT)
        assert topics_resp.status_code == 200, f"Failed to get topics: {topics_resp.text}"
        topics_data = topics_resp.json()
        topics = topics_data.get("items")
        assert topics and isinstance(topics, list), "No topics found"
        # Select the first active topic
        topic_id = topics[0].get("id")
        assert isinstance(topic_id, int), "Invalid topic_id"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Failed to get topic_id: {e}")

    question_id = None
    try:
        # Step 3: Create a new question via POST /questions
        question_url = f"{BASE_URL}/questions"
        question_payload = {
            "text": "Pregunta QA para desactivar?",
            "topic_id": topic_id,
            "difficulty": "media",
            "choices": [
                {"text": "Opción 1", "is_correct": False},
                {"text": "Opción 2", "is_correct": True},
                {"text": "Opción 3", "is_correct": False},
                {"text": "Opción 4", "is_correct": False}
            ]
        }
        create_resp = requests.post(question_url, headers=headers, json=question_payload, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Question creation failed: {create_resp.text}"
        create_data = create_resp.json()
        question = create_data.get("question")
        assert question and "id" in question, "Missing question ID in response"
        question_id = question["id"]

        # Step 4: DELETE /questions/<id> to logically deactivate the question
        delete_url = f"{BASE_URL}/questions/{question_id}"
        delete_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
        assert delete_resp.status_code == 200, f"Question delete failed: {delete_resp.text}"
        delete_data = delete_resp.json()
        message = delete_data.get("message")
        assert message == "Pregunta desactivada", f"Unexpected delete message: {message}"

    finally:
        # Cleanup: Ensure the question is deleted (logical deactivate) if not already
        if question_id is not None:
            try:
                # Attempt to delete again just in case
                requests.delete(f"{BASE_URL}/questions/{question_id}", headers=headers, timeout=TIMEOUT)
            except requests.RequestException:
                pass

test_admin_can_logically_deactivate_question()