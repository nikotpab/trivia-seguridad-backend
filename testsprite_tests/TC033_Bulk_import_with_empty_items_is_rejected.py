import requests

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_bulk_import_with_empty_items_is_rejected():
    # Authenticate as admin to get JWT token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    access_token = login_resp.json().get("access_token")
    assert access_token and isinstance(access_token, str), "No access_token in login response"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Attempt bulk import with empty items list
    import_url = f"{BASE_URL}/questions/import"
    import_payload = {"items": []}
    resp = requests.post(import_url, json=import_payload, headers=headers, timeout=TIMEOUT)

    # Assert the response is HTTP 422 with error 'items vacío'
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}. Response: {resp.text}"
    error_json = resp.json()
    # The error key is not specifically described, so check any message or error field contains 'items vacío'
    error_text_candidates = []
    if isinstance(error_json, dict):
        # Collect all string values to check error message presence
        def extract_strings(obj):
            strings = []
            if isinstance(obj, dict):
                for v in obj.values():
                    strings.extend(extract_strings(v))
            elif isinstance(obj, list):
                for item in obj:
                    strings.extend(extract_strings(item))
            elif isinstance(obj, str):
                strings.append(obj)
            return strings
        error_text_candidates = extract_strings(error_json)
    found_error = any("items vacío" in s for s in error_text_candidates)
    assert found_error, f"Expected error message containing 'items vacío' not found in response: {resp.text}"

test_bulk_import_with_empty_items_is_rejected()