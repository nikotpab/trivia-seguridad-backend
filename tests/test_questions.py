from .conftest import auth_header


def _admin(client):
    return auth_header(client, "admin@test.co")


def _payload(**overrides):
    data = {
        "topic_id": 1,
        "text": "¿Pregunta nueva?",
        "difficulty": "media",
        "explanation": "Porque sí.",
        "choices": [
            {"text": "Correcta", "is_correct": True},
            {"text": "Mala 1"}, {"text": "Mala 2"}, {"text": "Mala 3"},
        ],
    }
    data.update(overrides)
    return data


def test_create_question(client):
    res = client.post("/api/v1/questions", json=_payload(), headers=_admin(client))
    assert res.status_code == 201
    question = res.get_json()["question"]
    assert question["points"] == 200
    assert sum(1 for c in question["choices"] if c["is_correct"]) == 1


def test_create_requires_one_correct(client):
    bad = _payload(choices=[{"text": "a", "is_correct": True},
                            {"text": "b", "is_correct": True},
                            {"text": "c"}, {"text": "d"}])
    res = client.post("/api/v1/questions", json=bad, headers=_admin(client))
    assert res.status_code == 422


def test_create_requires_four_choices(client):
    bad = _payload(choices=[{"text": "a", "is_correct": True}, {"text": "b"}])
    assert client.post("/api/v1/questions", json=bad,
                       headers=_admin(client)).status_code == 422


def test_bulk_import_atomic(client):
    items = [_payload(), _payload(choices=[{"text": "x", "is_correct": True}])]
    res = client.post("/api/v1/questions/import", json={"items": items},
                      headers=_admin(client))
    assert res.status_code == 422  # el segundo es inválido -> nada se crea

    res = client.post("/api/v1/questions/import",
                      json={"items": [_payload(), _payload(text="Otra")]},
                      headers=_admin(client))
    assert res.status_code == 201
    assert res.get_json()["created"] == 2


def test_update_and_deactivate(client):
    headers = _admin(client)
    qid = client.post("/api/v1/questions", json=_payload(),
                      headers=headers).get_json()["question"]["id"]

    res = client.patch(f"/api/v1/questions/{qid}",
                       json={"difficulty": "dificil"}, headers=headers)
    assert res.get_json()["question"]["points"] == 300

    assert client.delete(f"/api/v1/questions/{qid}",
                         headers=headers).status_code == 200
    listed = client.get("/api/v1/questions", headers=headers).get_json()
    assert all(q["id"] != qid for q in listed["items"])


def test_topics_crud(client):
    headers = _admin(client)
    res = client.post("/api/v1/topics", json={"name": "Nuevo Tema", "level": 2},
                      headers=headers)
    assert res.status_code == 201
    # duplicado
    assert client.post("/api/v1/topics", json={"name": "Nuevo Tema"},
                       headers=headers).status_code == 409
    # guarda puede listar temas
    res = client.get("/api/v1/topics", headers=auth_header(client))
    assert res.status_code == 200
    assert len(res.get_json()["items"]) == 2
