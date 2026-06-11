import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_post_api_v1_auth_login_with_local_mode():
    url = f"{BASE_URL}/api/v1/auth/login"
    payload = {
        "email": "admin@seguridaddeoro.co",
        "password": "Password123!"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    access_token = data.get("access_token")
    user = data.get("user")

    assert isinstance(access_token, str) and access_token, "access_token missing or not a string"
    assert isinstance(user, dict), "user profile missing or not an object"
    # Validate some key fields in user profile (at least id and email)
    assert "email" in user and user["email"] == "admin@seguridaddeoro.co", "User email mismatch or missing"
    assert "id" in user, "User id missing"

test_post_api_v1_auth_login_with_local_mode()