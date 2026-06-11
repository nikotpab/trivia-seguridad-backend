import requests

def test_get_current_user_profile_without_token_is_rejected():
    base_url = "http://localhost:8000/api/v1/auth/me"
    headers = {
        # No Authorization header included intentionally
    }
    try:
        response = requests.get(base_url, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The error message expected per PRD: 'Falta el token de autorización'
    error_msg = json_data.get('error') or json_data.get('message') or json_data.get('detail') or ""
    assert "Falta el token de autorización" in error_msg, f"Expected error message to include 'Falta el token de autorización', got '{error_msg}'"

test_get_current_user_profile_without_token_is_rejected()