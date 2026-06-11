"""Reportes para supervisores y administradores — Función 5 del MVP."""
import csv
import io
from datetime import datetime, timedelta, timezone

from ..extensions import db
from ..models import GameSession, Question, SessionAnswer, Topic, User
from .gamification_service import rank_info

CRITICAL_ACCURACY = 0.60   # tema crítico: precisión < 60%
CRITICAL_MIN_ATTEMPTS = 10

# Caracteres que disparan fórmulas al abrir el CSV en Excel/LibreOffice
_CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(value) -> str:
    """Neutraliza la inyección de fórmulas (CWE-1236) en celdas con texto
    controlado por el usuario (nombre, email)."""
    text = "" if value is None else str(value)
    if text and text[0] in _CSV_FORMULA_PREFIXES:
        return "'" + text
    return text


def _accuracy_query(filters: list):
    """(total respondidas, correctas) excluyendo preguntas saltadas."""
    row = (
        db.session.query(
            db.func.count(SessionAnswer.id),
            db.func.sum(db.case((SessionAnswer.is_correct.is_(True), 1), else_=0)),
        )
        .join(GameSession, SessionAnswer.session_id == GameSession.id)
        .filter(SessionAnswer.is_correct.isnot(None), *filters)
        .first()
    )
    return row[0] or 0, row[1] or 0


def overview() -> dict:
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total, correct = _accuracy_query([])
    return {
        "guards_active": User.query.filter_by(role="guarda", is_active=True).count(),
        "sessions_finished": GameSession.query.filter_by(status="finished").count(),
        "questions_in_bank": Question.query.filter_by(is_active=True).count(),
        "answers_total": total,
        "overall_accuracy": round(correct / total, 4) if total else None,
        "active_last_7_days": User.query.filter(
            User.last_activity_at.isnot(None),
            User.last_activity_at >= week_ago.replace(tzinfo=None)).count(),
    }


def users_report() -> list[dict]:
    rows = []
    guards = (User.query.filter_by(role="guarda")
              .order_by(User.total_points.desc()).all())
    for user in guards:
        total, correct = _accuracy_query([GameSession.user_id == user.id])
        rows.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "is_active": user.is_active,
            "total_points": user.total_points,
            "rank": rank_info(user.total_points)["name"],
            "sessions_finished": user.sessions.filter_by(status="finished").count(),
            "answers": total,
            "accuracy": round(correct / total, 4) if total else None,
            "last_activity_at": user.last_activity_at.isoformat()
                                if user.last_activity_at else None,
        })
    return rows


def user_detail(user_id: int) -> dict | None:
    user = db.session.get(User, user_id)
    if not user:
        return None
    by_topic = []
    for topic in Topic.query.order_by(Topic.level, Topic.name).all():
        total, correct = _accuracy_query([
            GameSession.user_id == user.id, GameSession.topic_id == topic.id])
        if total:
            by_topic.append({
                "topic_id": topic.id, "topic_name": topic.name,
                "answers": total, "accuracy": round(correct / total, 4),
            })
    recent = (user.sessions.order_by(GameSession.started_at.desc())
              .limit(10).all())
    return {
        "user": user.to_dict(include_stats=True),
        "by_topic": by_topic,
        "recent_sessions": [s.to_dict() for s in recent],
    }


def topics_report() -> list[dict]:
    rows = []
    for topic in Topic.query.order_by(Topic.level, Topic.name).all():
        total, correct = _accuracy_query([GameSession.topic_id == topic.id])
        accuracy = round(correct / total, 4) if total else None
        rows.append({
            "topic_id": topic.id,
            "topic_name": topic.name,
            "level": topic.level,
            "question_count": topic.questions.filter_by(is_active=True).count(),
            "answers": total,
            "accuracy": accuracy,
            # Tema crítico: dónde reforzar la capacitación
            "is_critical": (total >= CRITICAL_MIN_ATTEMPTS
                            and accuracy is not None
                            and accuracy < CRITICAL_ACCURACY),
        })
    return rows


def users_csv() -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "nombre", "email", "activo", "puntos", "rango",
                     "partidas", "respuestas", "precision", "ultima_actividad"])
    for row in users_report():
        writer.writerow([
            row["id"], _csv_safe(row["full_name"]), _csv_safe(row["email"]),
            "si" if row["is_active"] else "no",
            row["total_points"], _csv_safe(row["rank"]), row["sessions_finished"],
            row["answers"],
            f"{row['accuracy']:.2%}" if row["accuracy"] is not None else "",
            row["last_activity_at"] or "",
        ])
    return buffer.getvalue()
