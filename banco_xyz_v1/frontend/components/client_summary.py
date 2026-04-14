from __future__ import annotations

import streamlit as st



def render_client_summary(client: dict) -> None:
    st.markdown("### Cliente selecionado")
    st.write(client)
