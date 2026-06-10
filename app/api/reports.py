"""Panel del supervisor (Función 5) — supervisor y admin."""
from flask import Blueprint, Response, jsonify

from ..auth.decorators import require_auth
from ..services import report_service

bp = Blueprint("reports", __name__)


@bp.get("/overview")
@require_auth("supervisor")
def overview():
    return jsonify(report_service.overview())


@bp.get("/users")
@require_auth("supervisor")
def users():
    return jsonify(items=report_service.users_report())


@bp.get("/users/<int:user_id>")
@require_auth("supervisor")
def user_detail(user_id: int):
    detail = report_service.user_detail(user_id)
    if not detail:
        return jsonify(error="Usuario no encontrado"), 404
    return jsonify(detail)


@bp.get("/topics")
@require_auth("supervisor")
def topics():
    """Precisión por tema; marca temas críticos donde reforzar capacitación."""
    return jsonify(items=report_service.topics_report())


@bp.get("/export/users.csv")
@require_auth("supervisor")
def export_users_csv():
    csv_data = report_service.users_csv()
    return Response(
        csv_data, mimetype="text/csv",
        headers={"Content-Disposition":
                 "attachment; filename=reporte_guardas.csv"})
