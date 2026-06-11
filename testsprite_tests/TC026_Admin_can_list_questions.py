import requests

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
LOGIN_URL = f"{BASE_URL}{API_PREFIX}/auth/login"
QUESTIONS_URL = f"{BASE_URL}{API_PREFIX}/questions"
TIMEOUT = 30

def test_admin_can_list_questions():
    # Login as admin to get token
    login_payload = {
        "email": "admin@seguridaddeoro.co",
        "password": "Password123!"
    }
    try:
        login_resp = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert isinstance(access_token, str) and access_token.strip() != "", "access_token missing or empty"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        resp = requests.get(QUESTIONS_URL, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
        resp_json = resp.json()
        assert isinstance(resp_json, dict), "Response JSON is not a dict"
        # Validate keys: items (array), total, page, pages
        assert "items" in resp_json, "Missing items in response"
        assert isinstance(resp_json["items"], list), "items is not a list"
        assert "total" in resp_json, "Missing total in response"
        assert isinstance(resp_json["total"], int), "total is not an int"
        assert "page" in resp_json, "Missing page in response"
        assert isinstance(resp_json["page"], int), "page is not an int"
        assert "pages" in resp_json, "Missing pages in response"
        assert isinstance(resp_json["pages"], int), "pages is not an int"
        # total should be >= 25 (seed creates 25 questions)
        assert resp_json["total"] >= 25, f"Expected total >= 25, got {resp_json['total']}"
    except requests.RequestException as e:
        assert False, f"GET /questions request failed: {e}"

test_admin_can_list_questions()