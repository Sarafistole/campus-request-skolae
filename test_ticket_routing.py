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
        raise RuntimeError(
            "Aucun type de demande disponible pour les tests."
        )

    if len(tags) < 3:
        raise RuntimeError(
            "Il faut au moins 3 tags pour tester le routage."
        )

    student_id = student.id
    request_type_id = request_type.id

    tag_1 = tags[0]
    tag_2 = tags[1]
    tag_3 = tags[2]

    # Sauvegarde des mappings actuels afin de pouvoir les restaurer.
    original_services = {
        tag_1.id: list(tag_1.target_services or []),
        tag_2.id: list(tag_2.target_services or []),
        tag_3.id: list(tag_3.target_services or []),
    }

    # Mappings temporaires uniquement utilisés pour les tests.
    #
    # tag_1 teste le routage multi-service.
    # tag_2 partage SERVICE_TEST avec tag_1 pour tester
    # la déduplication entre plusieurs tags.
    # tag_3 ne possède aucun mapping.
    tag_1.target_services = [
        "SERVICE_TEST",
        "SERVICE_TEST_2",
    ]
    tag_2.target_services = [
        "SERVICE_TEST",
    ]
    tag_3.target_services = []

    db.session.commit()

    tag_1_id = tag_1.id
    tag_2_id = tag_2.id
    tag_3_id = tag_3.id


def create_ticket(client, tag_ids, title):
    return client.post(
        "/dashboard",
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
        # Un tag peut produire plusieurs services recommandés.
        # -----------------------------------------------------

        response = create_ticket(
            client,
            [tag_1_id],
            "TEST ROUTING 02 - multi service",
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                title="TEST ROUTING 02 - multi service"
            ).first()

            success = (
                response.status_code == 302
                and ticket is not None
                and ticket.recommended_services
                == ["SERVICE_TEST", "SERVICE_TEST_2"]
            )

            print(
                "OK" if success else "ECHEC",
                "| Multi-service              |",
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
        # Plusieurs tags ne doivent pas dupliquer un service.
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
                and ticket.recommended_services
                == ["SERVICE_TEST", "SERVICE_TEST_2"]
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
    # Les tickets de test sont supprimés avec leurs associations.
    # Les mappings temporaires des tags sont ensuite restaurés.
    # ---------------------------------------------------------

    with app.app_context():
        test_tickets = Ticket.query.filter(
            Ticket.title.like("TEST ROUTING 02%")
        ).all()

        for ticket in test_tickets:
            ticket.tags.clear()
            db.session.delete(ticket)

        for tag_id, original_service_list in original_services.items():
            tag = db.session.get(Tag, tag_id)

            if tag is not None:
                tag.target_services = original_service_list

        db.session.commit()