"""Temas/módulos de capacitación. Lectura: todos. Escritura: admin (Función 3)."""
from flask import Blueprint, jsonify, request

from ..auth.decorators import require_auth
from ..extensions import db
from ..models import Topic

bp = Blueprint("topics", __name__)


@bp.get("")
@require_auth()
def list_topics():
    query = Topic.query
    if request.args.get("include_inactive") != "1":
        query = query.filter_by(is_active=True)
    topics = query.order_by(Topic.level, Topic.name).all()
    return jsonify(items=[t.to_dict(with_counts=True) for t in topics])


@bp.post("")
@require_auth("admin")
def create_topic():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(error="name es obligatorio"), 422
    if Topic.query.filter_by(name=name).first():
        return jsonify(error="Ya existe un tema con ese nombre"), 409
    topic = Topic(name=name, description=data.get("description", ""),
                  level=int(data.get("level", 1)))
    db.session.add(topic)
    db.session.commit()
    return jsonify(topic=topic.to_dict()), 201


@bp.patch("/<int:topic_id>")
@require_auth("admin")
def update_topic(topic_id: int):
    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify(error="Tema no encontrado"), 404
    data = request.get_json(silent=True) or {}
    if "name" in data:
        topic.name = data["name"].strip()
    if "description" in data:
        topic.description = data["description"]
    if "level" in data:
        topic.level = int(data["level"])
    if "is_active" in data:
        topic.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(topic=topic.to_dict())


@bp.delete("/<int:topic_id>")
@require_auth("admin")
def deactivate_topic(topic_id: int):
    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify(error="Tema no encontrado"), 404
    topic.is_active = False
    db.session.commit()
    return jsonify(message="Tema desactivado", topic=topic.to_dict())
