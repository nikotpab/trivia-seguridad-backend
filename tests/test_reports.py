import pytest

from .conftest import auth_header
from .test_game import _answer, _correct_choice, _start


def _play_full_game(client, email="guarda@test.co"):
    headers = auth_header(client, email)
    data = _start(client, headers)
    sid = data["session"]["id"]
    while not data.get("finished"):
        data = _answer(client, headers, sid, _correct_choice(data["question"])["id"])
    return data


def test_overview(client):
    _play_full_game(client)
    headers = auth_header(client, "super@test.co")
    res = client.get("/api/v1/reports/overview", headers=headers)
    data = res.get_json()
    assert data["sessions_finished"] == 1
    assert data["overall_accuracy"] == pytest.approx(1.0)
    assert data["guards_active"] == 2
    assert data["questions_in_bank"] == 6


def test_users_report_and_detail(client):
    _play_full_game(client)
    headers = auth_header(client, "super@test.co")

    rows = client.get("/api/v1/reports/users", headers=headers).get_json()["items"]
    top = rows[0]
    assert top["email"] == "guarda@test.co"
    assert top["accuracy"] == pytest.approx(1.0)
    assert top["sessions_finished"] == 1

    detail = client.get(f"/api/v1/reports/users/{top['id']}",
                        headers=headers).get_json()
    assert detail["by_topic"][0]["topic_name"] == "Control de Accesos"
    assert len(detail["recent_sessions"]) == 1


def test_topics_report(client):
    _play_full_game(client)
    headers = auth_header(client, "super@test.co")
    rows = client.get("/api/v1/reports/topics", headers=headers).get_json()["items"]
    assert rows[0]["answers"] == 6
    assert rows[0]["is_critical"] is False


def test_csv_export(client):
    _play_full_game(client)
    headers = auth_header(client, "super@test.co")
    res = client.get("/api/v1/reports/export/users.csv", headers=headers)
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert "guarda@test.co" in res.get_data(as_text=True)


def test_leaderboard(client):
    _play_full_game(client)
    headers = auth_header(client)
    data = client.get("/api/v1/leaderboard", headers=headers).get_json()
    assert data["items"][0]["full_name"] == "Guarda Test"
    assert data["items"][0]["position"] == 1
    assert data["items"][0]["points"] > 0

    weekly = client.get("/api/v1/leaderboard?period=week", headers=headers).get_json()
    assert weekly["items"][0]["full_name"] == "Guarda Test"


def test_badges_endpoint(client):
    _play_full_game(client)
    headers = auth_header(client)
    items = client.get("/api/v1/badges", headers=headers).get_json()["items"]
    unlocked = {b["code"] for b in items if b["unlocked"]}
    assert "primera_mision" in unlocked
    assert any(not b["unlocked"] for b in items)


def test_ranks_endpoint(client):
    headers = auth_header(client)
    data = client.get("/api/v1/ranks", headers=headers).get_json()
    assert len(data["ranks"]) == 5
    assert data["me"]["name"] == "Recluta"
    assert data["me"]["next_rank"] == "Vigilante I"
