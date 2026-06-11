import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_create_question_with_nonexistent_topic_rejected():
    # Authenticate as admin
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        login_resp.raise_for_status()
    except Exception as e:
        assert False, f"Admin login failed: {e}"
    login_data = login_resp.json()
    access_token = login_data.get("access_token")
    assert access_token and isinstance(access_token, str), "No access_token returned on login"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Prepare question creation payload with non-existent topic_id 999999
    question_payload = {
        "text": "Q",
        "topic_id": 999999,
        "difficulty": "media",
        "choices": [
            {"text": "Choice 1", "is_correct": True},
            {"text": "Choice 2", "is_correct": False},
            {"text": "Choice 3", "is_correct": False},
            {"text": "Choice 4", "is_correct": False}
        ]
    }
    
    question_url = f"{BASE_URL}/questions"
    resp = requests.post(question_url, json=question_payload, headers=headers, timeout=TIMEOUT)
    
    # Validate response is HTTP 422
    assert resp.status_code == 422, f"Expected 422 status code but got {resp.status_code}"
    
    # Validate error message contains 'topic_id no existe'
    try:
        error_data = resp.json()
    except Exception:
        error_data = {}
    error_message = ""
    if isinstance(error_data, dict):
        # Error might be in a field called 'error' or in general message
        candidates = []
        if "error" in error_data:
            candidates.append(error_data["error"])
        if "message" in error_data:
            candidates.append(error_data["message"])
        # Sometimes errors can be in a list or dict of validation errors
        if "errors" in error_data:
            err = error_data["errors"]
            if isinstance(err, dict):
                for v in err.values():
                    if isinstance(v, list):
                        candidates.extend(v)
                    elif isinstance(v, str):
                        candidates.append(v)
            elif isinstance(err, list):
                candidates.extend(err)
            elif isinstance(err, str):
                candidates.append(err)
        # Flatten and join candidates for search
        error_message = " ".join(str(c) for c in candidates)
    assert "topic_id no existe" in error_message.lower(), f"Expected error message to contain 'topic_id no existe' but got: {error_message}"

test_create_question_with_nonexistent_topic_rejected()