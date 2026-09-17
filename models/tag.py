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

    # Services administratifs recommandés pour traiter
    # les tickets associés à ce sujet.
    #
    # Un même sujet peut être routé vers plusieurs services.
    # Exemple :
    # ["Direction", "Pédagogie"]
    target_services = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )