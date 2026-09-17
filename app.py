import secrets

from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import db, migrate
from models import Student, Admin, RequestType, Tag, Ticket
from services.email_service import send_confirmation_email


app = Flask(__name__)

# Chargement de la configuration
app.config.from_object(Config)

# Connexion de SQLAlchemy à Flask
db.init_app(app)

# Connexion de Flask-Migrate à Flask et SQLAlchemy
migrate.init_app(app, db)


@app.route("/")
def home():
    return "Campus Request : WELCOME !"


@app.route("/auth")
def auth_home():
    return render_template("connexion.html")

@app.route("/choix-register")
def choix_register():
    return render_template("choix-register.html")

@app.route("/choix-auth")
def choix_auth():
    return render_template("choix-auth.html")

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "GET":
        return render_template("admin-register.html")

    return "Inscription administrateur - bientôt disponible"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # L'inscription est réservée aux adresses scolaires MySkolae.
    if not email.endswith("@myskolae.fr"):
        return render_template(
            "register.html",
            error="Veuillez utiliser votre adresse email @myskolae.fr."
        ), 400

    if len(password) < 12:
        return render_template(
            "register.html",
            error="Le mot de passe doit contenir au moins 12 caractères."
        ), 400

    student = Student.query.filter_by(email=email).first()

    if student and student.is_confirmed:
        return render_template(
            "register.html",
            error="Un compte existe déjà avec cette adresse email."
        ), 409

    confirmation_code = f"{secrets.randbelow(1_000_000):06d}"

    if student is None:
        student = Student(
            email=email,
            password_hash=generate_password_hash(password),
            confirmation_code=confirmation_code,
            is_confirmed=False,
        )
        db.session.add(student)
    else:
        # Un compte non confirmé peut recommencer son inscription.
        student.password_hash = generate_password_hash(password)
        student.confirmation_code = confirmation_code

    try:
        # On tente l'envoi avant de valider définitivement la transaction.
        send_confirmation_email(email, confirmation_code)
        db.session.commit()
    except Exception:
        db.session.rollback()

        return render_template(
            "register.html",
            error=(
                "Impossible d'envoyer le code de vérification. "
                "Veuillez réessayer plus tard."
            )
        ), 503

    session["pending_student_email"] = email

    return redirect(url_for("confirm"))


@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    email = session.get("pending_student_email")

    if not email:
        return redirect(url_for("register"))

    student = Student.query.filter_by(email=email).first()

    if student is None:
        session.pop("pending_student_email", None)
        return redirect(url_for("register"))

    if request.method == "GET":
        return render_template("confirm.html")

    submitted_code = request.form.get("confirmation_code", "").strip()

    if not secrets.compare_digest(
        submitted_code,
        student.confirmation_code or ""
    ):
        return render_template(
            "confirm.html",
            error="Code de vérification incorrect."
        ), 400

    student.is_confirmed = True
    student.confirmation_code = None
    db.session.commit()

    session.pop("pending_student_email", None)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    student = Student.query.filter_by(email=email).first()

    if student is None:
        return render_template(
            "login.html",
            error="Email ou mot de passe incorrect."
        ), 401

    if not check_password_hash(student.password_hash, password):
        return render_template(
            "login.html",
            error="Email ou mot de passe incorrect."
        ), 401

    if not student.is_confirmed:
        return render_template(
            "login.html",
            error=(
                "Veuillez confirmer votre adresse email "
                "avant de vous connecter."
            )
        ), 403

    session["student_id"] = student.id

    return redirect(url_for("home"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin-login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    admin = Admin.query.filter_by(email=email).first()

    if admin is None:
        return render_template(
            "admin-login.html",
            error="Email ou mot de passe incorrect."
        ), 401

    if not check_password_hash(admin.password_hash, password):
        return render_template(
            "admin-login.html",
            error="Email ou mot de passe incorrect."
        ), 401

    session["admin_id"] = admin.id

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    return redirect(url_for("login"))


@app.route("/test-db")
def test_db():
    try:
        db.session.execute(text("SELECT 1"))
        return "Connexion PostgreSQL OK !"
    except Exception as e:
        return f"Erreur de connexion : {e}"


@app.route("/create-tables")
def create_tables():
    db.create_all()
    return "Tables créées !"


if __name__ == "__main__":
    app.run(debug=True)