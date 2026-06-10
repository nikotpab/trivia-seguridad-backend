"""Motor del quiz — Función 2 del MVP.

Toda la mecánica se valida en el servidor (anti-trampa):
  - El servidor elige y ordena las preguntas al crear la sesión.
  - El jugador nunca recibe cuál opción es la correcta.
  - Puntaje, rachas y comodines se calculan aquí.

Comodines (una vez por partida cada uno):
  - fifty_fifty : descarta dos opciones incorrectas.
  - skip        : salta la pregunta sin penalización (no cuenta en precisión).
"""
import random
from datetime import datetime, timezone

from ..extensions import db
from ..models import Choice, GameSession, Question, SessionAnswer, Topic, User
from .gamification_service import evaluate_badges, points_for, rank_info


class GameError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def _current_question(session: GameSession) -> Question:
    qid = session.question_ids[session.current_index]
    return db.session.get(Question, qid)


def _question_payload(session: GameSession) -> dict:
    """Pregunta actual sanitizada + estado de la partida."""
    question = _current_question(session)
    payload = question.to_player_dict()
    random.shuffle(payload["choices"])
    # Si ya se usó 50/50 en esta pregunta, respetar las opciones reducidas
    ff = (session.lifelines_used or {}).get("fifty_fifty")
    if ff and ff.get("question_id") == question.id:
        keep = set(ff["kept_choice_ids"])
        payload["choices"] = [c for c in payload["choices"] if c["id"] in keep]
    return {"session": session.to_dict(), "question": payload}


def start_session(user: User, topic_id: int, num_questions: int) -> dict:
    topic = db.session.get(Topic, topic_id)
    if not topic or not topic.is_active:
        raise GameError("Tema no encontrado", 404)

    if user.sessions.filter_by(status="active").count():
        raise GameError("Ya tienes una partida activa. Termínala o abandónala primero.", 409)

    questions = (Question.query
                 .filter_by(topic_id=topic_id, is_active=True)
                 .all())
    if not questions:
        raise GameError("El tema no tiene preguntas disponibles", 422)

    random.shuffle(questions)
    selected = questions[:num_questions]
    # Orden tipo concurso: de fácil a difícil
    order = {"facil": 0, "media": 1, "dificil": 2}
    selected.sort(key=lambda q: order.get(q.difficulty, 1))

    session = GameSession(user_id=user.id, topic_id=topic_id,
                          question_ids=[q.id for q in selected])
    db.session.add(session)
    db.session.commit()
    return _question_payload(session)


def get_state(user: User, session_id: int) -> dict:
    session = _owned_session(user, session_id)
    if session.is_finished:
        return {"session": session.to_dict(), "question": None}
    return _question_payload(session)


def _owned_session(user: User, session_id: int) -> GameSession:
    session = db.session.get(GameSession, session_id)
    if not session or session.user_id != user.id:
        raise GameError("Partida no encontrada", 404)
    return session


def _active_session(user: User, session_id: int) -> GameSession:
    session = _owned_session(user, session_id)
    if session.is_finished:
        raise GameError("La partida ya terminó", 409)
    return session


def submit_answer(user: User, session_id: int, choice_id: int) -> dict:
    session = _active_session(user, session_id)
    question = _current_question(session)

    choice = db.session.get(Choice, choice_id)
    if not choice or choice.question_id != question.id:
        raise GameError("La opción no corresponde a la pregunta actual", 422)

    is_correct = choice.is_correct
    points = 0
    if is_correct:
        session.streak += 1
        session.best_streak = max(session.best_streak, session.streak)
        points = points_for(question.difficulty, session.streak)
        session.score += points
        session.correct_count += 1
        user.total_points += points
    else:
        session.streak = 0

    db.session.add(SessionAnswer(
        session_id=session.id, question_id=question.id,
        choice_id=choice.id, is_correct=is_correct, points_awarded=points,
    ))

    result = {
        "is_correct": is_correct,
        "correct_choice_id": question.correct_choice.id,
        "explanation": question.explanation,
        "points_awarded": points,
    }
    return _advance(session, user, result)


def use_lifeline(user: User, session_id: int, kind: str) -> dict:
    session = _active_session(user, session_id)
    used = dict(session.lifelines_used or {})
    if kind in used:
        raise GameError(f"El comodín '{kind}' ya fue usado en esta partida", 409)

    question = _current_question(session)

    if kind == "fifty_fifty":
        wrong = [c for c in question.choices if not c.is_correct]
        kept = [question.correct_choice.id, random.choice(wrong).id]
        random.shuffle(kept)
        used["fifty_fifty"] = {"question_id": question.id, "kept_choice_ids": kept}
        session.lifelines_used = used
        db.session.commit()
        return _question_payload(session)

    if kind == "skip":
        used["skip"] = {"question_id": question.id}
        session.lifelines_used = used
        session.streak = 0
        db.session.add(SessionAnswer(
            session_id=session.id, question_id=question.id,
            choice_id=None, is_correct=None, points_awarded=0,
        ))
        return _advance(session, user, {"skipped": True})

    raise GameError("Comodín desconocido. Disponibles: fifty_fifty, skip", 422)


def abandon(user: User, session_id: int) -> dict:
    session = _active_session(user, session_id)
    session.status = "abandoned"
    session.finished_at = datetime.now(timezone.utc)
    db.session.commit()
    return {"session": session.to_dict()}


def _advance(session: GameSession, user: User, result: dict) -> dict:
    """Avanza a la siguiente pregunta o cierra la partida."""
    session.current_index += 1
    finished = session.current_index >= session.total_questions

    if finished:
        session.status = "finished"
        session.finished_at = datetime.now(timezone.utc)
        db.session.commit()
        new_badges = evaluate_badges(user, session)
        db.session.commit()
        answered = [a for a in session.answers if a.is_correct is not None]
        accuracy = (session.correct_count / len(answered)) if answered else 0.0
        return {
            "result": result,
            "finished": True,
            "summary": {
                "session": session.to_dict(),
                "accuracy": round(accuracy, 4),
                "new_badges": new_badges,
                "rank": rank_info(user.total_points),
            },
        }

    db.session.commit()
    payload = _question_payload(session)
    payload["result"] = result
    payload["finished"] = False
    return payload
