from __future__ import annotations

from typing import Any

from app.graph.workflow import report_graph
from app.services.pdf_service import generate_report_pdf



def generate_report_flow(client_id: str, thread_id: str) -> dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "client_id": client_id,
        "thread_id": thread_id,
        "approval_status": "pending",
        "delivery_status": "not_requested",
        "audit_log": [],
    }
    state = report_graph.invoke(initial_state, config=config)

    if state.get("pdf_path"):
        return _build_response(state, "completed")

    snapshot = report_graph.get_state(config)
    pending = snapshot.values or state
    return _build_response(pending, "awaiting_human_approval")



def approve_report_flow(
    thread_id: str,
    approved: bool,
    notes: str | None,
    approver_name: str | None,
) -> dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = report_graph.get_state(config)
    if not snapshot.values:
        raise ValueError("Thread não encontrado ou expirado")

    state = {**snapshot.values}
    state["approval_status"] = "approved" if approved else "rejected"
    state["approval_notes"] = notes
    state["approver_name"] = approver_name

    audit_log = state.get("audit_log", [])
    audit_log.append(
        {
            "step": "approval",
            "action": "approved" if approved else "rejected",
            "actor": approver_name,
            "notes": notes,
        }
    )
    state["audit_log"] = audit_log

    if approved:
        run_id = state.get("run_id") or "sem_run_id"
        client_id = state.get("client_id") or "sem_client_id"
        filename = f"relatorio_{client_id}_{run_id}.pdf"
        state["pdf_path"] = generate_report_pdf(state, filename)

    return _build_response(state, "completed" if approved else "rejected")



def get_report_status_flow(thread_id: str) -> dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = report_graph.get_state(config)
    if not snapshot.values:
        raise ValueError("Thread não encontrada ou expirada")
    state = snapshot.values
    return {
        "thread_id": state.get("thread_id"),
        "approval_status": state.get("approval_status"),
        "delivery_status": state.get("delivery_status"),
        "pdf_path": state.get("pdf_path"),
        "audit_log": state.get("audit_log", []),
    }



def _build_response(state: dict, status: str) -> dict[str, Any]:
    return {
        "status": status,
        "thread_id": state.get("thread_id"),
        "run_id": state.get("run_id"),
        "report_preview": state.get("report_text"),
        "email_text": state.get("email_text"),
        "whatsapp_text": state.get("whatsapp_text"),
        "pdf_path": state.get("pdf_path"),
        "delivery_status": state.get("delivery_status"),
        "artifacts": {
            "recommended_allocation": state.get("recommended_allocation"),
            "rag_results": state.get("rag_results"),
        },
        "audit_log": state.get("audit_log", []),
        "error_message": state.get("error_message"),
    }
