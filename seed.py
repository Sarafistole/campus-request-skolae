from app import app
from extensions import db
from models import RequestType, Tag


REQUEST_TYPES = [
    "Signaler",
    "Questions-Renseignements",
    "Proposer",
]

TAGS = [
    "Harcèlement",
    "Dégradation matériel",
    "Vol",
    "Planning",
    "BDE",
    "Événement",
    "Clubs & Associations",
    "Entretien des locaux",
    "Accessibilité",
]


with app.app_context():

    # Initialisation des natures de demande
    for name in REQUEST_TYPES:
        existing_type = RequestType.query.filter_by(name=name).first()

        if existing_type is None:
            db.session.add(RequestType(name=name))

    # Initialisation des services / sujets
    for name in TAGS:
        existing_tag = Tag.query.filter_by(name=name).first()

        if existing_tag is None:
            db.session.add(Tag(name=name))

    db.session.commit()

    print("Données de référence initialisées.")