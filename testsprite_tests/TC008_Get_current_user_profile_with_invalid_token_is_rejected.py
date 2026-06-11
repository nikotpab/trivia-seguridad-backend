import requests

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

def test_get_current_user_profile_with_invalid_token_is_rejected():
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": "Bearer not-a-real-token"
    }

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The error message must be 'Token inválido'
    error_msg = json_data.get("error") or json_data.get("message") or ""
    assert "Token inválido" in error_msg or error_msg == "Token inválido", f"Expected error message 'Token inválido', got {error_msg}"

test_get_current_user_profile_with_invalid_token_is_rejected()