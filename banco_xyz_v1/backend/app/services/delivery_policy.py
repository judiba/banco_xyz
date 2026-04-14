from __future__ import annotations

from app.models.enums import DeliveryChannel



def resolve_delivery_plan(state: dict, requested_channel: str | None = None) -> dict:
    client = state.get("client", {}) or {}

    preferred = str(client.get("canal_preferencia") or "").strip().lower()
    email = client.get("email")
    phone = client.get("telefone")
    name = client.get("nome", "cliente")

    requested = (requested_channel or "").strip().lower() if requested_channel else None
    channel = requested or preferred or DeliveryChannel.MANUAL_REVIEW.value

    email_body = state.get("email_text") or (
        f"Olá, {name},\n\nSegue em anexo o seu relatório de investimentos.\n\nAtenciosamente,\nBanco XYZ"
    )
    whatsapp_body = state.get("whatsapp_text") or (
        f"Olá, {name}! Seu relatório foi aprovado e está pronto para envio."
    )

    channels: list[dict] = []

    if channel == DeliveryChannel.EMAIL.value:
        if not email:
            return {"decision": "manual_review", "reason": "Cliente sem e-mail", "channels": []}
        channels.append({"channel": "email", "target": email, "subject": "Seu relatório de investimentos", "body": email_body})

    elif channel == DeliveryChannel.WHATSAPP.value:
        if not phone:
            return {"decision": "manual_review", "reason": "Cliente sem telefone", "channels": []}
        channels.append({"channel": "whatsapp", "target": phone, "body": whatsapp_body})

    elif channel == DeliveryChannel.BOTH.value:
        if email:
            channels.append({"channel": "email", "target": email, "subject": "Seu relatório de investimentos", "body": email_body})
        if phone:
            channels.append({"channel": "whatsapp", "target": phone, "body": whatsapp_body})
        if not channels:
            return {"decision": "manual_review", "reason": "Sem contatos válidos", "channels": []}

    elif channel == DeliveryChannel.AUTOMATIC.value:
        if email:
            channels.append({"channel": "email", "target": email, "subject": "Seu relatório de investimentos", "body": email_body})
        elif phone:
            channels.append({"channel": "whatsapp", "target": phone, "body": whatsapp_body})
        else:
            return {"decision": "manual_review", "reason": "Sem contatos válidos", "channels": []}

    else:
        return {"decision": "manual_review", "reason": "Canal não suportado ou indefinido", "channels": []}

    return {"decision": "auto_delivery", "reason": None, "channels": channels}
