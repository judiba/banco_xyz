from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER


def send_email_message(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
) -> None:
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("Configuração SMTP incompleta")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM or SMTP_USER
    msg["To"] = to_email
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            content = f.read()
        msg.add_attachment(
            content,
            maintype="application",
            subtype="pdf",
            filename="relatorio.pdf",
        )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
