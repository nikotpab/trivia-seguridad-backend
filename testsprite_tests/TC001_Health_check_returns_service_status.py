import requests

def test_tc001_health_check_returns_service_status():
    base_url = "http://localhost:8000"
    url = f"{base_url}/api/v1/health"

    try:
        response = requests.get(url, timeout=30)
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

        json_data = response.json()
        expected = {'status': 'ok', 'service': 'trivia-seguridad-api'}
        assert json_data == expected, f"Expected JSON {expected}, got {json_data}"

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_tc001_health_check_returns_service_status()