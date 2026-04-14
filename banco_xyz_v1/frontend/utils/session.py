import streamlit as st

def init_session():
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("pdf_path", None)