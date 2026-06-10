"""Flujo completo del quiz: la opción correcta del seed siempre es 'Opción 1'."""
import pytest

from .conftest import auth_header


def _start(client, headers, num=6):
    res = client.post("/api/v1/game/sessions",
                      json={"topic_id": 1, "num_questions": num}, headers=headers)
    assert res.status_code == 201, res.get_json()
    return res.get_json()


def _correct_choice(question):
    return next(c for c in question["choices"] if c["text"] == "Opción 1")


def _wrong_choice(question):
    return next(c for c in question["choices"] if c["text"] != "Opción 1")


def _answer(client, headers, session_id, choice_id):
    res = client.post(f"/api/v1/game/sessions/{session_id}/answer",
                      json={"choice_id": choice_id}, headers=headers)
    assert res.status_code == 200, res.get_json()
    return res.get_json()


def test_player_payload_is_sanitized(client):
    payload = _start(client, auth_header(client))
    question = payload["question"]
    assert "is_correct" not in question["choices"][0]
    assert question["points"] in (100, 200, 300)
    # de fácil a difícil
    assert question["difficulty"] == "facil"


def test_full_game_correct_answers(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]

    data = payload
    for _ in range(6):
        data = _answer(client, headers, sid, _correct_choice(data["question"])["id"])
        assert data["result"]["is_correct"] is True
        if data["finished"]:
            break

    assert data["finished"] is True
    summary = data["summary"]
    assert summary["session"]["status"] == "finished"
    assert summary["session"]["correct_count"] == 6
    assert summary["accuracy"] == pytest.approx(1.0)
    # racha completa de 6 -> insignias
    codes = {b["code"] for b in summary["new_badges"]}
    assert {"primera_mision", "perfeccionista", "racha_de_5"} <= codes
    # puntos acumulados en el perfil
    me = client.get("/api/v1/auth/me", headers=headers).get_json()["user"]
    assert me["total_points"] == summary["session"]["score"] > 0


def test_streak_bonus(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]

    # primera correcta: sin bono; segunda correcta consecutiva: +10%
    data = _answer(client, headers, sid, _correct_choice(payload["question"])["id"])
    first = data["result"]["points_awarded"]
    data2 = _answer(client, headers, sid, _correct_choice(data["question"])["id"])
    second = data2["result"]["points_awarded"]
    base_second = data["question"]["points"]
    assert second == round(base_second * 1.1)
    assert first == payload["question"]["points"]


def test_wrong_answer_resets_streak(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]

    data = _answer(client, headers, sid, _wrong_choice(payload["question"])["id"])
    assert data["result"]["is_correct"] is False
    assert data["result"]["points_awarded"] == 0
    assert data["result"]["correct_choice_id"] is not None
    assert data["session"]["streak"] == 0


def test_fifty_fifty(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]

    res = client.post(f"/api/v1/game/sessions/{sid}/lifeline",
                      json={"type": "fifty_fifty"}, headers=headers)
    assert res.status_code == 200
    choices = res.get_json()["question"]["choices"]
    assert len(choices) == 2
    assert any(c["text"] == "Opción 1" for c in choices)  # la correcta sobrevive

    # segundo uso -> rechazado
    res = client.post(f"/api/v1/game/sessions/{sid}/lifeline",
                      json={"type": "fifty_fifty"}, headers=headers)
    assert res.status_code == 409


def test_skip(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]

    res = client.post(f"/api/v1/game/sessions/{sid}/lifeline",
                      json={"type": "skip"}, headers=headers)
    data = res.get_json()
    assert res.status_code == 200
    assert data["session"]["current_index"] == 1
    assert data["session"]["score"] == 0


def test_cannot_answer_with_foreign_choice(client):
    headers = auth_header(client)
    payload = _start(client, headers)
    sid = payload["session"]["id"]
    # un choice_id que no pertenece a la pregunta actual
    current_ids = {c["id"] for c in payload["question"]["choices"]}
    foreign = next(i for i in range(1, 100) if i not in current_ids)
    res = client.post(f"/api/v1/game/sessions/{sid}/answer",
                      json={"choice_id": foreign}, headers=headers)
    assert res.status_code == 422


def test_one_active_session_per_user(client):
    headers = auth_header(client)
    _start(client, headers)
    res = client.post("/api/v1/game/sessions", json={"topic_id": 1}, headers=headers)
    assert res.status_code == 409


def test_abandon_and_restart(client):
    headers = auth_header(client)
    sid = _start(client, headers)["session"]["id"]
    res = client.post(f"/api/v1/game/sessions/{sid}/abandon", headers=headers)
    assert res.get_json()["session"]["status"] == "abandoned"
    assert client.post("/api/v1/game/sessions", json={"topic_id": 1},
                       headers=headers).status_code == 201


def test_cannot_access_foreign_session(client):
    sid = _start(client, auth_header(client))["session"]["id"]
    other = auth_header(client, "guarda2@test.co")
    assert client.get(f"/api/v1/game/sessions/{sid}", headers=other).status_code == 404
