from extensions import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )