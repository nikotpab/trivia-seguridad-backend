"""Gestión de usuarios — solo administradores (Función 1)."""
from flask import Blueprint, g, jsonify, request

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import User
from ..models.user import ROLES

bp = Blueprint("users", __name__)

USER_NOT_FOUND = "Usuario no encontrado"


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
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(int(request.args.get("per_page", 20)), 100)
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
    if User.query.filter_by(email=email).first():
        return jsonify(error="Ya existe un usuario con ese email"), 409

    user = User(email=email, full_name=full_name, role=role)
    if password:
        user.set_password(password)
    db.session.add(user)
    db.session.commit()
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
        user.full_name = data["full_name"].strip()
    if "role" in data:
        if data["role"] not in ROLES:
            return jsonify(error=f"Rol inválido. Opciones: {', '.join(ROLES)}"), 422
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if data.get("password"):
        user.set_password(data["password"])
    db.session.commit()
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
    return jsonify(message="Usuario desactivado", user=user.to_dict())
