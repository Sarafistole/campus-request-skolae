import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé utilisée par Flask pour sécuriser les sessions.
    # Elle doit être définie dans le fichier .env.
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Configuration Brevo pour l'envoi des codes de vérification.
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    SMTP_SENDER = os.getenv("SMTP_SENDER")