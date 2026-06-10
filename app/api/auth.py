"""Autenticación.

- POST /auth/login : solo AUTH_MODE=local. En modo cognito el login lo hace
  Cognito (Hosted UI o SDK Amplify en Flutter) y este endpoint responde 400.
- GET  /auth/me    : perfil del usuario autenticado (cualquier modo).
"""
from flask import Blueprint, current_app, g, jsonify, request

from ..auth.decorators import require_auth
from ..auth.tokens import issue_local_token
from ..models import User

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    if current_app.config["AUTH_MODE"] != "local":
        return jsonify(error="El login se realiza contra AWS Cognito "
                             "(AUTH_MODE=cognito)"), 400

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email y password son obligatorios"), 422

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password) or not user.is_active:
        return jsonify(error="Credenciales inválidas"), 401

    return jsonify(access_token=issue_local_token(user),
                   user=user.to_dict(include_stats=True))


@bp.get("/me")
@require_auth()
def me():
    return jsonify(user=g.current_user.to_dict(include_stats=True))
