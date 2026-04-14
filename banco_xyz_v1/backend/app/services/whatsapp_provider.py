from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message(
    phone_number: str,
    message: str,
    attachment_path: str | None = None,
) -> None:
    if not phone_number:
        raise RuntimeError("Telefone inválido")

    # TODO: substituir por Meta WhatsApp Cloud API ou Twilio.
    logger.info(
        "Stub de WhatsApp acionado | phone=%s | attachment=%s | preview=%s",
        phone_number,
        attachment_path,
        message[:120],
    )
