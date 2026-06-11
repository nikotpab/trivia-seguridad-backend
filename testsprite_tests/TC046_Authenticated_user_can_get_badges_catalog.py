import requests

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30

def test_authenticated_user_can_get_badges_catalog():
    login_url = f"{BASE_URL}/auth/login"
    badges_url = f"{BASE_URL}/badges"
    credentials = {
        "email": "guarda1@seguridaddeoro.co",
        "password": "Password123!"
    }
    try:
        # Authenticate to get access token
        login_resp = requests.post(login_url, json=credentials, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed, status code: {login_resp.status_code}"
        login_data = login_resp.json()
        assert "access_token" in login_data and isinstance(login_data["access_token"], str) and login_data["access_token"], "No valid access_token found"

        token = login_data["access_token"]
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Request badges catalog
        badges_resp = requests.get(badges_url, headers=headers, timeout=TIMEOUT)
        assert badges_resp.status_code == 200, f"Badges request failed, status code: {badges_resp.status_code}"
        badges_data = badges_resp.json()
        assert "items" in badges_data and isinstance(badges_data["items"], list), "Response 'items' field missing or not a list"
        # Seed creates 6 badges
        assert len(badges_data["items"]) == 6, f"Expected 6 badges, got {len(badges_data['items'])}"
        for badge in badges_data["items"]:
            assert isinstance(badge, dict), "Each badge item must be a dictionary"
            assert "unlocked" in badge, "Badge item missing 'unlocked' field"
            assert isinstance(badge["unlocked"], bool), "'unlocked' field must be boolean"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_authenticated_user_can_get_badges_catalog()