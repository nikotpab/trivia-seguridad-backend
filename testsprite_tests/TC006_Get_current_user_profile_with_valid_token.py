import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_EMAIL = "admin@seguridaddeoro.co"
LOGIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_get_current_user_profile_with_valid_token():
    login_url = f"{BASE_URL}/auth/login"
    profile_url = f"{BASE_URL}/auth/me"

    login_payload = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }

    try:
        # Log in to obtain access_token
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}: {login_resp.text}"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        assert access_token and isinstance(access_token, str) and access_token.strip(), "access_token missing or empty"
        user_info = login_json.get("user")
        assert user_info and isinstance(user_info, dict), "User info missing in login response"

        # Use access_token to get current user profile
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_resp = requests.get(profile_url, headers=headers, timeout=TIMEOUT)
        assert profile_resp.status_code == 200, f"Profile request failed with status {profile_resp.status_code}: {profile_resp.text}"
        profile_json = profile_resp.json()
        user_obj = profile_json.get("user")
        assert user_obj and isinstance(user_obj, dict), "User object missing in profile response"
        email = user_obj.get("email")
        assert email == LOGIN_EMAIL, f"Expected email '{LOGIN_EMAIL}', got '{email}'"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_get_current_user_profile_with_valid_token()