import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cle_de_secours_dev")

# Configuration de la base de données PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Gr0upe4ESGI")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modèle Utilisateur
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    confirmation_code = db.Column(db.String(6), nullable=True)
    is_confirmed = db.Column(db.Boolean, default=False)

# Fonction d'envoi d'e-mail via Brevo SMTP
def send_confirmation_email(recipient_email, code):
    sender = os.getenv("SMTP_SENDER")
    body = (
        f"Bonjour,\n\n"
        f"Voici votre code de validation pour finaliser votre inscription sur Campus Request : {code}\n\n"
        f"Ce code est à usage unique.\n\n"
        f"L'équipe Campus Request."
    )
    msg = MIMEText(body)
    msg['Subject'] = "Code de validation - Campus Request"
    msg['From'] = sender
    msg['To'] = recipient_email

    server_host = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
    server_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pwd = os.getenv("SMTP_PASSWORD")

    with smtplib.SMTP(server_host, server_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pwd)
        server.send_message(msg)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if not email.endswith('@myskolae.fr'):
            flash("L'adresse doit obligatoirement se terminer par @myskolae.fr", "danger")
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Cette adresse e-mail est déjà enregistrée.", "warning")
            return redirect(url_for('register'))

        code = f"{random.randint(100000, 999999)}"
        hashed_pwd = generate_password_hash(password)

        new_user = User(
            email=email,
            password_hash=hashed_pwd,
            confirmation_code=code,
            is_confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()

        try:
            send_confirmation_email(email, code)
        except Exception as e:
            print(f"Erreur d'envoi SMTP : {e}")
            flash("Erreur lors de l'envoi de l'e-mail de confirmation.", "warning")

        session['pending_email'] = email
        return redirect(url_for('confirm'))

    return render_template('register.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    email = session.get('pending_email')
    if not email:
        return redirect(url_for('register'))

    if request.method == 'POST':
        input_code = request.form.get('code', '').strip()
        user = User.query.filter_by(email=email).first()

        if user and user.confirmation_code == input_code:
            user.is_confirmed = True
            user.confirmation_code = None
            db.session.commit()
            session.pop('pending_email', None)
            flash("Compte validé avec succès. Vous pouvez vous connecter.", "success")
            return redirect(url_for('login'))
        else:
            flash("Code incorrect. Veuillez réessayer.", "danger")

    return render_template('confirm.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_confirmed:
                session['pending_email'] = email
                flash("Veuillez d'abord valider votre compte avec le code reçu.", "warning")
                return redirect(url_for('confirm'))

            session['user_id'] = user.id
            flash("Connexion réussie.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Identifiants invalides.", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
