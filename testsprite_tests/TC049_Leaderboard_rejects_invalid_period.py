import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_EMAIL = "guarda1@seguridaddeoro.co"
LOGIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_leaderboard_rejects_invalid_period():
    # Authenticate as guarda1 to get access token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
        login_json = login_response.json()
        access_token = login_json.get("access_token")
        assert access_token and isinstance(access_token, str), "access_token missing or invalid"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Authentication failed: {str(e)}")

    # Make GET request to leaderboard with invalid period "year"
    leaderboard_url = f"{BASE_URL}/leaderboard"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"period": "year"}

    try:
        response = requests.get(leaderboard_url, headers=headers, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to leaderboard failed: {str(e)}")

    # Validate response code and error message
    assert response.status_code == 422, f"Expected status 422 but got {response.status_code}"
    json_resp = response.json()
    error_msg = json_resp.get("error") or json_resp.get("message") or json_resp.get("detail")
    expected_error = "period inválido: all | month | week"
    assert error_msg is not None, "Error message missing in response"
    assert expected_error in error_msg, f"Expected error message to contain '{expected_error}', got '{error_msg}'"

test_leaderboard_rejects_invalid_period()