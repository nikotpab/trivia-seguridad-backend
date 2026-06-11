import requests

def test_login_succeeds_with_valid_local_credentials():
    base_url = "http://localhost:8000/api/v1"
    login_url = f"{base_url}/auth/login"
    payload = {
        "email": "admin@seguridaddeoro.co",
        "password": "Password123!"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(login_url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected HTTP 200 but got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "access_token" in data, "Response JSON missing 'access_token'"
    assert isinstance(data["access_token"], str) and data["access_token"].strip() != "", "'access_token' is not a non-empty string"
    assert "user" in data, "Response JSON missing 'user'"
    user = data["user"]
    assert "id" in user, "User object missing 'id'"
    assert "email" in user, "User object missing 'email'"
    assert user["email"] == "admin@seguridaddeoro.co", f"User email expected 'admin@seguridaddeoro.co', got '{user['email']}'"

test_login_succeeds_with_valid_local_credentials()