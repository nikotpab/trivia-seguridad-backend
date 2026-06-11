import requests

def test_login_fails_with_unknown_email():
    base_url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "noexiste@seguridaddeoro.co",
        "password": "anyPassword123!"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=30)
        assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"
        json_resp = response.json()
        # According to PRD, 401 returns "Invalid credentials" error but error message text is not fixed here.
        # Just check it has some error message or error key.
        assert ("error" in json_resp and json_resp["error"]) or ("message" in json_resp and json_resp["message"]), \
            "Response JSON should contain error or message field indicating invalid credentials."
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_login_fails_with_unknown_email()