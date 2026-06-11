import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
TOPICS_URL = f"{BASE_URL}/topics"
LOGIN_EMAIL = "guarda1@seguridaddeoro.co"
LOGIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_authenticated_user_can_list_topics():
    # Step 1: Log in to get access_token
    login_payload = {"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    try:
        login_response = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"
        login_data = login_response.json()
        access_token = login_data.get("access_token")
        assert isinstance(access_token, str) and access_token.strip(), "access_token missing or empty"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: GET /topics with authentication
    try:
        topics_response = requests.get(TOPICS_URL, headers=headers, timeout=TIMEOUT)
        assert topics_response.status_code == 200, f"GET /topics returned {topics_response.status_code}"
        topics_data = topics_response.json()
        assert "items" in topics_data, "'items' field missing in response"
        items = topics_data["items"]
        assert isinstance(items, list), "'items' is not a list"
        assert len(items) > 0, "Expected at least one topic in items"
    except requests.RequestException as e:
        assert False, f"GET /topics request failed: {e}"


test_authenticated_user_can_list_topics()