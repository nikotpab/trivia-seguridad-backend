import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_can_list_users_with_pagination():
    # Authenticate as admin to get JWT token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.status_code} {login_resp.text}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert access_token and isinstance(access_token, str), "Missing or invalid access_token in login response"
    except Exception as e:
        assert False, f"Exception during login request: {e}"

    # Use the token to request user list with pagination
    users_url = f"{BASE_URL}/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        users_resp = requests.get(users_url, headers=headers, timeout=TIMEOUT)
        assert users_resp.status_code == 200, f"Expected 200 OK, got {users_resp.status_code}: {users_resp.text}"
        users_data = users_resp.json()
        # Validate required fields
        assert "items" in users_data and isinstance(users_data["items"], list), "Missing or invalid 'items' array"
        assert "total" in users_data and isinstance(users_data["total"], int), "Missing or invalid 'total'"
        assert "page" in users_data and isinstance(users_data["page"], int), "Missing or invalid 'page'"
        assert "pages" in users_data and isinstance(users_data["pages"], int), "Missing or invalid 'pages'"
        # items length should be > 0 because seed creates users
        assert len(users_data["items"]) > 0, "Expected at least one user in 'items'"
    except Exception as e:
        assert False, f"Exception during GET /users request: {e}"

test_admin_can_list_users_with_pagination()