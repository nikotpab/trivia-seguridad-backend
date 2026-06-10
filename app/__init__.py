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
from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"].split(","))

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
