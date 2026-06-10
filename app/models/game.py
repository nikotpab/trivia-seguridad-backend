from datetime import datetime, timezone

from ..extensions import db

SESSION_STATUS = ("active", "finished", "abandoned")
LIFELINES = ("fifty_fifty", "skip")


class GameSession(db.Model):
    """Una partida/misión: N preguntas de un tema, validadas en servidor."""
    __tablename__ = "game_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    status = db.Column(db.String(12), nullable=False, default="active")

    # Orden de preguntas elegido por el servidor (anti-trampa)
    question_ids = db.Column(db.JSON, nullable=False, default=list)
    current_index = db.Column(db.Integer, nullable=False, default=0)

    score = db.Column(db.Integer, nullable=False, default=0)
    correct_count = db.Column(db.Integer, nullable=False, default=0)
    streak = db.Column(db.Integer, nullable=False, default=0)       # racha actual
    best_streak = db.Column(db.Integer, nullable=False, default=0)  # mejor racha de la partida
    lifelines_used = db.Column(db.JSON, nullable=False, default=dict)

    started_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="sessions")
    topic = db.relationship("Topic")
    answers = db.relationship("SessionAnswer", back_populates="session",
                              lazy="selectin", cascade="all, delete-orphan")

    @property
    def total_questions(self) -> int:
        return len(self.question_ids or [])

    @property
    def is_finished(self) -> bool:
        return self.status != "active"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "status": self.status,
            "current_index": self.current_index,
            "total_questions": self.total_questions,
            "score": self.score,
            "correct_count": self.correct_count,
            "streak": self.streak,
            "best_streak": self.best_streak,
            "lifelines_used": self.lifelines_used or {},
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class SessionAnswer(db.Model):
    __tablename__ = "session_answers"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("game_sessions.id"),
                           nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"),
                            nullable=False, index=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"), nullable=True)
    # True/False = respondida; NULL = saltada con comodín
    is_correct = db.Column(db.Boolean, nullable=True)
    points_awarded = db.Column(db.Integer, nullable=False, default=0)
    answered_at = db.Column(db.DateTime, nullable=False,
                            default=lambda: datetime.now(timezone.utc))

    session = db.relationship("GameSession", back_populates="answers")
    question = db.relationship("Question")
