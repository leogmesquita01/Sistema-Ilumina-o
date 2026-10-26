import streamlit as st

from app.dashboard.estilos.tema import CSS_TEMA


def aplicar_estilos() -> None:
    st.markdown(f"<style>{CSS_TEMA}</style>", unsafe_allow_html=True)
