"""Trivia Seguridad — Backend Flask.

API REST para la plataforma de capacitación gamificada (MVP).
Funciones cubiertas (ver Funciones_Guardia_Pro / COT-2026-001):
 1. Acceso por roles (guarda / supervisor / admin) — local o AWS Cognito
 2. Capacitación en formato de juego (quiz con niveles y comodines)
 3. Banco de preguntas y panel de administración (API)
 4. Puntos, insignias y rangos + tabla de posiciones
 5. Seguimiento y reportes para supervisores
 7. Datos protegidos (JWT, RBAC, listo para respaldos)
"""
import logging

from flask import Flask, jsonify
from flask_cors import CORS

from .config import WEAK_SECRETS, Config
from .extensions import db, limiter


def _check_secrets(app: Flask) -> None:
    """Falla cerrado: en producción no se permiten secretos por defecto.

    Sin esto, un JWT HS256 firmado con un secreto público del repositorio
    permitiría falsificar tokens de administrador (OWASP A02/A07)."""
    if app.config.get("TESTING"):
        return
    for key in ("SECRET_KEY", "JWT_SECRET"):
        if (app.config.get(key) or "") in WEAK_SECRETS:
            raise RuntimeError(
                f"{key} usa un valor por defecto inseguro. Define una clave "
                "aleatoria fuerte (p. ej. `python -c \"import secrets; "
                "print(secrets.token_urlsafe(48))\"`) antes de arrancar.")


def _parse_origins(raw: str) -> list[str] | str:
    origins = [o.strip() for o in (raw or "").split(",") if o.strip()]
    return "*" if origins == ["*"] else origins


def _configure_logging(app: Flask) -> None:
    if app.config.get("TESTING"):
        return
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s")


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        # API JSON: ningún recurso debe cargarse desde estas respuestas
        resp.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        resp.headers.setdefault("Cache-Control", "no-store")
        if app.config.get("HSTS_ENABLED"):
            resp.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains")
        return resp


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    _check_secrets(app)
    _configure_logging(app)

    db.init_app(app)
    CORS(app, origins=_parse_origins(app.config["CORS_ORIGINS"]))

    limiter.enabled = app.config.get("RATELIMIT_ENABLED", True)
    limiter.init_app(app)

    _register_security_headers(app)

    # --- Blueprints ---
    from .api.auth import bp as auth_bp
    from .api.users import bp as users_bp
    from .api.topics import bp as topics_bp
    from .api.questions import bp as questions_bp
    from .api.game import bp as game_bp
    from .api.gamification import bp as gamification_bp
    from .api.reports import bp as reports_bp

    prefix = "/api/v1"
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(users_bp, url_prefix=f"{prefix}/users")
    app.register_blueprint(topics_bp, url_prefix=f"{prefix}/topics")
    app.register_blueprint(questions_bp, url_prefix=f"{prefix}/questions")
    app.register_blueprint(game_bp, url_prefix=f"{prefix}/game")
    app.register_blueprint(gamification_bp, url_prefix=prefix)      # /badges, /leaderboard
    app.register_blueprint(reports_bp, url_prefix=f"{prefix}/reports")

    @app.get(f"{prefix}/health")
    def health():
        return {"status": "ok", "service": "trivia-seguridad-api"}

    # --- Errores JSON uniformes ---
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Recurso no encontrado"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Método no permitido"), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Error interno del servidor"), 500

    # --- CLI: flask init-db / flask seed ---
    from . import seeds
    app.cli.add_command(seeds.init_db_command)
    app.cli.add_command(seeds.seed_command)

    return app
