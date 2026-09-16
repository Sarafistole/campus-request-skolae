import json
import urllib.error
import urllib.request

from flask import current_app


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_confirmation_email(recipient_email, confirmation_code):
    api_key = current_app.config.get("BREVO_API_KEY")
    sender = current_app.config.get("SMTP_SENDER")

    if not api_key or not sender:
        raise RuntimeError(
            "Configuration Brevo incomplète. "
            "Vérifiez BREVO_API_KEY et SMTP_SENDER dans le fichier .env."
        )

    payload = {
        "sender": {
            "email": sender,
            "name": "Campus Request",
        },
        "to": [
            {
                "email": recipient_email,
            }
        ],
        "subject": "Campus Request - Code de vérification",
        "htmlContent": (
            "<h2>Bienvenue sur Campus Request</h2>"
            "<p>Voici votre code de vérification :</p>"
            f"<h1>{confirmation_code}</h1>"
            "<p>Ce code est requis pour activer votre compte.</p>"
        ),
    }

    request = urllib.request.Request(
        BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError(
                    f"Brevo a retourné le statut HTTP {response.status}."
                )

    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Erreur HTTP Brevo : {error.code}."
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            "Impossible de contacter l'API Brevo."
        ) from error

    return True