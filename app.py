import os
import json
import random
import urllib.request
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cle_par_defaut')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_code = db.Column(db.String(6), nullable=True)

def send_confirmation_email(destinataire, code):
    api_key = os.getenv('BREVO_API_KEY')
    sender = os.getenv('SMTP_SENDER', 'campusrequest.skolae@gmail.com')
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"email": sender, "name": "Campus Request"},
        "to": [{"email": destinataire}],
        "subject": "Code de validation - Campus Request",
        "htmlContent": f"""
            <h2>Bienvenue sur Campus Request</h2>
            <p>Voici votre code de validation à 6 chiffres :</p>
            <h1 style='color: #003366; letter-spacing: 4px;'>{code}</h1>
            <p>Ce code est requis pour activer votre compte.</p>
        """
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status in (200, 201)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email.endswith('@myskolae.fr'):
            flash('Seules les adresses @myskolae.fr sont autorisées.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cette adresse email est déjà utilisée.', 'danger')
            return redirect(url_for('register'))

        code = f"{random.randint(100000, 999999)}"
        hashed_password = generate_password_hash(password)

        new_user = User(
            email=email,
            password=hashed_password,
            confirmation_code=code,
            is_confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()

        try:
            send_confirmation_email(email, code)
            session['pending_email'] = email
            flash('Un code de confirmation vous a été envoyé par email.', 'info')
            return redirect(url_for('confirm'))
        except Exception as e:
            flash(f"Erreur lors de l'envoi de l'email : {e}", 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    email = session.get('pending_email')
    if not email:
        return redirect(url_for('register'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        user = User.query.filter_by(email=email).first()

        if user and user.confirmation_code == code:
            user.is_confirmed = True
            user.confirmation_code = None
            db.session.commit()
            session.pop('pending_email', None)
            flash('Compte validé avec succès ! Vous pouvez vous connecter.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Code invalide. Veuillez réessayer.', 'danger')

    return render_template('confirm.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Identifiants incorrects.', 'danger')
            return redirect(url_for('login'))

        if not user.is_confirmed:
            session['pending_email'] = user.email
            flash('Veuillez d abord valider votre compte avec le code reçu par email.', 'warning')
            return redirect(url_for('confirm'))

        session['user_id'] = user.id
        session['user_email'] = user.email
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Connexion requise.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', email=session.get('user_email'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
