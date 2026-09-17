from app import app
from extensions import db
from models import Admin, Ticket, Service


def result(name, success, details=""):
    print(
        "OK" if success else "ECHEC",
        "|",
        f"{name:<30}",
        "|",
        details,
    )
    return success


with app.app_context():
    admin = Admin.query.first()
    ticket = Ticket.query.first()
    services = Service.query.order_by(Service.id).limit(2).all()

    if admin is None:
        raise RuntimeError(
            "Aucun administrateur disponible pour le test."
        )

    if ticket is None:
        raise RuntimeError(
            "Aucun ticket disponible pour le test."
        )

    if len(services) < 2:
        raise RuntimeError(
            "Au moins deux services sont nécessaires pour le test."
        )

    admin_id = admin.id
    public_id = ticket.public_id

    service_1_id = services[0].id
    service_2_id = services[1].id

    original_assigned_service_id = ticket.assigned_service_id
    original_recommended_services = list(
        ticket.recommended_services or []
    )


try:
    with app.test_client() as client:

        # ---------------------------------------------------------
        # 1. Administrateur non connecté
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": service_1_id},
            follow_redirects=False,
        )

        result(
            "Admin non connecte",
            response.status_code == 302,
            f"attendu=302 obtenu={response.status_code}",
        )

        # Connexion simulée de l'administrateur.
        with client.session_transaction() as session:
            session["admin_id"] = admin_id

        # ---------------------------------------------------------
        # 2. Ticket inexistant
        # ---------------------------------------------------------
        response = client.post(
            "/admin/tickets/ticket-inexistant/service",
            data={"service_id": service_1_id},
            follow_redirects=False,
        )

        result(
            "Ticket inexistant",
            response.status_code == 404,
            f"attendu=404 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # 3. Service vide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": ""},
            follow_redirects=False,
        )

        result(
            "Service vide",
            response.status_code == 400,
            f"attendu=400 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # 4. Service non numérique
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": "Direction"},
            follow_redirects=False,
        )

        result(
            "Service non numerique",
            response.status_code == 400,
            f"attendu=400 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # 5. Service inexistant
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": 999999999},
            follow_redirects=False,
        )

        result(
            "Service inexistant",
            response.status_code == 400,
            f"attendu=400 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # 6. Affectation vers un service valide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": service_1_id},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_service_id = ticket.assigned_service_id
            current_recommended = list(
                ticket.recommended_services or []
            )

        result(
            "Service valide",
            (
                response.status_code == 302
                and current_service_id == service_1_id
            ),
            (
                f"status_http={response.status_code} "
                f"service_id={current_service_id}"
            ),
        )

        # ---------------------------------------------------------
        # 7. Le routage automatique doit rester intact
        # ---------------------------------------------------------
        result(
            "Routing conserve",
            current_recommended == original_recommended_services,
            (
                f"avant={original_recommended_services} "
                f"apres={current_recommended}"
            ),
        )

        # ---------------------------------------------------------
        # 8. Réorientation vers un autre service valide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/service",
            data={"service_id": service_2_id},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_service_id = ticket.assigned_service_id
            current_recommended = list(
                ticket.recommended_services or []
            )

        result(
            "Reorientation valide",
            (
                response.status_code == 302
                and current_service_id == service_2_id
                and current_recommended
                == original_recommended_services
            ),
            (
                f"status_http={response.status_code} "
                f"service_id={current_service_id}"
            ),
        )

finally:
    # Le test ne doit pas modifier définitivement le ticket utilisé.
    with app.app_context():
        ticket = Ticket.query.filter_by(
            public_id=public_id
        ).first()

        if ticket is not None:
            ticket.assigned_service_id = original_assigned_service_id
            db.session.commit()