import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
LEADERBOARD_URL = f"{BASE_URL}/leaderboard"
USER_EMAIL = "guarda1@seguridaddeoro.co"
USER_PASSWORD = "Password123!"
TIMEOUT = 30

def test_leaderboard_returns_results_for_period_week():
    # Step 1: Authenticate as guarda1 and get access token
    login_payload = {
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    }
    try:
        login_resp = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert isinstance(access_token, str) and access_token, "access_token missing or empty in login response"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Step 2: Call GET /leaderboard?period=week
    params = {"period": "week"}
    try:
        resp = requests.get(LEADERBOARD_URL, headers=headers, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Leaderboard request failed: {e}"

    assert resp.status_code == 200, f"Expected status 200 but got {resp.status_code} with body {resp.text}"
    try:
        data = resp.json()
    except Exception as e:
        assert False, f"Response JSON decode failed: {e}"

    # Assert response keys and values
    assert "items" in data, "Response JSON missing 'items' key"
    assert isinstance(data["items"], list), "'items' is not a list"
    assert data.get("period") == "week", f"Response 'period' value is not 'week' but {data.get('period')}"

test_leaderboard_returns_results_for_period_week()