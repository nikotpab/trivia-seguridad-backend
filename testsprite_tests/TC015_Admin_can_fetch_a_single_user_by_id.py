import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_can_fetch_single_user_by_id():
    # Log in as admin to get access token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert access_token and isinstance(access_token, str), "No access_token in login response"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Failed to authenticate admin user: {e}")

    # Fetch user with id 1 using admin token
    user_url = f"{BASE_URL}/users/1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        user_resp = requests.get(user_url, headers=headers, timeout=TIMEOUT)
        assert user_resp.status_code == 200, f"Expected 200 OK but got {user_resp.status_code}"
        user_data = user_resp.json()
        user = user_data.get("user")
        assert isinstance(user, dict), "Response JSON missing 'user' object"
        assert user.get("id") == 1, f"User id expected to be 1 but got {user.get('id')}"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Failed to fetch user by id: {e}")

test_admin_can_fetch_single_user_by_id()