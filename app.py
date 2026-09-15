import os
import random
from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

db_user = os.getenv("DB_USER")
db_pwd = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    confirmation_code = db.Column(db.String(6), nullable=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return f"""
        <h1>Bienvenue {current_user.email} !</h1>
        <p><a href="/protected">Espace membre</a> | <a href="/logout">Se déconnecter</a></p>
        """
    return """
    <h1>Portail Étudiant Skolae</h1>
    <p><a href="/login">Connexion</a> | <a href="/register">Inscription</a></p>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not email.endswith('@myskolae.fr'):
            return "Seules les adresses @myskolae.fr sont autorisées. <a href='/register'>Réessayer</a>"

        if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none():
            return "Adresse déjà inscrite. <a href='/register'>Réessayer</a>"

        hashed_pwd = generate_password_hash(password)
        code = str(random.randint(100000, 999999))

        new_user = User(email=email, password_hash=hashed_pwd, confirmation_code=code, is_confirmed=False)
        db.session.add(new_user)
        db.session.commit()

        session['pending_email'] = email
        return redirect(url_for('confirm'))

    return """
    <h2>Inscription Skolae</h2>
    <form method="POST">
        Email : <input type="email" name="email" required><br><br>
        Mot de passe : <input type="password" name="password" required><br><br>
        <button type="submit">Recevoir le code</button>
    </form>
    """

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    email = session.get('pending_email')
    if not email:
        return redirect(url_for('register'))

    if request.method == 'POST':
        entered_code = request.form['code'].strip()
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

        if user and user.confirmation_code == entered_code:
            user.is_confirmed = True
            user.confirmation_code = None
            db.session.commit()
            session.pop('pending_email', None)
            return "Compte activé ! <a href='/login'>Connexion</a>"

        return "Code incorrect. <a href='/confirm'>Réessayer</a>"

    return f"""
    <h2>Validation</h2>
    <form method="POST">
        Code reçu pour {email} : <input type="text" name="code" required><br><br>
        <button type="submit">Valider</button>
    </form>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if not user or not check_password_hash(user.password_hash, password):
            return "Identifiants invalides. <a href='/login'>Réessayer</a>"

        if not user.is_confirmed:
            session['pending_email'] = email
            return "Compte non validé. <a href='/confirm'>Entrer le code</a>"

        login_user(user)
        return redirect(url_for('protected'))

    return """
    <h2>Connexion</h2>
    <form method="POST">
        Email : <input type="email" name="email" required><br><br>
        Mot de passe : <input type="password" name="password" required><br><br>
        <button type="submit">Connexion</button>
    </form>
    """

@app.route('/protected')
@login_required
def protected():
    return f"<h2>Espace privé</h2><p>Connecté en tant que {current_user.email}</p><a href='/logout'>Déconnexion</a>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
