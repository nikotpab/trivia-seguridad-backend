from datetime import datetime, timezone

from ..extensions import db

# Puntos base por dificultad (mecánica tipo "Millonario")
DIFFICULTY_POINTS = {"facil": 100, "media": 200, "dificil": 300}


class Topic(db.Model):
    """Tema/módulo de capacitación (ej. Control de Accesos)."""
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    level = db.Column(db.Integer, nullable=False, default=1)  # nivel requerido
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    questions = db.relationship("Question", back_populates="topic", lazy="dynamic")

    def to_dict(self, with_counts: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "is_active": self.is_active,
        }
        if with_counts:
            data["question_count"] = self.questions.filter_by(is_active=True).count()
        return data


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default="media")  # facil|media|dificil
    explanation = db.Column(db.Text, default="")  # retroalimentación al responder
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))

    topic = db.relationship("Topic", back_populates="questions")
    choices = db.relationship("Choice", back_populates="question", lazy="selectin",
                              cascade="all, delete-orphan", order_by="Choice.id")

    @property
    def correct_choice(self):
        return next((c for c in self.choices if c.is_correct), None)

    def to_dict(self, include_answers: bool = False) -> dict:
        """include_answers=True solo para admin — nunca exponer al jugador."""
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "text": self.text,
            "difficulty": self.difficulty,
            "points": DIFFICULTY_POINTS.get(self.difficulty, 100),
            "is_active": self.is_active,
            "explanation": self.explanation if include_answers else None,
            "choices": [c.to_dict(include_answers) for c in self.choices],
        }

    def to_player_dict(self) -> dict:
        """Versión sanitizada para el jugador: sin marcar la correcta."""
        return {
            "id": self.id,
            "text": self.text,
            "difficulty": self.difficulty,
            "points": DIFFICULTY_POINTS.get(self.difficulty, 100),
            "choices": [{"id": c.id, "text": c.text} for c in self.choices],
        }


class Choice(db.Model):
    __tablename__ = "choices"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"),
                            nullable=False, index=True)
    text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

    question = db.relationship("Question", back_populates="choices")

    def to_dict(self, include_answers: bool = False) -> dict:
        data = {"id": self.id, "text": self.text}
        if include_answers:
            data["is_correct"] = self.is_correct
        return data
