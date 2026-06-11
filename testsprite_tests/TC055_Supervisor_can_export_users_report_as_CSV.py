import requests

BASE_URL = "http://localhost:8000/api/v1"
SUPERVISOR_EMAIL = "supervisor@seguridaddeoro.co"
SUPERVISOR_PASSWORD = "Password123!"
TIMEOUT = 30

def test_supervisor_can_export_users_report_as_csv():
    # Authenticate as supervisor to obtain JWT token
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": SUPERVISOR_EMAIL,
        "password": SUPERVISOR_PASSWORD
    }
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: HTTP {login_resp.status_code} - {login_resp.text}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        assert isinstance(access_token, str) and access_token, "access_token missing or empty in login response"
    except requests.RequestException as e:
        assert False, f"Login request failed: {str(e)}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Request CSV export of users report
    export_url = f"{BASE_URL}/reports/export/users.csv"
    try:
        export_resp = requests.get(export_url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"CSV export request failed: {str(e)}"

    assert export_resp.status_code == 200, f"Expected HTTP 200 but got {export_resp.status_code}"
    content_type = export_resp.headers.get("Content-Type", "")
    assert "text/csv" in content_type.lower(), f"Expected Content-Type 'text/csv' but got '{content_type}'"

    content_disposition = export_resp.headers.get("Content-Disposition", "")
    # The Content-Disposition header should contain attachment; filename=reporte_guardas.csv, exact casing may vary
    assert content_disposition.lower().startswith("attachment"), "Content-Disposition header missing or not an attachment"
    assert "reporte_guardas.csv" in content_disposition.lower(), f"Content-Disposition filename not 'reporte_guardas.csv': '{content_disposition}'"

    # Optionally check that response body is not empty and starts with header CSV line pattern (e.g. maybe checking presence of some header column)
    content = export_resp.content
    assert content, "CSV content is empty"
    # Check first few bytes represent text readable as CSV (utf-8), or at least contains typical CSV delimiters like comma or semicolon
    try:
        text = content.decode("utf-8")
        assert ("," in text or ";" in text), "CSV content does not contain expected delimiters"
    except UnicodeDecodeError:
        assert False, "CSV content not decodable as UTF-8"


test_supervisor_can_export_users_report_as_csv()