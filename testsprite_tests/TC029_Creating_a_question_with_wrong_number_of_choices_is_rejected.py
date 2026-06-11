import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def login_get_token(email: str, password: str) -> str:
    url = f"{BASE_URL}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("access_token", "")

def test_create_question_wrong_number_of_choices_is_rejected():
    token = login_get_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}
    # Prepare payload with only 3 choices instead of 4
    payload = {
        "topic_id": 1,
        "text": "Q",
        "difficulty": "media",
        "choices": [
            {"text": "Choice 1", "is_correct": False},
            {"text": "Choice 2", "is_correct": True},
            {"text": "Choice 3", "is_correct": False}
        ]
    }
    url = f"{BASE_URL}/questions"
    response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    json_resp = response.json()
    error_messages = []
    if isinstance(json_resp, dict):
        if "error" in json_resp and isinstance(json_resp["error"], str):
            error_messages.append(json_resp["error"])
        elif "errors" in json_resp and isinstance(json_resp["errors"], list):
            error_messages.extend(json_resp["errors"])
        elif "message" in json_resp and isinstance(json_resp["message"], str):
            error_messages.append(json_resp["message"])
    # Assert the expected Spanish error message is present
    assert any("Se requieren exactamente 4 opciones" in msg for msg in error_messages), \
        f"Expected error message about 4 options, got: {json_resp}"

test_create_question_wrong_number_of_choices_is_rejected()