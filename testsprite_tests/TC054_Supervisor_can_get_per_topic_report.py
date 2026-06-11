import requests

BASE_URL = "http://localhost:8000/api/v1"
SUPERVISOR_EMAIL = "supervisor@seguridaddeoro.co"
SUPERVISOR_PASSWORD = "Password123!"
TIMEOUT = 30

def test_supervisor_can_get_per_topic_report():
    login_url = f"{BASE_URL}/auth/login"
    reports_topics_url = f"{BASE_URL}/reports/topics"

    # Authenticate as supervisor to get token
    login_payload = {
        "email": SUPERVISOR_EMAIL,
        "password": SUPERVISOR_PASSWORD
    }
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"
    assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
    login_json = login_response.json()
    access_token = login_json.get("access_token")
    assert access_token and isinstance(access_token, str), "No access_token in login response"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # GET /reports/topics
    try:
        response = requests.get(reports_topics_url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET /reports/topics request failed: {e}"
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "items" in json_data, "'items' field missing in response"
    assert isinstance(json_data["items"], list), "'items' field is not a list"

test_supervisor_can_get_per_topic_report()