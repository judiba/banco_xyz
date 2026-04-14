from __future__ import annotations

import streamlit as st



def render_timeline(status: str) -> None:
    st.markdown(f"### Timeline do fluxo")
    st.info(f"Status atual: {status}")
