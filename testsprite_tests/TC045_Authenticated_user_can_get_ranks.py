import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
RANKS_URL = f"{BASE_URL}/ranks"
TIMEOUT = 30

def test_authenticated_user_can_get_ranks():
    email = "guarda1@seguridaddeoro.co"
    password = "Password123!"
    # Authenticate and retrieve token
    try:
        login_resp = requests.post(
            LOGIN_URL,
            json={"email": email, "password": password},
            timeout=TIMEOUT
        )
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}: {login_resp.text}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert access_token and isinstance(access_token, str), "access_token missing or not a string in login response"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Login request failed or invalid: {e}")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Call GET /api/v1/ranks with auth token
    try:
        ranks_resp = requests.get(RANKS_URL, headers=headers, timeout=TIMEOUT)
        assert ranks_resp.status_code == 200, f"Ranks request failed with status {ranks_resp.status_code}: {ranks_resp.text}"
        ranks_data = ranks_resp.json()
        # Validate presence of 'ranks' and 'me' fields
        assert "ranks" in ranks_data, "Response JSON missing 'ranks' field"
        assert isinstance(ranks_data["ranks"], (list, dict)), "'ranks' field is not a list or dict"
        assert "me" in ranks_data, "Response JSON missing 'me' field"
        assert isinstance(ranks_data["me"], dict), "'me' field is not a dict"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"GET /ranks request failed or invalid response: {e}")

test_authenticated_user_can_get_ranks()