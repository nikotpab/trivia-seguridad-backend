"""Registro de eventos de seguridad (Función 7 / OWASP A09).

Emite líneas estructuradas a stdout (las captura CloudWatch en producción,
ver gunicorn.conf.py). Se usa para detectar fuerza bruta, abuso de permisos
y acciones administrativas sensibles.
"""
import logging

from flask import has_request_context, request

logger = logging.getLogger("security")


def _client_ip() -> str:
    if not has_request_context():
        return "-"
    # Detrás de un proxy/ALB el cliente real viene en X-Forwarded-For
    fwd = request.headers.get("X-Forwarded-For", "")
    return fwd.split(",")[0].strip() if fwd else (request.remote_addr or "-")


def log_event(event: str, **fields) -> None:
    """Registra un evento de seguridad con campos clave=valor."""
    parts = [f"event={event}", f"ip={_client_ip()}"]
    parts += [f"{k}={v}" for k, v in fields.items() if v is not None]
    logger.info(" ".join(parts))
