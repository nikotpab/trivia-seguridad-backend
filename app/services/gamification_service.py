"""Puntos, rangos e insignias — Función 4 del MVP.

Reglas de puntaje (mecánica tipo concurso):
  - Puntos base por dificultad: fácil 100 · media 200 · difícil 300
  - Bono de racha: +10% por cada acierto consecutivo después del primero,
    con tope de +50% (racha de 6 o más).
"""
from ..extensions import db
from ..models import Badge, GameSession, SessionAnswer, UserBadge, RANKS
from ..models.question import DIFFICULTY_POINTS

STREAK_BONUS_STEP = 0.10
STREAK_BONUS_CAP = 0.50

# Catálogo de insignias (los seeds lo insertan en la tabla `badges`)
BADGE_CATALOG = [
    {"code": "primera_mision",  "name": "Primera Misión",
     "description": "Completaste tu primera partida de capacitación."},
    {"code": "perfeccionista",  "name": "Perfeccionista",
     "description": "Partida perfecta: todas las respuestas correctas (mínimo 5 preguntas)."},
    {"code": "racha_de_5",      "name": "Racha de 5",
     "description": "Cinco aciertos consecutivos en una misma partida."},
    {"code": "veterano",        "name": "Veterano",
     "description": "Diez partidas completadas."},
    {"code": "experto_en_tema", "name": "Experto en Tema",
     "description": "90% de acierto en un tema con al menos 20 preguntas respondidas."},
    {"code": "leyenda_dorada",  "name": "Leyenda Dorada",
     "description": "Acumulaste 50.000 puntos totales."},
]


def points_for(difficulty: str, streak: int) -> int:
    """Puntos por un acierto, dado el tamaño de la racha (incluyéndolo)."""
    base = DIFFICULTY_POINTS.get(difficulty, 100)
    bonus = min(max(streak - 1, 0) * STREAK_BONUS_STEP, STREAK_BONUS_CAP)
    return round(base * (1 + bonus))


def rank_info(total_points: int) -> dict:
    """Rango actual y progreso hacia el siguiente (Escala de Mando)."""
    current = RANKS[0]
    next_rank = None
    for rank in RANKS:
        if total_points >= rank["threshold"]:
            current = rank
        else:
            next_rank = rank
            break
    progress = 1.0
    if next_rank:
        span = next_rank["threshold"] - current["threshold"]
        progress = round((total_points - current["threshold"]) / span, 4) if span else 1.0
    return {
        "id": current["id"],
        "name": current["name"],
        "points": total_points,
        "next_rank": next_rank["name"] if next_rank else None,
        "next_threshold": next_rank["threshold"] if next_rank else None,
        "progress_to_next": progress,
    }


def _award(user, code: str, earned: list) -> None:
    badge = Badge.query.filter_by(code=code).first()
    if not badge:
        return
    exists = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
    if not exists:
        db.session.add(UserBadge(user_id=user.id, badge_id=badge.id))
        earned.append(badge.to_dict())


def evaluate_badges(user, session: GameSession) -> list[dict]:
    """Evalúa e otorga insignias al terminar una partida. Devuelve las nuevas."""
    earned: list[dict] = []
    finished = user.sessions.filter_by(status="finished").count()

    if finished >= 1:
        _award(user, "primera_mision", earned)
    if finished >= 10:
        _award(user, "veterano", earned)

    answered = [a for a in session.answers if a.is_correct is not None]
    if len(answered) >= 5 and all(a.is_correct for a in answered):
        _award(user, "perfeccionista", earned)
    if session.best_streak >= 5:
        _award(user, "racha_de_5", earned)
    if user.total_points >= 50_000:
        _award(user, "leyenda_dorada", earned)

    # Experto en tema: precisión >= 90% con >= 20 respuestas en el tema
    topic_stats = (
        db.session.query(
            db.func.count(SessionAnswer.id),
            db.func.sum(db.case((SessionAnswer.is_correct.is_(True), 1), else_=0)),
        )
        .join(GameSession, SessionAnswer.session_id == GameSession.id)
        .filter(GameSession.user_id == user.id,
                GameSession.topic_id == session.topic_id,
                SessionAnswer.is_correct.isnot(None))
        .first()
    )
    total, correct = topic_stats[0] or 0, topic_stats[1] or 0
    if total >= 20 and correct / total >= 0.9:
        _award(user, "experto_en_tema", earned)

    return earned
