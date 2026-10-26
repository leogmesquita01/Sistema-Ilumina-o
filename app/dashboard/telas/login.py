import streamlit as st

from app.constantes import NOME_MUNICIPIO, UF_MUNICIPIO
from app.dashboard.html_seguro import esc
from app.dashboard.sessao import entrar
from app.dashboard.ui import html, painel, tela


def renderizar_tela_login() -> None:
    with tela("login"):
        _, centro, _ = st.columns([1, 1.05, 1])
        with centro:
            html(
                '<div class="il-login-topo">'
                '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                'stroke-linecap="square" aria-hidden="true"><path d="M6 21V5h9"></path><path d="M15 5v3"></path>'
                '<path d="M12 8h6l-1.5 3h-3z"></path><path d="M4 21h4"></path></svg>'
                '<div class="il-marca-nome">ILUMINA</div>'
                f'<div class="il-marca-local">Iluminação pública · {esc(NOME_MUNICIPIO)} / {esc(UF_MUNICIPIO)}</div>'
                "</div>"
            )

            aviso = st.session_state.pop("aviso_login", None)
            if aviso:
                st.warning(aviso)

            with painel("login"):
                html('<div class="il-painel-topo"><h1 class="il-painel-titulo">Entrar</h1></div>')
                with st.form("form_login", border=False):
                    email = st.text_input("E-mail", autocomplete="username")
                    senha = st.text_input("Senha", type="password", autocomplete="current-password")
                    enviar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if enviar:
                with st.spinner("Entrando…"):
                    erro = entrar(email, senha)
                if erro:
                    st.error(erro)
                else:
                    st.rerun()

            st.caption("Acesso restrito à equipe. As contas são criadas pelo administrador.")
