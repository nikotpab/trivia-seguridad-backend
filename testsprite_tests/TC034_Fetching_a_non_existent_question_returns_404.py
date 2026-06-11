import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_fetch_nonexistent_question_returns_404():
    # Login as admin to get Bearer token
    login_url = f"{BASE_URL}/auth/login"
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    
    try:
        login_resp = requests.post(login_url, json=login_data, timeout=TIMEOUT)
        login_resp.raise_for_status()
    except requests.RequestException as e:
        raise AssertionError(f"Login request failed: {e}")
    
    login_json = login_resp.json()
    access_token = login_json.get("access_token")
    assert access_token and isinstance(access_token, str), "No access_token in login response"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Request non-existent question
    question_id = 999999
    question_url = f"{BASE_URL}/questions/{question_id}"
    
    try:
        resp = requests.get(question_url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request for non-existent question failed: {e}")
    
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    resp_json = resp.json()
    expected_error = "Pregunta no encontrada"
    # Accept error message in a field like "error" or "message"
    error_msg = resp_json.get("error") or resp_json.get("message") or ""
    assert expected_error in error_msg, f"Expected error message '{expected_error}', got '{error_msg}'"

test_fetch_nonexistent_question_returns_404()