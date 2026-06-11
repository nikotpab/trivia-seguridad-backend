import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_create_question_without_exactly_one_correct_choice_rejected():
    # Step 1: Authenticate as admin to get bearer token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("access_token")
        assert token and isinstance(token, str), "No access_token in login response"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Prepare the question payload with 4 choices and none correct
    question_url = f"{BASE_URL}/questions"
    question_payload = {
        "topic_id": 1,
        "text": "Q",
        "difficulty": "media",
        "choices": [
            {"text": "Choice 1", "is_correct": False},
            {"text": "Choice 2", "is_correct": False},
            {"text": "Choice 3", "is_correct": False},
            {"text": "Choice 4", "is_correct": False},
        ],
    }

    try:
        resp = requests.post(question_url, json=question_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Create question request failed: {e}"

    # Step 3: Assert status code 422 and error message about exactly one correct choice
    assert resp.status_code == 422, f"Unexpected status code: {resp.status_code}, response: {resp.text}"
    try:
        error_json = resp.json()
    except Exception:
        assert False, "Response is not valid JSON"

    error_message = None
    if isinstance(error_json, dict):
        # The error might be in different keys, check common ones
        if "error" in error_json and isinstance(error_json["error"], str):
            error_message = error_json["error"]
        elif "message" in error_json and isinstance(error_json["message"], str):
            error_message = error_json["message"]
        elif "detail" in error_json and isinstance(error_json["detail"], str):
            error_message = error_json["detail"]
        else:
            # check nested errors or list
            for key in error_json:
                val = error_json[key]
                if isinstance(val, list) and val:
                    if isinstance(val[0], dict) and "msg" in val[0]:
                        error_message = val[0]["msg"]
                        break
                    elif isinstance(val[0], str):
                        error_message = val[0]
                        break

    assert error_message is not None, f"No error message found in response JSON: {error_json}"
    assert "Debe haber exactamente una opción correcta" in error_message, f"Unexpected error message: {error_message}"


test_create_question_without_exactly_one_correct_choice_rejected()