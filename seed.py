from app import app
from extensions import db
from models import RequestType, Tag, Service


REQUEST_TYPES = [
    "Signaler",
    "Questions-Renseignements",
    "Proposer",
]


# Référentiel des services administratifs.
# Les adresses en .test sont volontairement fictives
# et devront être remplacées par les adresses réelles.
SERVICES = {
    "BDE": "bde@example.test",
    "Scolarité": "scolarite@example.test",
    "Pédagogie": "pedagogie@example.test",
    "Planning": "planning@example.test",
    "Relation Entreprise": "relation-entreprise@example.test",
    "Admissions": "admissions@example.test",
    "Communication": "communication@example.test",
    "Direction": "direction@example.test",
    "Informatique": "informatique@example.test",
    "Maintenance matériel": "maintenance-materiel@example.test",
}


# Référentiel des sujets et de leur routage automatique.
# Un même sujet peut recommander plusieurs services.
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

    # Initialisation des natures de demande.
    for name in REQUEST_TYPES:
        existing_type = RequestType.query.filter_by(name=name).first()

        if existing_type is None:
            db.session.add(
                RequestType(name=name)
            )

    # Initialisation et mise à jour du référentiel des services.
    for name, email in SERVICES.items():
        existing_service = Service.query.filter_by(name=name).first()

        if existing_service is None:
            db.session.add(
                Service(
                    name=name,
                    email=email,
                )
            )
        else:
            existing_service.email = email

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