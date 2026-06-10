"""Verificación de tokens en dos modos:

- local   : JWT HS256 emitido por este backend (/api/v1/auth/login).
            Para desarrollo y pruebas sin infraestructura AWS.
- cognito : JWT RS256 emitido por un User Pool de AWS Cognito, verificado
            contra su JWKS. El rol se toma del claim `cognito:groups` y el
            usuario se aprovisiona automáticamente en la base local.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt
from flask import current_app

from ..extensions import db
from ..models import User


class AuthError(Exception):
    def __init__(self, message: str, status: int = 401):
        super().__init__(message)
        self.message = message
        self.status = status


# ---------------------------------------------------------------- local mode
def issue_local_token(user: User) -> str:
    cfg = current_app.config
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "mode": "local",
        "iat": now,
        "exp": now + timedelta(minutes=cfg["JWT_EXPIRES_MIN"]),
    }
    return jwt.encode(payload, cfg["JWT_SECRET"], algorithm="HS256")


def _verify_local(token: str) -> User:
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET"],
                             algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expirado")
    except jwt.InvalidTokenError:
        raise AuthError("Token inválido")

    user = db.session.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise AuthError("Usuario no encontrado o inactivo")
    return user


# -------------------------------------------------------------- cognito mode
@lru_cache(maxsize=4)
def _jwks_client(region: str, user_pool_id: str) -> jwt.PyJWKClient:
    url = (f"https://cognito-idp.{region}.amazonaws.com/"
           f"{user_pool_id}/.well-known/jwks.json")
    return jwt.PyJWKClient(url, cache_keys=True)


def _verify_cognito(token: str) -> User:
    cfg = current_app.config
    region, pool = cfg["COGNITO_REGION"], cfg["COGNITO_USER_POOL_ID"]
    if not pool:
        raise AuthError("COGNITO_USER_POOL_ID no configurado", 500)

    issuer = f"https://cognito-idp.{region}.amazonaws.com/{pool}"
    try:
        signing_key = _jwks_client(region, pool).get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token, signing_key.key, algorithms=["RS256"], issuer=issuer,
            # El access token de Cognito no trae `aud`; validamos client_id abajo
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expirado")
    except jwt.PyJWTError:
        raise AuthError("Token inválido")

    client_id = cfg["COGNITO_APP_CLIENT_ID"]
    token_client = payload.get("client_id") or payload.get("aud")
    if client_id and token_client != client_id:
        raise AuthError("Token no corresponde a esta aplicación")

    return _provision_cognito_user(payload)


def _provision_cognito_user(payload: dict) -> User:
    """Crea/actualiza el usuario local a partir del token de Cognito."""
    sub = payload["sub"]
    email = payload.get("email") or payload.get("username") or f"{sub}@cognito"
    groups = payload.get("cognito:groups") or []
    role = next((g for g in ("admin", "supervisor", "guarda") if g in groups), "guarda")

    user = User.query.filter_by(cognito_sub=sub).first()
    if not user:
        user = User.query.filter_by(email=email).first()  # enlazar cuenta existente
        if user:
            user.cognito_sub = sub
        else:
            user = User(email=email, cognito_sub=sub,
                        full_name=payload.get("name", email.split("@")[0]))
            db.session.add(user)
    if not user.is_active:
        raise AuthError("Usuario inactivo")
    user.role = role  # Cognito es la fuente de verdad del rol
    db.session.commit()
    return user


# ------------------------------------------------------------------- público
def verify_token(token: str) -> User:
    mode = current_app.config["AUTH_MODE"]
    if mode == "cognito":
        return _verify_cognito(token)
    return _verify_local(token)
