from app import app
from models import Student, Tag


def run_test(name, client, data, expected_status):
    response = client.post(
        "/dashboard",
        data=data,
        follow_redirects=False
    )

    result = "OK" if response.status_code == expected_status else "ECHEC"

    print(
        f"{result:5} | {name:25} | "
        f"attendu={expected_status} obtenu={response.status_code}"
    )


with app.app_context():
    student = Student.query.first()
    tags = Tag.query.order_by(Tag.id).all()

    if student is None:
        raise RuntimeError("Aucun étudiant disponible pour les tests.")

    if len(tags) < 6:
        raise RuntimeError("Il faut au moins 6 tags pour tester la limite.")

    student_id = student.id
    tag_ids = [str(tag.id) for tag in tags]


with app.test_client() as client:

    # ---------------------------------------------------------
    # 1. Utilisateur non connecté
    # ---------------------------------------------------------
    response = client.get(
        "/dashboard",
        follow_redirects=False
    )

    print(
        "OK" if response.status_code == 302 else "ECHEC",
        "| Non connecté              |",
        f"attendu=302 obtenu={response.status_code}"
    )

    # ---------------------------------------------------------
    # Création d'une session étudiant valide pour les tests
    # ---------------------------------------------------------
    with client.session_transaction() as session:
        session["student_id"] = student_id

    valid_data = {
        "title": "Ticket de validation",
        "description": "Description suffisamment complète pour le test.",
        "request_type_id": "1",
        "scope": "SELF",
        "tag_ids": [tag_ids[0]]
    }

    # ---------------------------------------------------------
    # 2. Titre vide
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = ""

    run_test(
        "Titre vide",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 3. Titre trop long
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = "A" * 256

    run_test(
        "Titre > 255",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 4. Description vide
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = ""

    run_test(
        "Description vide",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 5. Description trop longue
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = "A" * 5001

    run_test(
        "Description > 5000",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 6. Type de demande inexistant
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["request_type_id"] = "999999"

    run_test(
        "RequestType inexistant",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 7. Scope invalide
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["scope"] = "INVALID"

    run_test(
        "Scope invalide",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 8. Aucun tag
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["tag_ids"] = []

    run_test(
        "0 tag",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 9. Plus de 5 tags
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["tag_ids"] = tag_ids[:6]

    run_test(
        "6 tags",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 10. Tag inexistant
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["tag_ids"] = ["999999"]

    run_test(
        "Tag inexistant",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 11. Titre composé uniquement de ponctuation
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = "???????"

    run_test(
        "Titre ponctuation",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 12. Titre trop court
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = "abc"

    run_test(
        "Titre trop court",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 13. Titre composé de caractères répétés
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = "aaaaaaaaaa"

    run_test(
        "Titre répétitif",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 14. Titre composé uniquement d'espaces
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["title"] = "       "

    run_test(
        "Titre espaces",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 15. Description composée uniquement d'espaces
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = " " * 100

    run_test(
        "Description espaces",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 16. Description trop courte
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = "Texte trop court"

    run_test(
        "Description trop courte",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 17. Description composée uniquement de ponctuation
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = "?" * 100

    run_test(
        "Description ponctuation",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 18. Description répétitive
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = "ab" * 20

    run_test(
        "Description répétitive",
        client,
        data,
        400
    )

    # ---------------------------------------------------------
    # 19. Description avec témoignage sensible mais exploitable
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = (
        "Un étudiant m'a insulté et harcelé à plusieurs reprises. "
        "Je souhaite signaler les faits et obtenir de l'aide."
    )

    run_test(
        "Témoignage sensible",
        client,
        data,
        302
    )

    # ---------------------------------------------------------
    # 20. Description valide
    # ---------------------------------------------------------
    data = valid_data.copy()
    data["description"] = (
        "Depuis plusieurs semaines, je rencontre des difficultés "
        "avec mon emploi du temps. Je souhaite obtenir de l'aide "
        "pour trouver une solution adaptée à ma situation."
    )

    run_test(
        "Description valide",
        client,
        data,
        302
    )

    # ---------------------------------------------------------
    # 21. Session avec étudiant inexistant
    # ---------------------------------------------------------
    with client.session_transaction() as session:
        session["student_id"] = 999999

    response = client.get(
        "/dashboard",
        follow_redirects=False
    )

    print(
        "OK" if response.status_code == 302 else "ECHEC",
        "| Session étudiant invalide |",
        f"attendu=302 obtenu={response.status_code}"
    )