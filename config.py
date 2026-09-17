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

    # URL publique de l'application utilisée pour générer
    # les liens présents dans les emails.
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    # Proxy SOCKS optionnel utilisé pour l'envoi Brevo.
    # Laisser vide lorsqu'aucun proxy n'est nécessaire.
    SOCKS_PROXY = os.getenv("SOCKS_PROXY")