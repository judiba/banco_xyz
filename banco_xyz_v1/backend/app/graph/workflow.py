from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from app.agents.report_agent import approval_gate, build_prompt, draft_report, load_client, retrieve_knowledge
from app.core.config import settings
from app.graph.state import GraphState
from app.services.pdf_service import generate_report_pdf

_db_path = Path(settings.sqlite_db_path)
_db_path.parent.mkdir(parents=True, exist_ok=True)
_conn = sqlite3.connect(str(_db_path), check_same_thread=False)
checkpointer = SqliteSaver(_conn)


def create_pdf(state: dict) -> dict:
    print("🔥 CREATE_PDF FOI EXECUTADO")
    filename = f"relatorio_{state['client_id']}_{state['run_id']}.pdf"
    pdf_path = generate_report_pdf(state, filename)
    audit = state.get("audit_log", []) + [{"step": "create_pdf", "file": pdf_path}]
    return {**state, "pdf_path": pdf_path, "audit_log": audit}


def approval_router(state: dict) -> str:
    return "approved" if state.get("approval_status") == "approved" else "rejected"


builder = StateGraph(GraphState)
builder.add_node("load_client", load_client)
builder.add_node("retrieve_knowledge", retrieve_knowledge)
builder.add_node("build_prompt", build_prompt)
builder.add_node("draft_report", draft_report)
builder.add_node("approval_gate", approval_gate)
builder.add_node("create_pdf", create_pdf)

builder.set_entry_point("load_client")
builder.add_edge("load_client", "retrieve_knowledge")
builder.add_edge("retrieve_knowledge", "build_prompt")
builder.add_edge("build_prompt", "draft_report")
builder.add_edge("draft_report", "approval_gate")
builder.add_conditional_edges("approval_gate", approval_router, {"approved": "create_pdf", "rejected": END})
builder.add_edge("create_pdf", END)

report_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_after=["draft_report"],
)