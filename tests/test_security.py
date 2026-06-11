"""Pruebas de los controles de seguridad (hardening)."""
import secrets

import pytest

from app import create_app
from app.config import TestConfig
from app.services.report_service import _csv_safe

from .conftest import auth_header


# --- W-01: el arranque rechaza secretos por defecto ------------------------
class _InsecureConfig(TestConfig):
    TESTING = False          # desactiva el bypass del guardia
    JWT_SECRET = "dev-secret-change-me"
    SECRET_KEY = "dev-secret-change-me"


def test_startup_rejects_weak_secret():
    with pytest.raises(RuntimeError):
        create_app(_InsecureConfig)


class _SecureConfig(TestConfig):
    TESTING = False
    SECRET_KEY = "x-" + secrets.token_urlsafe(48)
    JWT_SECRET = "y-" + secrets.token_urlsafe(48)


def test_startup_accepts_strong_secret():
    assert create_app(_SecureConfig) is not None


# --- W-05: saneamiento de inyección de fórmulas en CSV ---------------------
@pytest.mark.parametrize("payload", ["=cmd|'/c calc'!A1", "+1", "-1", "@SUM(A1)"])
def test_csv_safe_neutralizes_formula(payload):
    assert _csv_safe(payload).startswith("'")


def test_csv_safe_leaves_plain_text():
    assert _csv_safe("Andrés Rojas") == "Andrés Rojas"


# --- W-06: cabeceras de seguridad ------------------------------------------
def test_security_headers_present(client):
    res = client.get("/api/v1/health")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in res.headers["Content-Security-Policy"]


# --- W-08: política de contraseñas -----------------------------------------
def test_create_user_rejects_short_password(client):
    headers = auth_header(client, "admin@test.co")
    res = client.post("/api/v1/users", headers=headers, json={
        "email": "nuevo@test.co", "full_name": "Nuevo", "password": "123"})
    assert res.status_code == 422


def test_create_user_accepts_strong_password(client):
    headers = auth_header(client, "admin@test.co")
    res = client.post("/api/v1/users", headers=headers, json={
        "email": "nuevo2@test.co", "full_name": "Nuevo Dos",
        "password": "una-clave-larga-1"})
    assert res.status_code == 201


# --- W-10: parsing robusto de entradas -------------------------------------
def test_bad_pagination_does_not_500(client):
    headers = auth_header(client, "admin@test.co")
    res = client.get("/api/v1/users?page=abc", headers=headers)
    assert res.status_code == 200
