"""Partidas del quiz (Función 2). Disponible para todos los roles."""
from flask import Blueprint, current_app, g, jsonify, request

from ..auth.decorators import require_auth
from ..services import game_service
from ..services.game_service import GameError

bp = Blueprint("game", __name__)


@bp.errorhandler(GameError)
def handle_game_error(exc: GameError):
    return jsonify(error=exc.message), exc.status


@bp.post("/sessions")
@require_auth()
def start_session():
    data = request.get_json(silent=True) or {}
    topic_id = data.get("topic_id")
    if not topic_id:
        return jsonify(error="topic_id es obligatorio"), 422
    cfg = current_app.config
    num = min(int(data.get("num_questions", cfg["GAME_DEFAULT_QUESTIONS"])),
              cfg["GAME_MAX_QUESTIONS"])
    payload = game_service.start_session(g.current_user, topic_id, max(num, 1))
    return jsonify(payload), 201


@bp.get("/sessions/<int:session_id>")
@require_auth()
def get_session(session_id: int):
    return jsonify(game_service.get_state(g.current_user, session_id))


@bp.post("/sessions/<int:session_id>/answer")
@require_auth()
def answer(session_id: int):
    data = request.get_json(silent=True) or {}
    choice_id = data.get("choice_id")
    if not choice_id:
        return jsonify(error="choice_id es obligatorio"), 422
    return jsonify(game_service.submit_answer(g.current_user, session_id, choice_id))


@bp.post("/sessions/<int:session_id>/lifeline")
@require_auth()
def lifeline(session_id: int):
    data = request.get_json(silent=True) or {}
    kind = data.get("type")
    if not kind:
        return jsonify(error="type es obligatorio (fifty_fifty | skip)"), 422
    return jsonify(game_service.use_lifeline(g.current_user, session_id, kind))


@bp.post("/sessions/<int:session_id>/abandon")
@require_auth()
def abandon(session_id: int):
    return jsonify(game_service.abandon(g.current_user, session_id))
