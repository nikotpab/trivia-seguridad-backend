import requests

def test_get_api_v1_health_returns_service_status():
    base_url = "http://localhost:8000"
    url = f"{base_url}/api/v1/health"
    timeout = 30

    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(json_data, dict), "Response JSON is not an object"
    assert json_data.get("status") == "ok", f"Expected status 'ok' but got {json_data.get('status')}"
    assert json_data.get("service") == "trivia-seguridad-api", f"Expected service 'trivia-seguridad-api' but got {json_data.get('service')}"

test_get_api_v1_health_returns_service_status()