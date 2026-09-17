from app import app
from extensions import db
from models import RequestType, Tag


REQUEST_TYPES = [
    "Signaler",
    "Questions-Renseignements",
    "Proposer",
]

TAG_ROUTING = {
    "Harcèlement": ["Direction", "Pédagogie"],
    "Dégradation matériel": ["Maintenance matériel"],
    "Vol": ["Direction"],
    "Planning": ["Planning"],
    "BDE": ["BDE"],
    "Événement": ["Communication", "BDE"],
    "Clubs & Associations": ["BDE"],
    "Entretien des locaux": ["Direction"],
    "Accessibilité": ["Direction"],

    "Alternance": ["Relation Entreprise"],
    "Entreprise": ["Relation Entreprise"],

    "Absence": ["Scolarité"],
    "Notes & Examens": ["Scolarité", "Pédagogie"],

    "Formation": ["Pédagogie"],
    "Cours & Contenu pédagogique": ["Pédagogie"],
    "Intervenant": ["Planning", "Pédagogie"],
    "E-Learning": ["Pédagogie"],

    "Inscription": ["Admissions"],
    "Paiement / facturation": ["Admissions"],

    "Réseaux sociaux": ["Communication"],

    "Accès numérique": ["Informatique"],
    "Matériel informatique": [
        "Maintenance matériel",
        "Informatique",
    ],
    "Prêt / location de matériel": ["Maintenance matériel"],

    "Vie étudiante": ["BDE"],

    # Routage initial par défaut.
    # Un modérateur pourra ensuite reclassifier la demande.
    "Autre / Non catégorisé": ["Direction"],
}


with app.app_context():

    # Initialisation des natures de demande
    for name in REQUEST_TYPES:
        existing_type = RequestType.query.filter_by(name=name).first()

        if existing_type is None:
            db.session.add(RequestType(name=name))

    # Initialisation et mise à jour du routage des sujets.
    for name, target_services in TAG_ROUTING.items():
        existing_tag = Tag.query.filter_by(name=name).first()

        if existing_tag is None:
            db.session.add(
                Tag(
                    name=name,
                    target_services=target_services,
                )
            )
        else:
            existing_tag.target_services = target_services

    db.session.commit()

    print("Données de référence initialisées.")