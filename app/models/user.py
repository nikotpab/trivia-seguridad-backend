from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db

ROLES = ("guarda", "supervisor", "admin")
# Jerarquía: un rol superior puede hacer todo lo del inferior
ROLE_ORDER = {"guarda": 0, "supervisor": 1, "admin": 2}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="guarda")
    # Hash local (AUTH_MODE=local). En modo Cognito puede ser NULL.
    password_hash = db.Column(db.String(255), nullable=True)
    # 'sub' del token de Cognito — enlaza la identidad externa
    cognito_sub = db.Column(db.String(64), unique=True, nullable=True, index=True)

    total_points = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    last_activity_at = db.Column(db.DateTime, nullable=True)

    sessions = db.relationship("GameSession", back_populates="user", lazy="dynamic")
    badges = db.relationship("UserBadge", back_populates="user", lazy="selectin",
                             cascade="all, delete-orphan")

    # --- password (solo modo local) ---
    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, raw)

    def has_role(self, minimum: str) -> bool:
        return ROLE_ORDER[self.role] >= ROLE_ORDER[minimum]

    def to_dict(self, include_stats: bool = False) -> dict:
        data = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "total_points": self.total_points,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            from ..services.gamification_service import rank_info
            data["rank"] = rank_info(self.total_points)
            data["badges"] = [ub.to_dict() for ub in self.badges]
        return data
