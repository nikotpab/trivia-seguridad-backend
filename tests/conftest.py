import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Badge, Choice, Question, Topic, User
from app.services.gamification_service import BADGE_CATALOG


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        _seed_minimal()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed_minimal():
    users = [
        ("admin@test.co", "Admin Test", "admin", "Admin123*"),
        ("super@test.co", "Super Test", "supervisor", "Super123*"),
        ("guarda@test.co", "Guarda Test", "guarda", "Guarda123*"),
        ("guarda2@test.co", "Guarda Dos", "guarda", "Guarda123*"),
    ]
    for email, name, role, password in users:
        user = User(email=email, full_name=name, role=role)
        user.set_password(password)
        db.session.add(user)

    topic = Topic(name="Control de Accesos", level=1)
    db.session.add(topic)
    db.session.flush()

    # 6 preguntas: A/B/C/D, la correcta siempre es la opción "Correcta"
    for i in range(6):
        difficulty = ["facil", "media", "dificil"][i % 3]
        question = Question(topic_id=topic.id, text=f"Pregunta {i+1}",
                            difficulty=difficulty, explanation=f"Explicación {i+1}")
        for j in range(4):
            question.choices.append(Choice(text=f"Opción {j+1}", is_correct=j == 0))
        db.session.add(question)

    for data in BADGE_CATALOG:
        db.session.add(Badge(**data))
    db.session.commit()


def login(client, email, password):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


def auth_header(client, email="guarda@test.co", password="Guarda123*"):
    return {"Authorization": f"Bearer {login(client, email, password)}"}
