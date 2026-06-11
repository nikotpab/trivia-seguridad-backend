import requests

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

def test_login_fails_with_missing_fields():
    url = f"{BASE_URL}/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {}  # empty body, missing email and password

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The error message must include 'email y password son obligatorios' (in Spanish)
    # We accept the error message anywhere in the response JSON values.
    error_found = False
    def search_error(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                if search_error(v):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if search_error(item):
                    return True
        elif isinstance(obj, str):
            if "email y password son obligatorios" in obj:
                return True
        return False
    error_found = search_error(data)

    assert error_found, f"Response JSON does not contain expected error message 'email y password son obligatorios'. Response: {data}"

test_login_fails_with_missing_fields()