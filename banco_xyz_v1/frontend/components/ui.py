from __future__ import annotations

import streamlit as st

from components.approval_panel import render_approval_panel
from components.client_summary import render_client_summary
from components.delivery_panel import render_delivery_panel
from components.timeline import render_timeline
from services.api import generate_report

def run_ui(selected_client: dict) -> None:
    init_session()
    thread_id = st.session_state.thread_id

    render_client_summary(selected_client)

    if st.button("Gerar rascunho"):
        st.session_state.workflow_result = generate_report(selected_client["id_pessoa"], thread_id)

    result = st.session_state.workflow_result
    if not result:
        return

    render_timeline(result.get("status", "-"))
    st.text_area("Prévia do relatório", result.get("report_preview", ""), height=280)

    approval_result = render_approval_panel(thread_id)
    if approval_result:
        st.session_state.workflow_result = approval_result
        result = approval_result

    if result.get("pdf_path"):
        delivery_result = render_delivery_panel(thread_id, result.get("pdf_path"))
        if delivery_result:
            st.session_state.workflow_result = delivery_result
