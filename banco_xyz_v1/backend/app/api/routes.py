from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.delivery import DeliveryRequest
from app.models.schemas import ApprovalRequest, GenerateReportRequest
from app.services.client_repository import get_client, list_clients
from app.services.delivery_service import deliver_report_flow
from app.services.file_service import resolve_report_file
from app.services.rag_service import ensure_vector_store
from app.services.report_service import approve_report_flow, generate_report_flow, get_report_status_flow

router = APIRouter(tags=["Banco XYZ"])


def _serialize_report_result(result: dict) -> dict:
    result = result or {}
    return {
        "status": result.get("status") or (
            "awaiting_human_approval"
            if result.get("approval_status") == "pending"
            else result.get("approval_status", "-")
        ),
        "thread_id": result.get("thread_id"),
        "run_id": result.get("run_id"),
        "report_preview": result.get("report_preview") or result.get("report_text", ""),
        "report_summary": result.get("report_summary") or result.get("report_preview") or result.get("report_text", ""),
        "report_detailed": result.get("report_detailed") or result.get("report_text", ""),
        "artifacts": result.get("artifacts", {}),
        "audit_log": result.get("audit_log", []),
        "pdf_path": result.get("pdf_path"),
        "error_message": result.get("error_message") or result.get("rag_error") or result.get("error"),
    }

@router.on_event("startup")
def startup():
    ensure_vector_store()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/clients")
def clients():
    return list_clients()


@router.get("/clients/{client_id}")
def client_detail(client_id: str):
    try:
        return get_client(client_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/reports/generate")
def generate_report(payload: GenerateReportRequest):
    result = generate_report_flow(client_id=payload.client_id, thread_id=payload.thread_id)
    return _serialize_report_result(result)
    

@router.post("/reports/approve")
def approve_report(payload: ApprovalRequest):
    try:
        result = approve_report_flow(
            thread_id=payload.thread_id,
            approved=payload.approved,
            notes=payload.approval_notes,
            approver_name=payload.approver_name,
        )
        return _serialize_report_result(result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/reports/deliver")
def deliver_report(payload: DeliveryRequest):
    try:
        channel = payload.channel.value if payload.channel else None
        return deliver_report_flow(
            thread_id=payload.thread_id,
            requested_channel=channel,
            requested_by=payload.requested_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/reports/status")
def report_status(thread_id: str):
    try:
        result = get_report_status_flow(thread_id)
        return _serialize_report_result(result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@router.get("/reports/file")
def download_report(path: str):
    try:
        file_path: Path = resolve_report_file(path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return FileResponse(file_path, media_type="application/pdf")
