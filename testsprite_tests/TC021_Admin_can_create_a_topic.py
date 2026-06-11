import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_tc021_admin_can_create_topic():
    # Login as admin to get access_token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        token = login_data.get("access_token")
        assert token and isinstance(token, str) and len(token) > 0, "No access_token received"
    except requests.RequestException as e:
        assert False, f"Login request exception: {e}"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create unique topic name using timestamp
    timestamp = int(time.time() * 1000)
    topic_name = f"Tema QA {timestamp}"
    topic_payload = {
        "name": topic_name,
        "description": "desc",
        "level": 1
    }

    topic_url = f"{BASE_URL}/topics"
    created_topic_id = None

    try:
        create_resp = requests.post(topic_url, json=topic_payload, headers=headers, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Topic creation failed: {create_resp.text}"
        create_data = create_resp.json()
        topic = create_data.get("topic")
        assert topic is not None, "Response missing 'topic' object"
        created_topic_id = topic.get("id")
        created_topic_name = topic.get("name")
        assert created_topic_name == topic_name, f"Created topic name mismatch: expected '{topic_name}', got '{created_topic_name}'"

    except requests.RequestException as e:
        assert False, f"Topic creation request exception: {e}"

    finally:
        # Cleanup: delete the created topic if created_topic_id is available
        if created_topic_id is not None:
            try:
                delete_url = f"{BASE_URL}/topics/{created_topic_id}"
                del_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Accept 200 OK (successful logical delete) or 404 if already deleted/not found
                assert del_resp.status_code in (200, 404), f"Topic deletion failed with status {del_resp.status_code}: {del_resp.text}"
            except requests.RequestException:
                pass


test_tc021_admin_can_create_topic()