from extensions import db


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    # Service administratif recommandé pour traiter
    # les tickets associés à ce sujet.
    target_service = db.Column(
        db.String(100),
        nullable=True
    )