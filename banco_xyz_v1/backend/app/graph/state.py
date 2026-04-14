from typing import Any, TypedDict

class GraphState(TypedDict, total=False):
    client_id: str
    thread_id: str
    run_id: str
    client: dict[str, Any]
    rag_results: list[dict[str, Any]]
    market_snapshot: dict[str, Any]
    recommended_allocation: list[dict[str, Any]]
    report_prompt: str
    report_text: str
    approval_status: str
    approval_notes: str
    approver_name: str
    pdf_path: str
    audit_log: list[dict[str, Any]]
