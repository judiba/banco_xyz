from __future__ import annotations

import streamlit as st

from services.api import approve_report



def render_approval_panel(thread_id: str) -> dict | None:
    st.markdown("### Aprovação humana")
    notes = st.text_area("Observações do analista", value="")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Aprovar relatório"):
            return approve_report(thread_id, True, notes, "Analista Humano")

    with col2:
        if st.button("Rejeitar relatório"):
            return approve_report(thread_id, False, notes, "Analista Humano")

    return None
