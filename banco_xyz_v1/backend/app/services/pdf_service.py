from __future__ import annotations

from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.core.config import REPORTS_DIR


PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 2 * cm
TOP_MARGIN = 2 * cm
BOTTOM_MARGIN = 2 * cm


def _new_page(c: canvas.Canvas) -> float:
    c.showPage()
    c.setFont("Helvetica", 10)
    return PAGE_HEIGHT - TOP_MARGIN


def _ensure_space(c: canvas.Canvas, y: float, needed: float) -> float:
    if y - needed < BOTTOM_MARGIN:
        return _new_page(c)
    return y


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width_chars: int = 95,
    line_height: float = 16,
    font_name: str = "Helvetica",
    font_size: int = 10,
) -> float:
    c.setFont(font_name, font_size)

    for paragraph in str(text).split("\n"):
        lines = wrap(paragraph, width_chars) or [""]
        needed = max(len(lines), 1) * line_height + 4
        y = _ensure_space(c, y, needed)
        c.setFont(font_name, font_size)

        for line in lines:
            c.drawString(x, y, line)
            y -= line_height
        y -= 4

    return y


def _format_audit_log(audit_log: list[dict] | list) -> str:
    lines: list[str] = []

    for item in audit_log or []:
        if isinstance(item, dict):
            at = item.get("at", "-")
            step = item.get("step", "-")
            details = []

            for key, value in item.items():
                if key in {"at", "step"}:
                    continue
                details.append(f"{key}={value}")

            suffix = f" | {'; '.join(details)}" if details else ""
            lines.append(f"{at} | {step}{suffix}")
        else:
            lines.append(str(item))

    return "\n".join(lines)


def generate_report_pdf(state: dict, filename: str) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = REPORTS_DIR / filename

    client = state.get("client", {})
    client_name = client.get("nome", "Cliente")
    client_id = state.get("client_id", "-")
    profile = client.get("perfil_suitability", "-")
    objective = client.get("objetivo_investimento", "-")
    horizon = client.get("horizonte_tempo", "-")
    patrimonio = client.get("patrimonio_total", "-")
    thread_id = state.get("thread_id", "-")
    run_id = state.get("run_id", "-")
    report_text = state.get("report_text", "Relatório não disponível.")
    audit_log = state.get("audit_log", [])

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.setTitle(f"Relatorio {client_name}")

    y = PAGE_HEIGHT - TOP_MARGIN

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(LEFT_MARGIN, y, "Banco XYZ - Relatório de Investimentos")
    y -= 1.2 * cm

    c.setFont("Helvetica", 10)
    header = [
        f"Cliente: {client_name} ({client_id})",
        f"Perfil: {profile} | Objetivo: {objective}",
        f"Horizonte: {horizon} | Patrimônio: R$ {patrimonio}",
        f"Thread: {thread_id} | Run: {run_id}",
    ]

    for line in header:
        y = _ensure_space(c, y, 16)
        c.setFont("Helvetica", 10)
        c.drawString(LEFT_MARGIN, y, line)
        y -= 14

    y -= 10

    # Corpo do relatório
    y = _ensure_space(c, y, 30)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT_MARGIN, y, "Relatório")
    y -= 18

    y = _draw_wrapped_text(
        c,
        report_text,
        LEFT_MARGIN,
        y,
        width_chars=95,
        line_height=14,
        font_name="Helvetica",
        font_size=10,
    )

    y -= 8

    # Auditoria
    y = _ensure_space(c, y, 30)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT_MARGIN, y, "Trilha de auditoria")
    y -= 18

    audit_text = _format_audit_log(audit_log) or "Sem registros de auditoria."
    y = _draw_wrapped_text(
        c,
        audit_text,
        LEFT_MARGIN,
        y,
        width_chars=105,
        line_height=12,
        font_name="Helvetica",
        font_size=9,
    )

    # Rodapé simples
    y -= 12
    y = _ensure_space(c, y, 24)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        LEFT_MARGIN,
        y,
        "Documento gerado automaticamente para apoio consultivo. Sujeito a validacao humana final.",
    )

    c.save()
    return str(pdf_path)