from __future__ import annotations

from typing import Any

from app.graph.workflow import report_graph
from app.models.enums import DeliveryStatus
from app.services.audit_service import append_audit
from app.services.delivery_policy import resolve_delivery_plan
from app.services.notification_service import send_email_message, send_whatsapp_message



def deliver_report_flow(
    thread_id: str,
    requested_channel: str | None = None,
    requested_by: str | None = None,
) -> dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = report_graph.get_state(config)

    if not snapshot.values:
        raise ValueError("Thread não encontrada ou expirada")

    state = snapshot.values

    if state.get("approval_status") != "approved":
        raise ValueError("Relatório ainda não aprovado")

    if not state.get("pdf_path"):
        raise ValueError("PDF ainda não foi gerado")

    plan = resolve_delivery_plan(state, requested_channel=requested_channel)
    if plan["decision"] == "manual_review":
        state["delivery_status"] = DeliveryStatus.MANUAL_REVIEW.value
        append_audit(state, "delivery_manual_review", requested_by=requested_by, reason=plan.get("reason"))
        return {
            "status": state["delivery_status"],
            "thread_id": thread_id,
            "pdf_path": state.get("pdf_path"),
            "decision": plan["decision"],
            "reason": plan.get("reason"),
            "channels": plan.get("channels", []),
            "audit_log": state.get("audit_log", []),
        }

    state["delivery_status"] = DeliveryStatus.IN_PROGRESS.value
    append_audit(state, "delivery_started", requested_by=requested_by, channel=requested_channel)

    successes = 0
    failures = 0

    for item in plan["channels"]:
        try:
            if item["channel"] == "email":
                send_email_message(
                    to_email=item["target"],
                    subject=item["subject"],
                    body=item["body"],
                    attachment_path=state["pdf_path"],
                )
            elif item["channel"] == "whatsapp":
                send_whatsapp_message(
                    phone_number=item["target"],
                    message=item["body"],
                    attachment_path=state.get("pdf_path"),
                )
            append_audit(state, "delivery_sent", requested_by=requested_by, target=item["target"], delivery_channel=item["channel"])
            successes += 1
        except Exception as exc:
            append_audit(state, "delivery_failed", requested_by=requested_by, target=item["target"], delivery_channel=item["channel"], error=str(exc))
            failures += 1

    if successes and failures:
        state["delivery_status"] = DeliveryStatus.PARTIAL.value
    elif successes:
        state["delivery_status"] = DeliveryStatus.SENT.value
    else:
        state["delivery_status"] = DeliveryStatus.FAILED.value

    return {
        "status": state["delivery_status"],
        "thread_id": thread_id,
        "pdf_path": state.get("pdf_path"),
        "decision": plan["decision"],
        "reason": plan.get("reason"),
        "channels": plan.get("channels", []),
        "audit_log": state.get("audit_log", []),
    }
