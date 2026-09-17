from datetime import datetime
from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # Code temporaire envoyé par email lors de l'inscription
    confirmation_code = db.Column(
        db.String(6),
        nullable=True
    )

    # Indique si l'adresse email de l'étudiant a été vérifiée
    is_confirmed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )