"""Gestión de usuarios — solo administradores (Función 1)."""
from flask import Blueprint, current_app, g, jsonify, request

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import User
from ..models.user import ROLES
from ..security_log import log_event

bp = Blueprint("users", __name__)

USER_NOT_FOUND = "Usuario no encontrado"


def _password_error(password: str) -> str | None:
    """Valida la política de contraseñas (modo local). None si es válida."""
    minimum = current_app.config["MIN_PASSWORD_LENGTH"]
    if not isinstance(password, str) or len(password) < minimum:
        return f"La contraseña debe tener al menos {minimum} caracteres"
    return None


@bp.get("")
@require_auth("admin")
def list_users():
    query = User.query
    if role := request.args.get("role"):
        query = query.filter_by(role=role)
    if q := request.args.get("q"):
        like = f"%{q}%"
        query = query.filter(db.or_(User.full_name.ilike(like),
                                    User.email.ilike(like)))
    page = max(request.args.get("page", 1, type=int) or 1, 1)
    per_page = min(request.args.get("per_page", 20, type=int) or 20, 100)
    pag = query.order_by(User.full_name).paginate(page=page, per_page=per_page,
                                                  error_out=False)
    return jsonify(items=[u.to_dict() for u in pag.items],
                   total=pag.total, page=page, pages=pag.pages)


@bp.post("")
@require_auth("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    role = data.get("role", "guarda")
    password = data.get("password")

    if not email or not full_name:
        return jsonify(error="email y full_name son obligatorios"), 422
    if role not in ROLES:
        return jsonify(error=f"Rol inválido. Opciones: {', '.join(ROLES)}"), 422
    if password is not None and (err := _password_error(password)):
        return jsonify(error=err), 422
    if User.query.filter_by(email=email).first():
        return jsonify(error="Ya existe un usuario con ese email"), 409

    user = User(email=email, full_name=full_name, role=role)
    if password:
        user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_event("user_created", actor=g.current_user.id, target=user.id, role=role)
    return jsonify(user=user.to_dict()), 201


@bp.get("/<int:user_id>")
@require_auth("admin")
def get_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error=USER_NOT_FOUND), 404
    return jsonify(user=user.to_dict(include_stats=True))


@bp.patch("/<int:user_id>")
@require_auth("admin")
def update_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error=USER_NOT_FOUND), 404

    data = request.get_json(silent=True) or {}
    if "full_name" in data:
        full_name = str(data["full_name"] or "").strip()
        if not full_name:
            return jsonify(error="full_name no puede estar vacío"), 422
        user.full_name = full_name
    if "role" in data:
        if data["role"] not in ROLES:
            return jsonify(error=f"Rol inválido. Opciones: {', '.join(ROLES)}"), 422
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if data.get("password"):
        if err := _password_error(data["password"]):
            return jsonify(error=err), 422
        user.set_password(data["password"])
    db.session.commit()
    log_event("user_updated", actor=g.current_user.id, target=user.id)
    return jsonify(user=user.to_dict())


@bp.delete("/<int:user_id>")
@require_auth("admin")
def deactivate_user(user_id: int):
    """Borrado lógico: conserva el historial de capacitación (Ley 1581:
    los datos se retienen según la política de tratamiento de la empresa)."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error=USER_NOT_FOUND), 404
    if user.id == g.current_user.id:
        return jsonify(error="No puedes desactivar tu propia cuenta"), 422
    user.is_active = False
    db.session.commit()
    log_event("user_deactivated", actor=g.current_user.id, target=user.id)
    return jsonify(message="Usuario desactivado", user=user.to_dict())
