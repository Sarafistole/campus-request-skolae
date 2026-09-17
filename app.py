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

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    # Récupération des données nécessaires au formulaire
    request_types = RequestType.query.order_by(RequestType.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    # Envoi du formulaire
    if request.method == "POST":

        # Vérification de la connexion
        student_id = session.get("student_id")

        if not student_id:
            return redirect(url_for("login"))

        title = request.form.get("title", "").strip()
        request_type_id = request.form.get("request_type_id")
        description = request.form.get("description", "").strip()
        scope = request.form.get("scope")
        classe_personnes_concernees = request.form.get(
            "classe_personnes_concernees",
            ""
        ).strip()

        # Récupération des tags sélectionnés
        tag_ids = request.form.getlist("tag_ids")

        # Vérifications de base
        if not title or not request_type_id or not description or not scope:
            return render_template(
                "dashboard_student.html",
                request_types=request_types,
                tags=tags,
                error="Veuillez remplir tous les champs obligatoires."
            ), 400

        # Entre 1 et 5 tags
        if len(tag_ids) < 1 or len(tag_ids) > 5:
            return render_template(
                "dashboard_student.html",
                request_types=request_types,
                tags=tags,
                error="Sélectionnez entre 1 et 5 sujets."
            ), 400

        # Vérification du type de demande
        request_type = RequestType.query.get(request_type_id)

        if request_type is None:
            return render_template(
                "dashboard_student.html",
                request_types=request_types,
                tags=tags,
                error="Type de demande invalide."
            ), 400

        # Récupération des tags
        selected_tags = Tag.query.filter(
            Tag.id.in_(tag_ids)
        ).all()

        if len(selected_tags) != len(set(tag_ids)):
            return render_template(
                "dashboard_student.html",
                request_types=request_types,
                tags=tags,
                error="Un ou plusieurs sujets sont invalides."
            ), 400

        # Création du ticket
        ticket = Ticket(
            student_id=student_id,
            request_type_id=request_type.id,
            title=title,
            description=description,
            scope=scope,  # ← ajoute cette ligne
            classe_personnes_concernees=classe_personnes_concernees or None,
            status="NEW"
        )

        # Association des tags
        ticket.tags = selected_tags

        db.session.add(ticket)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template(
        "dashboard_student.html",
        request_types=request_types,
        tags=tags
    )

@app.route("/account", methods=["GET", "POST"])
def account():
    student_id = session.get("student_id")

    if not student_id:
        return redirect(url_for("login"))

    student = Student.query.get(student_id)

    if student is None:
        session.pop("student_id", None)
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not new_password or not confirm_password:
            return render_template(
                "account.html",
                student=student,
                error="Veuillez remplir les deux champs."
            ), 400

        if new_password != confirm_password:
            return render_template(
                "account.html",
                student=student,
                error="Les deux mots de passe ne correspondent pas."
            ), 400

        # Le hash du nouveau mot de passe sera ajouté ici
        # avec la méthode déjà utilisée pour les étudiants.

        student.password_hash = generate_password_hash(new_password)

        db.session.commit()

        return redirect(url_for("account"))

    return render_template("account.html", student=student)


@app.route("/history")
def history():
    student_id = session.get("student_id")

    if not student_id:
        return redirect(url_for("login"))

    tickets = (
        Ticket.query
        .filter_by(student_id=student_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return render_template(
        "history.html",
        tickets=tickets
    )

@app.route("/auth")
def auth_home():
    return render_template("connexion.html")


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


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    return redirect(url_for("login"))


@app.route("/tickets/create", methods=["GET", "POST"])
def create_ticket():
    # Un ticket doit obligatoirement appartenir à un étudiant connecté.
    student_id = session.get("student_id")

    if student_id is None:
        return redirect(url_for("login"))

    # Vérifie que l'étudiant enregistré dans la session existe toujours.
    student = db.session.get(Student, student_id)

    if student is None:
        session.pop("student_id", None)
        return redirect(url_for("login"))

    # Les données nécessaires au formulaire.
    request_types = RequestType.query.order_by(RequestType.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.method == "GET":
        return render_template(
            "create_ticket.html",
            request_types=request_types,
            tags=tags
        )

    # Récupération et normalisation des données du formulaire.
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    request_type_id = request.form.get("request_type_id", type=int)
    scope = request.form.get("scope", "").strip().upper()
    precision = request.form.get(
        "classe_personnes_concernees",
        ""
    ).strip()

    # getlist permet de recevoir plusieurs tags depuis le formulaire.
    tag_ids_raw = request.form.getlist("tag_ids")

    # Suppression des doublons tout en conservant l'ordre.
    try:
        tag_ids = list(dict.fromkeys(int(tag_id) for tag_id in tag_ids_raw))
    except (TypeError, ValueError):
        return "Sélection de tags invalide.", 400

    # Validation du titre.
    if not title:
        return "Le titre est obligatoire.", 400

    if len(title) > 255:
        return "Le titre ne peut pas dépasser 255 caractères.", 400

    # Validation de la description.
    if not description:
        return "La description est obligatoire.", 400

    if len(description) > 5000:
        return "La description ne peut pas dépasser 5000 caractères.", 400
    
    # Validation du type de demande.
    if request_type_id is None:
        return "Le type de demande est obligatoire.", 400

    request_type = db.session.get(RequestType, request_type_id)

    if request_type is None:
        return "Type de demande invalide.", 400

    # Validation de la personne / du groupe concerné.
    allowed_scopes = {"SELF", "INDIVIDUAL", "GROUP"}

    if scope not in allowed_scopes:
        return "Personne(s) concernée(s) invalide(s).", 400

    # La précision reste facultative.
    if len(precision) > 255:
        return "La précision ne peut pas dépasser 255 caractères.", 400

    # Entre 1 et 5 sujets/services doivent être sélectionnés.
    if not 1 <= len(tag_ids) <= 5:
        return "Vous devez sélectionner entre 1 et 5 sujets/services.", 400

    selected_tags = db.session.execute(
        db.select(Tag).where(Tag.id.in_(tag_ids))
    ).scalars().all()

    # Empêche l'envoi d'identifiants de tags inexistants.
    if len(selected_tags) != len(tag_ids):
        return "Un ou plusieurs sujets/services sont invalides.", 400

    ticket = Ticket(
        student_id=student_id,
        request_type_id=request_type.id,
        title=title,
        description=description,
        scope=scope,
        classe_personnes_concernees=precision or None,
        tags=selected_tags
    )

    db.session.add(ticket)
    db.session.commit()

    return redirect(url_for("home"))


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