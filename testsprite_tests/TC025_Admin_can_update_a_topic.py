import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_admin_can_update_topic():
    # Login as admin to get token
    try:
        login_resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("access_token")
        assert token and isinstance(token, str), "No access_token in login response"
        headers = {"Authorization": f"Bearer {token}"}

        # Create a new topic to update
        unique_name = f"Tema QA {int(time.time() * 1000)}"
        create_payload = {
            "name": unique_name,
            "description": "Descripción inicial",
            "level": 1
        }
        create_resp = requests.post(
            f"{BASE_URL}/topics",
            headers=headers,
            json=create_payload,
            timeout=TIMEOUT,
        )
        assert create_resp.status_code == 201, f"Topic creation failed: {create_resp.text}"
        created_topic = create_resp.json().get("topic")
        assert created_topic and "id" in created_topic, "No topic created or missing id"
        topic_id = created_topic["id"]

        # Patch the topic description to 'actualizado'
        update_payload = {
            "description": "actualizado"
        }
        update_resp = requests.patch(
            f"{BASE_URL}/topics/{topic_id}",
            headers=headers,
            json=update_payload,
            timeout=TIMEOUT,
        )
        assert update_resp.status_code == 200, f"Topic update failed: {update_resp.text}"
        updated_topic = update_resp.json().get("topic")
        assert updated_topic and updated_topic.get("description") == "actualizado", (
            "Topic description not updated as expected"
        )
    finally:
        # Clean up: delete the created topic logically
        if 'topic_id' in locals():
            # Use DELETE to logically deactivate the topic
            try:
                requests.delete(
                    f"{BASE_URL}/topics/{topic_id}",
                    headers=headers,
                    timeout=TIMEOUT,
                )
            except Exception:
                pass

test_admin_can_update_topic()