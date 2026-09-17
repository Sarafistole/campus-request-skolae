import json
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_confirmation_email(recipient_email, confirmation_code):
    api_key = current_app.config.get("BREVO_API_KEY")
    sender = current_app.config.get("SMTP_SENDER")
    base_url = current_app.config.get(
        "BASE_URL",
        "http://localhost:5000"
    )
    socks_proxy = current_app.config.get("SOCKS_PROXY")

    if not api_key or not sender:
        raise RuntimeError(
            "Configuration Brevo incomplète. "
            "Vérifiez BREVO_API_KEY et SMTP_SENDER dans le fichier .env."
        )

    # Construction du lien permettant de confirmer directement
    # le compte depuis l'email.
    encoded_email = urllib.parse.quote(recipient_email, safe="")

    confirm_url = (
        f"{base_url.rstrip('/')}/confirm"
        f"?email={encoded_email}"
        f"&code={confirmation_code}"
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
        "subject": "Campus Request - Activation de votre compte",
        "htmlContent": f"""
            <div style="
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: auto;
                padding: 20px;
            ">
                <h2>Bienvenue sur Campus Request</h2>

                <p>
                    Voici votre code de vérification :
                </p>

                <div style="
                    padding: 15px;
                    text-align: center;
                    margin: 15px 0;
                    background: #f4f6f9;
                    border-radius: 6px;
                ">
                    <strong style="
                        font-size: 26px;
                        letter-spacing: 4px;
                    ">
                        {confirmation_code}
                    </strong>
                </div>

                <p>
                    Vous pouvez également confirmer directement
                    votre compte avec le bouton ci-dessous :
                </p>

                <p style="text-align: center; margin: 25px 0;">
                    <a
                        href="{confirm_url}"
                        style="
                            display: inline-block;
                            padding: 12px 24px;
                            background: #0066cc;
                            color: #ffffff;
                            text-decoration: none;
                            border-radius: 4px;
                            font-weight: bold;
                        "
                    >
                        Confirmer mon compte
                    </a>
                </p>

                <p style="font-size: 12px; color: #666666;">
                    Si le bouton ne fonctionne pas, vous pouvez
                    toujours utiliser le code de vérification
                    indiqué ci-dessus.
                </p>

                <hr style="
                    border: none;
                    border-top: 1px solid #eeeeee;
                    margin: 20px 0;
                ">

                <p style="font-size: 11px; color: #888888;">
                    Ceci est un message automatique.
                </p>
            </div>
        """,
    }

    # Si un proxy SOCKS est configuré, l'appel à Brevo
    # est effectué via curl avec SOCKS5.
    if socks_proxy:
        curl_bin = shutil.which("curl")

        if not curl_bin:
            raise RuntimeError(
                "SOCKS_PROXY est configuré mais curl "
                "n'est pas disponible sur le système."
            )

        command = [
            curl_bin,
            "--socks5-hostname",
            socks_proxy,
            "--silent",
            "--show-error",
            "--fail-with-body",
            "--request",
            "POST",
            BREVO_API_URL,
            "--header",
            "accept: application/json",
            "--header",
            f"api-key: {api_key}",
            "--header",
            "content-type: application/json",
            "--data",
            json.dumps(payload),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Délai dépassé lors de l'appel à Brevo via le proxy SOCKS."
            ) from error

        if result.returncode != 0:
            error_message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(
                "Erreur lors de l'appel à Brevo via le proxy SOCKS : "
                f"{error_message}"
            )

        return True

    # Sans proxy SOCKS, utilisation directe de l'API REST Brevo.
    brevo_request = urllib.request.Request(
        BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
            "User-Agent": "CampusRequest-Client",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            brevo_request,
            timeout=10
        ) as response:
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