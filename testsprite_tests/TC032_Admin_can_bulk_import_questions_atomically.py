import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30


def login(email: str, password: str) -> str:
    url = f"{BASE_URL}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    assert token and isinstance(token, str) and len(token) > 0
    return token


def test_admin_can_bulk_import_questions_atomically():
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # Prepare two valid question payloads with topic_id=1, text, difficulty 'media', 4 choices one correct
    timestamp = int(time.time() * 1000)

    question1 = {
        "text": f"Pregunta QA bulk import 1 - {timestamp}",
        "topic_id": 1,
        "difficulty": "media",
        "choices": [
            {"text": "Opción 1", "is_correct": False},
            {"text": "Opción 2", "is_correct": True},
            {"text": "Opción 3", "is_correct": False},
            {"text": "Opción 4", "is_correct": False}
        ]
    }

    question2 = {
        "text": f"Pregunta QA bulk import 2 - {timestamp}",
        "topic_id": 1,
        "difficulty": "media",
        "choices": [
            {"text": "Opción A", "is_correct": False},
            {"text": "Opción B", "is_correct": False},
            {"text": "Opción C", "is_correct": True},
            {"text": "Opción D", "is_correct": False}
        ]
    }

    payload = {"items": [question1, question2]}

    url = f"{BASE_URL}/questions/import"
    response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # If HTTP error, try to show response body for debug
        content = response.content.decode("utf-8", errors="replace")
        raise AssertionError(f"POST /questions/import failed with {response.status_code}: {content}") from e

    assert response.status_code == 201, f"Expected HTTP 201, got {response.status_code}"
    data = response.json()
    created = data.get("created")
    assert created == 2, f"Expected created=2, got {created}"


test_admin_can_bulk_import_questions_atomically()