import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
TOPICS_URL = f"{BASE_URL}/topics"
TIMEOUT = 30

def test_TC022_non_admin_cannot_create_topic_rbac_403():
    # Credentials for non-admin user 'guarda1@seguridaddeoro.co'
    login_payload = {
        "email": "guarda1@seguridaddeoro.co",
        "password": "Password123!"
    }
    try:
        # Authenticate and get JWT token
        login_resp = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed, status code: {login_resp.status_code}, response: {login_resp.text}"
        token = login_resp.json().get("access_token")
        assert token and isinstance(token, str), "No access_token received"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Attempt to create a topic as a non-admin
        topic_payload = {
            "name": "Tema Prohibido"
        }
        post_resp = requests.post(TOPICS_URL, json=topic_payload, headers=headers, timeout=TIMEOUT)
        
        # Assert that status code is 403 Forbidden
        assert post_resp.status_code == 403, f"Expected 403 Forbidden, got {post_resp.status_code}, response: {post_resp.text}"
        
        # Optional: check error message content
        error_json = post_resp.json()
        # The error message according to PRD likely includes something about forbidden or no permission
        assert ("error" in error_json and ("permiso" in error_json.get("error", "").lower() or "forbidden" in error_json.get("error", "").lower())) \
               or ("message" in error_json and ("permiso" in error_json.get("message", "").lower() or "forbidden" in error_json.get("message", "").lower())), \
               f"Expected error message about permissions, got: {error_json}"

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_TC022_non_admin_cannot_create_topic_rbac_403()