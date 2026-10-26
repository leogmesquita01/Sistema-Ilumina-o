import streamlit as st

from app.constantes import NOME_MUNICIPIO, UF_MUNICIPIO
from app.dashboard.sessao import entrar


def renderizar_tela_login() -> None:
    _, centro, _ = st.columns([1, 1.15, 1])
    with centro:
        st.markdown(
            '<div style="text-align: center; margin: 8vh 0 18px 0;">'
            '<div style="width: 52px; height: 52px; margin: 0 auto 14px auto; border-radius: 50%; '
            'background: linear-gradient(135deg, #10B981, #059669); display: flex; align-items: center; '
            'justify-content: center; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);">'
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#052016" stroke-width="2.5" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
            '</div>'
            '<div style="font-family: \'Outfit\', sans-serif; font-size: 1.5rem; font-weight: 800; color: #FFFFFF;">'
            f'Ilumina <span style="color: #10B981;">{NOME_MUNICIPIO}</span></div>'
            f'<div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">Iluminação pública · {NOME_MUNICIPIO} / {UF_MUNICIPIO}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        aviso = st.session_state.pop("aviso_login", None)
        if aviso:
            st.warning(aviso)

        with st.form("form_login"):
            email = st.text_input("E-mail", autocomplete="username")
            senha = st.text_input("Senha", type="password", autocomplete="current-password")
            enviar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if enviar:
            with st.spinner("Entrando..."):
                erro = entrar(email, senha)
            if erro:
                st.error(erro)
            else:
                st.rerun()

        st.caption("Acesso restrito à equipe. Contas são criadas pelo administrador.")
