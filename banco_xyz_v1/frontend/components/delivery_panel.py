from __future__ import annotations

import streamlit as st

from services.delivery_api import deliver_report

def init_session():
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("pdf_path", None)

def render_delivery_panel(thread_id: str, pdf_path: str | None) -> dict | None:
    st.markdown("### Entrega")
    if pdf_path:
        st.markdown(f"[Baixar PDF](http://127.0.0.1:8000/reports/file?path={pdf_path})")

    channel = st.selectbox("Canal de entrega", ["automatico", "email", "whatsapp", "ambos"])
    if st.button("Entregar relatório"):
        return deliver_report(thread_id, channel, "Analista Humano")

    return None
