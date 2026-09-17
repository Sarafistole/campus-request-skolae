from app import app
from extensions import db
from models import Admin, Ticket


def result(name, success, details=""):
    print(
        "OK" if success else "ECHEC",
        "|",
        f"{name:<28}",
        "|",
        details,
    )
    return success


with app.app_context():
    admin = Admin.query.first()
    ticket = Ticket.query.first()

    if admin is None:
        raise RuntimeError(
            "Aucun administrateur disponible pour le test."
        )

    if ticket is None:
        raise RuntimeError(
            "Aucun ticket disponible pour le test."
        )

    admin_id = admin.id
    public_id = ticket.public_id
    original_status = ticket.status


try:
    with app.test_client() as client:

        # ---------------------------------------------------------
        # 1. Administrateur non connecté
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "IN_PROGRESS"},
            follow_redirects=False,
        )

        result(
            "Admin non connecte",
            response.status_code == 302,
            f"attendu=302 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # Connexion simulée de l'administrateur
        # ---------------------------------------------------------
        with client.session_transaction() as session:
            session["admin_id"] = admin_id

        # ---------------------------------------------------------
        # 2. Ticket inexistant
        # ---------------------------------------------------------
        response = client.post(
            "/admin/tickets/ticket-inexistant/status",
            data={"status": "IN_PROGRESS"},
            follow_redirects=False,
        )

        result(
            "Ticket inexistant",
            response.status_code == 404,
            f"attendu=404 obtenu={response.status_code}",
        )

        # ---------------------------------------------------------
        # 3. Statut valide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "IN_PROGRESS"},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_status = ticket.status

        result(
            "Statut valide",
            (
                response.status_code == 302
                and current_status == "IN_PROGRESS"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

        # ---------------------------------------------------------
        # 4. Statut falsifié / invalide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "SUPPRIME_TOUT"},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_status = ticket.status

        result(
            "Statut invalide",
            (
                response.status_code == 400
                and current_status == "IN_PROGRESS"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

        # ---------------------------------------------------------
        # 5. Résolu
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "RESOLVED"},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_status = ticket.status

        result(
            "Statut RESOLVED",
            (
                response.status_code == 302
                and current_status == "RESOLVED"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

        # ---------------------------------------------------------
        # 6. Classé sans suite
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "DISMISSED"},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()

            current_status = ticket.status

        result(
            "Statut DISMISSED",
            (
                response.status_code == 302
                and current_status == "DISMISSED"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

        # ---------------------------------------------------------
        # 7. Transmis
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": "FORWARDED"},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()
            current_status = ticket.status

        result(
            "Statut FORWARDED",
            (
                response.status_code == 302
                and current_status == "FORWARDED"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

        # ---------------------------------------------------------
        # 8. Statut vide
        # ---------------------------------------------------------
        response = client.post(
            f"/admin/tickets/{public_id}/status",
            data={"status": ""},
            follow_redirects=False,
        )

        with app.app_context():
            ticket = Ticket.query.filter_by(
                public_id=public_id
            ).first()
            current_status = ticket.status

        result(
            "Statut vide",
            (
                response.status_code == 400
                and current_status == "FORWARDED"
            ),
            (
                f"status_http={response.status_code} "
                f"status_bdd={current_status}"
            ),
        )

finally:
    # Le test ne doit pas modifier définitivement le ticket utilisé.
    with app.app_context():
        ticket = Ticket.query.filter_by(
            public_id=public_id
        ).first()

        if ticket is not None:
            ticket.status = original_status
            db.session.commit()