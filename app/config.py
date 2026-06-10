"""Configuración central — todo se controla por variables de entorno."""
import os


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

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Reglas de juego
    GAME_DEFAULT_QUESTIONS = int(os.getenv("GAME_DEFAULT_QUESTIONS", "10"))
    GAME_MAX_QUESTIONS = int(os.getenv("GAME_MAX_QUESTIONS", "20"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # en memoria
    AUTH_MODE = "local"
    JWT_SECRET = "test-secret"
