"""Decoradores de autenticación y autorización (RBAC).

Uso:
    @require_auth()                  -> cualquier usuario autenticado
    @require_auth("supervisor")     -> supervisor o admin
    @require_auth("admin")          -> solo admin
"""
from datetime import datetime, timezone
from functools import wraps

from flask import g, jsonify, request

from ..extensions import db
from ..models.user import ROLE_ORDER
from ..security_log import log_event
from .tokens import AuthError, verify_token


def require_auth(minimum_role: str = "guarda"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify(error="Falta el token de autorización"), 401
            try:
                user = verify_token(header[7:].strip())
            except AuthError as exc:
                return jsonify(error=exc.message), exc.status

            if ROLE_ORDER[user.role] < ROLE_ORDER[minimum_role]:
                log_event("authz_denied", user_id=user.id, role=user.role,
                          required=minimum_role, path=request.path)
                return jsonify(error="No tienes permisos para esta operación"), 403

            user.last_activity_at = datetime.now(timezone.utc)
            db.session.commit()
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator
