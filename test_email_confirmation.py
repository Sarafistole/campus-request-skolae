from app import app
from extensions import db
from models import Student


TEST_EMAIL = "test-confirmation@myskolae.fr"
TEST_CODE = "123456"


def get_test_student():
    return Student.query.filter_by(email=TEST_EMAIL).first()


def reset_student():
    student = get_test_student()

    if student is None:
        student = Student(
            email=TEST_EMAIL,
            password_hash="TEST_ONLY",
            is_confirmed=False,
            confirmation_code=TEST_CODE,
        )
        db.session.add(student)
    else:
        student.is_confirmed = False
        student.confirmation_code = TEST_CODE

    db.session.commit()

    return student


def cleanup():
    student = get_test_student()

    if student is None:
        return

    # Sécurité : le script ne supprime que son compte de test dédié.
    if student.email != "test-confirmation@myskolae.fr":
        raise RuntimeError(
            "Sécurité : refus de supprimer un étudiant réel."
        )

    db.session.delete(student)
    db.session.commit()


def print_result(name, condition, details=""):
    status = "OK" if condition else "ERREUR"

    if details:
        print(f"{status} | {name:<32} | {details}")
    else:
        print(f"{status} | {name}")

    return condition


with app.app_context():
    client = app.test_client()
    results = []

    try:
        # ---------------------------------------------------------
        # 1. Confirmation directe avec une URL valide
        # ---------------------------------------------------------
        reset_student()

        response = client.get(
            "/confirm",
            query_string={
                "email": TEST_EMAIL,
                "code": TEST_CODE,
            },
        )

        db.session.expire_all()
        student = get_test_student()

        results.append(
            print_result(
                "URL valide",
                (
                    response.status_code == 302
                    and student.is_confirmed is True
                    and student.confirmation_code is None
                ),
                (
                    f"status={response.status_code} "
                    f"confirmed={student.is_confirmed}"
                ),
            )
        )

        # ---------------------------------------------------------
        # 2. Confirmation directe avec un code URL invalide
        # ---------------------------------------------------------
        reset_student()

        response = client.get(
            "/confirm",
            query_string={
                "email": TEST_EMAIL,
                "code": "999999",
            },
        )

        db.session.expire_all()
        student = get_test_student()

        results.append(
            print_result(
                "URL invalide",
                (
                    response.status_code == 400
                    and student.is_confirmed is False
                    and student.confirmation_code == TEST_CODE
                ),
                (
                    f"status={response.status_code} "
                    f"confirmed={student.is_confirmed}"
                ),
            )
        )

        # ---------------------------------------------------------
        # 3. Confirmation manuelle avec un code valide
        # ---------------------------------------------------------
        reset_student()

        with client.session_transaction() as session:
            session["pending_student_email"] = TEST_EMAIL

        response = client.post(
            "/confirm",
            data={
                "confirmation_code": TEST_CODE,
            },
        )

        db.session.expire_all()
        student = get_test_student()

        results.append(
            print_result(
                "Code manuel valide",
                (
                    response.status_code == 302
                    and student.is_confirmed is True
                    and student.confirmation_code is None
                ),
                (
                    f"status={response.status_code} "
                    f"confirmed={student.is_confirmed}"
                ),
            )
        )

        # ---------------------------------------------------------
        # 4. Confirmation manuelle avec un code invalide
        # ---------------------------------------------------------
        reset_student()

        with client.session_transaction() as session:
            session["pending_student_email"] = TEST_EMAIL

        response = client.post(
            "/confirm",
            data={
                "confirmation_code": "999999",
            },
        )

        db.session.expire_all()
        student = get_test_student()

        results.append(
            print_result(
                "Code manuel invalide",
                (
                    response.status_code == 400
                    and student.is_confirmed is False
                    and student.confirmation_code == TEST_CODE
                ),
                (
                    f"status={response.status_code} "
                    f"confirmed={student.is_confirmed}"
                ),
            )
        )

    finally:
        cleanup()

    if not all(results):
        raise SystemExit(1)