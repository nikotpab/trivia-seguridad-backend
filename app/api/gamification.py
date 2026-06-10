"""Insignias, rangos y tabla de posiciones (Función 4)."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, g, jsonify, request

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import Badge, GameSession, SessionAnswer, User, RANKS
from ..services.gamification_service import rank_info

bp = Blueprint("gamification", __name__)


@bp.get("/ranks")
@require_auth()
def ranks():
    """Escala de Mando completa + posición del usuario actual."""
    return jsonify(ranks=RANKS, me=rank_info(g.current_user.total_points))


@bp.get("/badges")
@require_auth()
def badges():
    """Catálogo de insignias indicando cuáles tiene el usuario."""
    owned = {ub.badge_id: ub.awarded_at for ub in g.current_user.badges}
    items = []
    for badge in Badge.query.order_by(Badge.id).all():
        data = badge.to_dict()
        data["unlocked"] = badge.id in owned
        data["awarded_at"] = owned[badge.id].isoformat() if badge.id in owned else None
        items.append(data)
    return jsonify(items=items)


@bp.get("/leaderboard")
@require_auth()
def leaderboard():
    """Tabla de posiciones. ?period=all|month|week, ?limit=10"""
    period = request.args.get("period", "all")
    limit = min(request.args.get("limit", 10, type=int), 50)

    if period == "all":
        users = (User.query.filter_by(role="guarda", is_active=True)
                 .order_by(User.total_points.desc(), User.full_name)
                 .limit(limit).all())
        rows = [{"user_id": u.id, "full_name": u.full_name,
                 "points": u.total_points,
                 "rank": rank_info(u.total_points)["name"]} for u in users]
    elif period in ("week", "month"):
        days = 7 if period == "week" else 30
        since = datetime.now(timezone.utc) - timedelta(days=days)
        results = (
            db.session.query(User, db.func.sum(SessionAnswer.points_awarded))
            .join(GameSession, GameSession.user_id == User.id)
            .join(SessionAnswer, SessionAnswer.session_id == GameSession.id)
            .filter(User.role == "guarda", User.is_active.is_(True),
                    SessionAnswer.answered_at >= since.replace(tzinfo=None))
            .group_by(User.id)
            .order_by(db.func.sum(SessionAnswer.points_awarded).desc())
            .limit(limit).all()
        )
        rows = [{"user_id": u.id, "full_name": u.full_name,
                 "points": int(points or 0),
                 "rank": rank_info(u.total_points)["name"]}
                for u, points in results]
    else:
        return jsonify(error="period inválido: all | month | week"), 422

    for i, row in enumerate(rows, start=1):
        row["position"] = i
    return jsonify(items=rows, period=period)
