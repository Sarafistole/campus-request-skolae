from datetime import datetime
import uuid

from extensions import db


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

    # Identifiant public utilisé dans les vues/routes
    public_id = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # Auteur connu en interne, mais à ne pas exposer aux admins
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

    # Contenu principal du ticket
    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    # Classe et/ou personne(s) concernée(s) - champ facultatif
    classe_personnes_concernees = db.Column(
        db.String(255),
        nullable=True
    )

    # Statut du ticket
    status = db.Column(
        db.String(50),
        nullable=False,
        default="NEW"
    )

    # Dates de création et de dernière modification
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Service/Sujet du ticket
    tags = db.relationship(
        "Tag",
        secondary=ticket_tags,
        backref="tickets"
    )