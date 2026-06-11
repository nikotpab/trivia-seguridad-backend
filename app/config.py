"""Configuración central — todo se controla por variables de entorno."""
import os


# Valores de marcador que NUNCA deben usarse en producción. El arranque
# (create_app) se aborta si SECRET_KEY/JWT_SECRET conservan uno de estos.
WEAK_SECRETS = frozenset({
    "", "dev-secret-change-me", "solo-desarrollo-local",
    "cambia-esto-en-produccion", "cambia-esto-tambien", "test-secret",
})


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///trivia.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Autenticación: "local" (JWT propio, desarrollo) o "cognito" (producción)
    AUTH_MODE = os.getenv("AUTH_MODE", "local")
    JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "480"))

    # AWS Cognito (solo AUTH_MODE=cognito)
    COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
    COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID", "")

    # CORS: lista de orígenes separados por coma. Por defecto solo orígenes de
    # desarrollo local; en producción se fija a los dominios reales del front.
    CORS_ORIGINS = os.getenv("CORS_ORIGINS",
                             "http://localhost:3000,http://localhost:8080")

    # Rate limiting (anti fuerza bruta). En producción usar Redis:
    #   RATELIMIT_STORAGE_URI=redis://host:6379
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "1") == "1"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5 per minute")

    # Política de contraseñas (modo local)
    MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))

    # Cabeceras de seguridad / HSTS (HSTS solo tiene efecto sobre HTTPS)
    HSTS_ENABLED = os.getenv("HSTS_ENABLED", "1") == "1"

    # Reglas de juego
    GAME_DEFAULT_QUESTIONS = int(os.getenv("GAME_DEFAULT_QUESTIONS", "10"))
    GAME_MAX_QUESTIONS = int(os.getenv("GAME_MAX_QUESTIONS", "20"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # en memoria
    AUTH_MODE = "local"
    JWT_SECRET = "test-secret"
    RATELIMIT_ENABLED = False  # las pruebas hacen muchos logins seguidos
