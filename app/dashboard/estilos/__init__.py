import streamlit as st
from app.dashboard.estilos.base import CSS_BASE
from app.dashboard.estilos.sidebar import CSS_SIDEBAR
from app.dashboard.estilos.cards import CSS_CARDS
from app.dashboard.estilos.componentes import CSS_COMPONENTES


def aplicar_estilos() -> None:
    css_completo = "\n".join([CSS_BASE, CSS_SIDEBAR, CSS_CARDS, CSS_COMPONENTES])
    st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True)
