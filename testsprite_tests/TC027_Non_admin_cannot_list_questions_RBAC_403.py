import requests

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

def test_tc027_non_admin_cannot_list_questions():
    login_url = f"{BASE_URL}/auth/login"
    questions_url = f"{BASE_URL}/questions"

    # Credentials for non-admin user
    email = "guarda1@seguridaddeoro.co"
    password = "Password123!"

    # Step 1: Login as guarda1 (non-admin) to get token
    login_payload = {"email": email, "password": password}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"
    assert login_resp.status_code == 200, f"Expected 200 on login, got {login_resp.status_code}"
    login_json = login_resp.json()
    access_token = login_json.get("access_token")
    assert access_token and isinstance(access_token, str), "access_token missing or invalid in login response"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Step 2: Attempt to GET /questions as non-admin
    try:
        questions_resp = requests.get(questions_url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Questions GET request failed: {e}"

    # Expect HTTP 403 Forbidden
    assert questions_resp.status_code == 403, f"Expected 403 Forbidden, got {questions_resp.status_code}"

test_tc027_non_admin_cannot_list_questions()