from datetime import datetime
import uuid

from extensions import db


# Table d'association entre les tickets et leurs tags.
# Un ticket peut posséder plusieurs tags et un tag peut être
# associé à plusieurs tickets.
ticket_tags = db.Table(
    "ticket_tags",
    db.Column(
        "ticket_id",
        db.Integer,
        db.ForeignKey("tickets.id"),
        primary_key=True
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True
    ),
)


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Identifiant public utilisé dans les vues/routes.
    # L'identifiant interne numérique ne doit pas être exposé.
    public_id = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # Auteur connu en interne, mais à ne pas exposer aux admins.
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    # Nature obligatoire :
    # Signaler / Questions-Renseignements / Proposer
    request_type_id = db.Column(
        db.Integer,
        db.ForeignKey("request_types.id"),
        nullable=False
    )

    request_type = db.relationship(
        "RequestType",
        backref="tickets"
    )

    # Contenu principal du ticket.
    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    # Personne(s) concernée(s) par la demande.
    # Valeurs autorisées :
    # SELF / INDIVIDUAL / GROUP
    scope = db.Column(
        db.String(20),
        nullable=False
    )

    # Services administratifs recommandés par le routage automatique.
    # Cette liste est calculée à partir des target_services
    # des tags sélectionnés lors de la création du ticket.
    #
    # Exemple :
    # ["Scolarité", "Vie étudiante"]
    #
    # Le résultat est enregistré sur le ticket afin de permettre
    # une correction manuelle ultérieure par un modérateur
    # sans modifier le mapping général des tags.
    recommended_services = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    # Classe et/ou personne(s) concernée(s).
    # Cette précision est facultative.
    classe_personnes_concernees = db.Column(
        db.String(255),
        nullable=True
    )

    # Statut du ticket.
    status = db.Column(
        db.String(50),
        nullable=False,
        default="NEW"
    )

    # Dates de création et de dernière modification.
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Services/Sujets sélectionnés par l'étudiant.
    # Entre 1 et 5 tags sont autorisés par la route de création.
    tags = db.relationship(
        "Tag",
        secondary=ticket_tags,
        backref="tickets"
    )