import smtplib
from email.message import EmailMessage

from flask import current_app


def send_confirmation_email(recipient_email, confirmation_code):
    smtp_server = current_app.config.get("SMTP_SERVER")
    smtp_port = current_app.config.get("SMTP_PORT")
    smtp_user = current_app.config.get("SMTP_USER")
    smtp_password = current_app.config.get("SMTP_PASSWORD")
    smtp_sender = current_app.config.get("SMTP_SENDER")

    if not all([
        smtp_server,
        smtp_port,
        smtp_user,
        smtp_password,
        smtp_sender,
    ]):
        raise RuntimeError(
            "Configuration SMTP incomplète. "
            "Vérifiez les variables SMTP dans le fichier .env."
        )

    message = EmailMessage()
    message["Subject"] = "Campus Request - Code de vérification"
    message["From"] = smtp_sender
    message["To"] = recipient_email

    message.set_content(
        "Votre code de vérification Campus Request est : "
        f"{confirmation_code}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, "
        "vous pouvez ignorer cet email."
    )

    with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)