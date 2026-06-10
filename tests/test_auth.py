from .conftest import auth_header, login


def test_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_login_ok(client):
    token = login(client, "guarda@test.co")
    assert token


def test_login_bad_password(client):
    res = client.post("/api/v1/auth/login",
                      json={"email": "guarda@test.co", "password": "mala"})
    assert res.status_code == 401


def test_me(client):
    res = client.get("/api/v1/auth/me", headers=auth_header(client))
    assert res.status_code == 200
    data = res.get_json()["user"]
    assert data["email"] == "guarda@test.co"
    assert data["rank"]["name"] == "Recluta"


def test_no_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_invalid_token(client):
    res = client.get("/api/v1/auth/me",
                     headers={"Authorization": "Bearer no-es-un-token"})
    assert res.status_code == 401


# --- RBAC ---
def test_guarda_cannot_manage_users(client):
    headers = auth_header(client)
    assert client.get("/api/v1/users", headers=headers).status_code == 403


def test_guarda_cannot_see_reports(client):
    headers = auth_header(client)
    assert client.get("/api/v1/reports/overview", headers=headers).status_code == 403


def test_supervisor_cannot_manage_questions(client):
    headers = auth_header(client, "super@test.co")
    assert client.get("/api/v1/questions", headers=headers).status_code == 403


def test_admin_can_do_everything(client):
    headers = auth_header(client, "admin@test.co")
    assert client.get("/api/v1/users", headers=headers).status_code == 200
    assert client.get("/api/v1/questions", headers=headers).status_code == 200
    assert client.get("/api/v1/reports/overview", headers=headers).status_code == 200
