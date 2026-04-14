from __future__ import annotations

from app.services.audit_service import append_audit


def build_contact_messages(state: dict) -> dict:
    client = state.get("client", {})
    name = client.get("nome", "cliente")
    report = state.get("report_text", "")

    email_text = (
        f"Olá, {name},\n\n"
        "Seu relatório de investimentos foi aprovado e segue em anexo.\n\n"
        "Resumo executivo:\n"
        f"{report[:700]}\n\n"
        "Atenciosamente,\nBanco XYZ"
    )

    whatsapp_text = (
        f"Olá, {name}! Seu relatório de investimentos foi aprovado e está disponível. "
        "Posso compartilhar o documento final com você."
    )

    state["email_text"] = email_text
    state["whatsapp_text"] = whatsapp_text
    return append_audit(state, "build_contact_messages")
