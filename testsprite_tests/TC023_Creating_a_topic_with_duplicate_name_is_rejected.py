import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def test_create_topic_with_duplicate_name_rejected():
    # Login as admin to get access token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token and isinstance(token, str)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create a topic with a unique name
    unique_name = f"Tema QA Duplicado {int(time.time()*1000)}"
    create_payload = {"name": unique_name, "description": "desc", "level": 1}
    create_resp = requests.post(
        f"{BASE_URL}/topics", json=create_payload, headers=headers, timeout=TIMEOUT
    )
    assert create_resp.status_code == 201, (
        f"Failed to create topic: {create_resp.status_code} {create_resp.text}"
    )
    created_topic = create_resp.json().get("topic")
    assert created_topic is not None and created_topic.get("name") == unique_name
    topic_id = created_topic.get("id")
    assert topic_id is not None

    try:
        # Attempt to create another topic with the same name (should fail with 409)
        dup_resp = requests.post(
            f"{BASE_URL}/topics", json=create_payload, headers=headers, timeout=TIMEOUT
        )
        assert dup_resp.status_code == 409, (
            f"Expected 409 on duplicate topic name, got {dup_resp.status_code}: {dup_resp.text}"
        )
        error_msg = dup_resp.json().get("error") or dup_resp.json().get("message") or ""
        assert "Ya existe un tema con ese nombre" in error_msg
    finally:
        # Clean up by deleting the created topic
        del_resp = requests.delete(
            f"{BASE_URL}/topics/{topic_id}", headers=headers, timeout=TIMEOUT
        )
        assert del_resp.status_code == 200, (
            f"Failed to delete topic after test: {del_resp.status_code} {del_resp.text}"
        )


test_create_topic_with_duplicate_name_rejected()