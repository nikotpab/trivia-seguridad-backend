"""Banco de preguntas — solo administradores (Función 3).

Cada pregunta tiene 4 opciones y exactamente una correcta.
Incluye carga masiva (POST /questions/import) para migrar contenido.
"""
from flask import Blueprint, g, jsonify, request

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import Choice, Question, Topic
from ..models.question import DIFFICULTY_POINTS
from ..security_log import log_event

bp = Blueprint("questions", __name__)

DIFFICULTIES = tuple(DIFFICULTY_POINTS.keys())
QUESTION_NOT_FOUND = "Pregunta no encontrada"


def _validate_payload(data: dict) -> str | None:
    """Devuelve un mensaje de error o None si el payload es válido."""
    if not (data.get("text") or "").strip():
        return "text es obligatorio"
    if not db.session.get(Topic, data.get("topic_id") or 0):
        return "topic_id no existe"
    if data.get("difficulty", "media") not in DIFFICULTIES:
        return f"difficulty inválida. Opciones: {', '.join(DIFFICULTIES)}"
    choices = data.get("choices") or []
    if len(choices) != 4:
        return "Se requieren exactamente 4 opciones"
    if sum(1 for c in choices if c.get("is_correct")) != 1:
        return "Debe haber exactamente una opción correcta"
    if any(not (c.get("text") or "").strip() for c in choices):
        return "Todas las opciones deben tener texto"
    return None


def _build_question(data: dict) -> Question:
    question = Question(
        topic_id=data["topic_id"],
        text=data["text"].strip(),
        difficulty=data.get("difficulty", "media"),
        explanation=data.get("explanation", ""),
    )
    for c in data["choices"]:
        question.choices.append(Choice(text=c["text"].strip(),
                                       is_correct=bool(c.get("is_correct"))))
    return question


@bp.get("")
@require_auth("admin")
def list_questions():
    query = Question.query
    if topic_id := request.args.get("topic_id", type=int):
        query = query.filter_by(topic_id=topic_id)
    if difficulty := request.args.get("difficulty"):
        query = query.filter_by(difficulty=difficulty)
    if request.args.get("include_inactive") != "1":
        query = query.filter_by(is_active=True)
    if q := request.args.get("q"):
        query = query.filter(Question.text.ilike(f"%{q}%"))

    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    pag = query.order_by(Question.id.desc()).paginate(page=page, per_page=per_page,
                                                      error_out=False)
    return jsonify(items=[q.to_dict(include_answers=True) for q in pag.items],
                   total=pag.total, page=page, pages=pag.pages)


@bp.post("")
@require_auth("admin")
def create_question():
    data = request.get_json(silent=True) or {}
    if error := _validate_payload(data):
        return jsonify(error=error), 422
    question = _build_question(data)
    db.session.add(question)
    db.session.commit()
    return jsonify(question=question.to_dict(include_answers=True)), 201


@bp.post("/import")
@require_auth("admin")
def import_questions():
    """Carga masiva: {"items": [<payload de pregunta>, ...]}. Atómica."""
    items = (request.get_json(silent=True) or {}).get("items") or []
    if not items:
        return jsonify(error="items vacío"), 422
    for i, data in enumerate(items):
        if error := _validate_payload(data):
            return jsonify(error=f"Ítem {i}: {error}"), 422
    questions = [_build_question(d) for d in items]
    db.session.add_all(questions)
    db.session.commit()
    log_event("questions_imported", actor=g.current_user.id, count=len(questions))
    return jsonify(created=len(questions)), 201


@bp.get("/<int:question_id>")
@require_auth("admin")
def get_question(question_id: int):
    question = db.session.get(Question, question_id)
    if not question:
        return jsonify(error=QUESTION_NOT_FOUND), 404
    return jsonify(question=question.to_dict(include_answers=True))


@bp.patch("/<int:question_id>")
@require_auth("admin")
def update_question(question_id: int):
    question = db.session.get(Question, question_id)
    if not question:
        return jsonify(error=QUESTION_NOT_FOUND), 404

    data = request.get_json(silent=True) or {}
    if "text" in data:
        text = str(data["text"] or "").strip()
        if not text:
            return jsonify(error="text no puede estar vacío"), 422
        question.text = text
    if "difficulty" in data:
        if data["difficulty"] not in DIFFICULTIES:
            return jsonify(error=f"difficulty inválida. Opciones: {', '.join(DIFFICULTIES)}"), 422
        question.difficulty = data["difficulty"]
    if "explanation" in data:
        question.explanation = data["explanation"]
    if "is_active" in data:
        question.is_active = bool(data["is_active"])
    if "choices" in data:
        choices = data["choices"]
        if len(choices) != 4 or sum(1 for c in choices if c.get("is_correct")) != 1:
            return jsonify(error="Se requieren 4 opciones con exactamente una correcta"), 422
        question.choices.clear()
        for c in choices:
            question.choices.append(Choice(text=c["text"].strip(),
                                           is_correct=bool(c.get("is_correct"))))
    db.session.commit()
    return jsonify(question=question.to_dict(include_answers=True))


@bp.delete("/<int:question_id>")
@require_auth("admin")
def deactivate_question(question_id: int):
    """Borrado lógico: las partidas históricas conservan su referencia."""
    question = db.session.get(Question, question_id)
    if not question:
        return jsonify(error=QUESTION_NOT_FOUND), 404
    question.is_active = False
    db.session.commit()
    return jsonify(message="Pregunta desactivada")
