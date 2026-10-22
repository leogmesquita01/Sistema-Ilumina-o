import importlib
import streamlit as st
import app.dashboard.estilos.base as _mod_base
import app.dashboard.estilos.sidebar as _mod_sidebar
import app.dashboard.estilos.cards as _mod_cards
import app.dashboard.estilos.componentes as _mod_componentes


def aplicar_estilos() -> None:
    importlib.reload(_mod_base)
    importlib.reload(_mod_sidebar)
    importlib.reload(_mod_cards)
    importlib.reload(_mod_componentes)
    css_completo = "\n".join(
        [
            _mod_base.CSS_BASE,
            _mod_sidebar.CSS_SIDEBAR,
            _mod_cards.CSS_CARDS,
            _mod_componentes.CSS_COMPONENTES,
        ]
    )
    st.markdown(f"<style>{css_completo}</style>", unsafe_allow_html=True)
