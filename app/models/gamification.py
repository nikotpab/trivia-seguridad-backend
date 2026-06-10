from datetime import datetime, timezone

from ..extensions import db

# Escala de Mando — misma escala del boceto (js/data.js)
RANKS = [
    {"id": "recluta",    "name": "Recluta",            "threshold": 0},
    {"id": "vigilante1", "name": "Vigilante I",        "threshold": 10_000},
    {"id": "oficial1",   "name": "Oficial de Primera", "threshold": 25_000},
    {"id": "jefe",       "name": "Jefe de Turno",      "threshold": 50_000},
    {"id": "supervisor", "name": "Supervisor",         "threshold": 90_000},
]


class Badge(db.Model):
    """Catálogo de insignias. La lógica de otorgamiento vive en
    services/gamification_service.py, referenciada por `code`."""
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), default="")

    def to_dict(self) -> dict:
        return {"id": self.id, "code": self.code,
                "name": self.name, "description": self.description}


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    __table_args__ = (db.UniqueConstraint("user_id", "badge_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    awarded_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("Badge")

    def to_dict(self) -> dict:
        data = self.badge.to_dict()
        data["awarded_at"] = self.awarded_at.isoformat()
        return data
