from app import app
from extensions import db
from models import Student, RequestType, Tag, Ticket


with app.app_context():
    student = Student.query.first()
    request_type = RequestType.query.first()
    tags = Tag.query.order_by(Tag.id).limit(3).all()

    if student is None:
        raise RuntimeError("Aucun étudiant disponible pour les tests.")

    if request_type is None:
        raise RuntimeError("Aucun type de demande disponible pour les tests.")

    if len(tags) < 3:
        raise RuntimeError("Il faut au moins 3 tags pour tester le routage.")

    student_id = student.id
    request_type_id = request_type.id

    tag_1 = tags[0]
    tag_2 = tags[1]
    tag_3 = tags[2]

    # Sauvegarde des mappings actuels afin de pouvoir les restaurer.
    original_services = {
        tag_1.id: tag_1.target_service,
        tag_2.id: tag_2.target_service,
        tag_3.id: tag_3.target_service,
    }

    # Mapping temporaire uniquement utilisé pour les tests.
    tag_1.target_service = "SERVICE_TEST"
    tag_2.target_service = "SERVICE_TEST"
    tag_3.target_service = None

    db.session.commit()

    tag_1_id = tag_1.id
    tag_2_id = tag_2.id
    tag_3_id = tag_3.id


def create_ticket(client, tag_ids, title):
    return client.post(
        "/tickets/create",
        data={
            "title": title,
            "description": "Description utilisée pour tester ROUTING-02.",
            "request_type_id": str(request_type_id),
            "scope": "SELF",
            "tag_ids": [str(tag_id) for tag_id in tag_ids],
        },
        follow_redirects=False,
    )


try:
    with app.test_client() as client:

        # Session étudiant valide.
        with client.session_transaction() as session:
            session["student_id"] = student_id

        # -----------------------------------------------------
        # TEST 1
        # Un tag connu doit produire son service recommandé.
        # -----------------------------------------------------

        response = create_ticket(
            client,
            [tag_1_id],
            "TEST ROUTING 02 - mapping connu",
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                title="TEST ROUTING 02 - mapping connu"
            ).first()

            success = (
                response.status_code == 302
                and ticket is not None
                and ticket.recommended_services == ["SERVICE_TEST"]
            )

            print(
                "OK" if success else "ECHEC",
                "| Mapping connu              |",
                f"status={response.status_code}",
                f"routing={ticket.recommended_services if ticket else None}",
            )

        # -----------------------------------------------------
        # TEST 2
        # L'absence de mapping ne doit pas bloquer le ticket.
        # -----------------------------------------------------

        response = create_ticket(
            client,
            [tag_3_id],
            "TEST ROUTING 02 - sans mapping",
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                title="TEST ROUTING 02 - sans mapping"
            ).first()

            success = (
                response.status_code == 302
                and ticket is not None
                and ticket.recommended_services == []
            )

            print(
                "OK" if success else "ECHEC",
                "| Aucun mapping              |",
                f"status={response.status_code}",
                f"routing={ticket.recommended_services if ticket else None}",
            )

        # -----------------------------------------------------
        # TEST 3
        # Deux tags vers le même service doivent être dédupliqués.
        # -----------------------------------------------------

        response = create_ticket(
            client,
            [tag_1_id, tag_2_id],
            "TEST ROUTING 02 - deduplication",
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                title="TEST ROUTING 02 - deduplication"
            ).first()

            success = (
                response.status_code == 302
                and ticket is not None
                and ticket.recommended_services == ["SERVICE_TEST"]
            )

            print(
                "OK" if success else "ECHEC",
                "| Déduplication              |",
                f"status={response.status_code}",
                f"routing={ticket.recommended_services if ticket else None}",
            )

finally:
    # ---------------------------------------------------------
    # Nettoyage
    # ---------------------------------------------------------
    # Les tickets sont supprimés via l'ORM afin que SQLAlchemy
    # nettoie d'abord leurs associations dans ticket_tags.
    # Les mappings temporaires des tags sont ensuite restaurés.
    # ---------------------------------------------------------

    with app.app_context():
        test_tickets = Ticket.query.filter(
            Ticket.title.like("TEST ROUTING 02%")
        ).all()

        for ticket in test_tickets:
            # Supprime explicitement les associations ticket_tags
            # avant de supprimer le ticket.
            ticket.tags.clear()
            db.session.delete(ticket)

        for tag_id, original_service in original_services.items():
            tag = db.session.get(Tag, tag_id)

            if tag is not None:
                tag.target_service = original_service

        db.session.commit()