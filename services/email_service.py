import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_confirmation_email(recipient_email, confirmation_code, fallback_url="http://localhost:5000/"):
    api_key = current_app.config.get("BREVO_API_KEY") if current_app else os.getenv("BREVO_API_KEY")
    sender = current_app.config.get("SMTP_SENDER") if current_app else os.getenv("SMTP_SENDER")
    socks_proxy = os.getenv("SOCKS_PROXY")

    # URL propre depuis l'environnement, sinon fallback
    base_url = os.getenv("BASE_URL") or (current_app.config.get("BASE_URL") if current_app else None) or fallback_url

    if not api_key or not sender:
        raise RuntimeError(
            "Configuration Brevo incomplète. "
            "Vérifiez BREVO_API_KEY et SMTP_SENDER dans le fichier .env."
        )

    confirm_url = f"{base_url.rstrip('/')}/confirm?email={urllib.parse.quote(recipient_email)}&code={confirmation_code}"

    payload = {
        "sender": {
            "email": sender,
            "name": "Campus Request - Ne pas répondre",
        },
        "replyTo": {
            "email": "no-reply@campusrequest.skolae.fr",
            "name": "No Reply Automatique",
        },
        "to": [
            {
                "email": recipient_email,
            }
        ],
        "subject": "Campus Request - Activation de votre compte",
        "htmlContent": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #003366;">Bienvenue sur Campus Request</h2>
                <p>Voici votre code de validation :</p>
                <div style="background: #f4f6f9; padding: 15px; border-radius: 6px; text-align: center; margin: 15px 0;">
                    <span style="font-size: 26px; font-weight: bold; letter-spacing: 4px; color: #003366;">{confirmation_code}</span>
                </div>
                <p>Ou activez directement votre compte en cliquant sur le lien ci-dessous :</p>
                <p style="text-align: center; margin: 25px 0;">
                    <a href="{confirm_url}" style="display: inline-block; background: #0066cc; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        Confirmer mon compte
                    </a>
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 11px; color: #888;">Ceci est un message automatique, merci de ne pas y répondre.</p>
            </div>
        """,
    }

    if socks_proxy:
        curl_bin = "/usr/bin/curl" if os.path.exists("/usr/bin/curl") else (shutil.which("curl") or "curl")
        cmd = [
            curl_bin, "--socks5-hostname", socks_proxy,
            "-s", "-S", "-X", "POST", BREVO_API_URL,
            "-H", "accept: application/json",
            "-H", f"api-key: {api_key}",
            "-H", "content-type: application/json",
            "-d", json.dumps(payload)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = (res.stdout + " " + res.stderr).strip()
        if "messageId" not in output:
            raise RuntimeError(f"Erreur Brevo (Proxy) : {output}")
        return True

    request = urllib.request.Request(
        BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
            "User-Agent": "CampusRequest-Client"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError(f"Brevo HTTP {response.status}")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Erreur HTTP Brevo : {error.code}.") from error
    except urllib.error.URLError as error:
        raise RuntimeError("Impossible de contacter l'API Brevo.") from error

    return True
