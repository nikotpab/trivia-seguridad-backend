import requests

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "guarda1@seguridaddeoro.co"
PASSWORD = "Password123!"

def test_leaderboard_returns_results_for_period_all():
    try:
        # Login to get access token
        login_resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": EMAIL, "password": PASSWORD},
            timeout=30,
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_json = login_resp.json()
        token = login_json.get("access_token")
        assert token and isinstance(token, str) and len(token) > 0, "No access_token found"
        
        headers = {"Authorization": f"Bearer {token}"}

        # GET /leaderboard?period=all
        leaderboard_resp = requests.get(
            f"{BASE_URL}/leaderboard",
            headers=headers,
            params={"period": "all"},
            timeout=30,
        )
        assert leaderboard_resp.status_code == 200, f"Leaderboard request failed: {leaderboard_resp.text}"
        data = leaderboard_resp.json()
        assert "items" in data, "'items' not in response"
        assert isinstance(data["items"], list), "'items' is not an array"
        assert "period" in data, "'period' field missing from response"
        assert data["period"] == "all", f"Expected period 'all', got '{data['period']}'"
    except requests.RequestException as e:
        assert False, f"Request exception: {e}"

test_leaderboard_returns_results_for_period_all()