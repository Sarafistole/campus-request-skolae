from flask import Flask
from config import Config
from extensions import db, migrate
from sqlalchemy import text
from models import Student, Admin, RequestType, Tag, Ticket


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