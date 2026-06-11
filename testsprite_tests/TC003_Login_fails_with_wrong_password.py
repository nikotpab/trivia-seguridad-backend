import requests

base_url = "http://localhost:8000/api/v1"

def test_login_fails_wrong_password():
    url = f"{base_url}/auth/login"
    payload = {
        "email": "admin@seguridaddeoro.co",
        "password": "WrongPassword!"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    try:
        data = response.json()
    except Exception:
        assert False, "Response is not valid JSON"

    error_message = data.get("error") or data.get("message") or ""
    assert "Credenciales inválidas" in error_message, f"Expected error message containing 'Credenciales inválidas', got: {error_message}"

test_login_fails_wrong_password()