import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from app.constantes import NOME_MUNICIPIO, UF_MUNICIPIO
from app.dashboard.estilos import aplicar_estilos
from app.dashboard.html_seguro import esc
from app.dashboard.sessao import iniciais, preparar_sessao, sair, usuario_atual
from app.dashboard.telas.login import renderizar_tela_login
from app.dashboard.ui import PAGINAS, html
from app.erros import mensagem_para_usuario
from app.database.conexao import (
    ErroConfiguracao,
    configuracao_supabase,
    inicializar_banco,
    modo_local,
)

from app.dashboard.telas.mapa_postes import renderizar_tela_mapa
from app.dashboard.telas.solicitar_reparo import renderizar_tela_solicitar_reparo
from app.dashboard.telas.ordens_servico import renderizar_tela_ordens_servico
from app.dashboard.telas.importar_base import renderizar_tela_importar
from app.dashboard.telas.cadastrar_poste import renderizar_tela_cadastrar
from app.dashboard.telas.localizacao_postes import renderizar_tela_localizacao
from app.dashboard.telas.administracao import eh_admin, renderizar_tela_administracao

st.set_page_config(
    page_title=f"Ilumina {NOME_MUNICIPIO}",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

aplicar_estilos()

try:
    if modo_local():
        inicializar_banco()
    else:
        configuracao_supabase()
except ErroConfiguracao as erro:
    st.error(str(erro))
    st.stop()

if not preparar_sessao():
    renderizar_tela_login()
    st.stop()


def _tratar_erro_banco(erro: Exception) -> None:
    """Mostra uma mensagem compreensível (e desloga só se a sessão expirou de fato)."""
    mensagem = mensagem_para_usuario(erro, modo_local=modo_local())
    if mensagem.sessao_expirada:
        sair(mensagem.texto)
        st.rerun()
    st.error(mensagem.texto)


# ---- Navegação ---------------------------------------------------------------
# `pagina_atual` é a fonte da verdade; o menu só a espelha. Assim qualquer botão
# pode trocar de tela (ui.ir_para) sem mexer no estado de um widget já criado.
# A tela "Administração" só entra no menu de quem é admin. Operador que tentar
# chegar nela pelo session_state volta para o mapa (e o banco barra de qualquer jeito).
usuario = usuario_atual()
paginas = dict(PAGINAS)
if eh_admin(usuario):
    paginas["admin"] = ":material/admin_panel_settings: Admin"

if st.session_state.get("pagina_atual") not in paginas:
    st.session_state["pagina_atual"] = "mapa"
st.session_state["nav_principal"] = st.session_state["pagina_atual"]


def _ao_trocar_tela() -> None:
    st.session_state["pagina_atual"] = st.session_state["nav_principal"]
    st.session_state.pop("reparo_emitida", None)  # voltar ao reparo abre formulário novo


# ---- Cabeçalho: marca · menu · quem está logado ------------------------------
nome_usuario = usuario["nome"]
papel_usuario = "Administrador" if usuario.get("papel") == "admin" else "Operador"

# Com a aba Admin o menu tem 7 itens: ganha espaço do bloco do usuário para não quebrar linha.
proporcao = [1, 7.4, 1.4] if "admin" in paginas else [1, 6.4, 1.7]
col_marca, col_menu, col_usuario = st.columns(proporcao, vertical_alignment="center", gap="small")
with col_marca:
    html(
        '<div class="il-marca">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="square" aria-hidden="true"><path d="M6 21V5h9"></path><path d="M15 5v3"></path>'
        '<path d="M12 8h6l-1.5 3h-3z"></path><path d="M4 21h4"></path></svg>'
        '<div><div class="il-marca-nome">ILUMINA</div>'
        f'<div class="il-marca-local">{esc(NOME_MUNICIPIO)} / {esc(UF_MUNICIPIO)}</div></div></div>'
    )
with col_menu:
    st.radio(
        "Telas",
        list(paginas),
        format_func=lambda chave: paginas[chave],
        key="nav_principal",
        on_change=_ao_trocar_tela,
        horizontal=True,
        label_visibility="collapsed",
    )
with col_usuario:
    c_info, c_sair = st.columns([3, 1.2], vertical_alignment="center", gap="small")
    with c_info:
        html(
            '<div class="il-usuario">'
            f'<span class="il-avatar" aria-hidden="true">{esc(iniciais(nome_usuario))}</span>'
            f'<div><div class="il-usuario-nome">{esc(nome_usuario)}</div>'
            f'<div class="il-usuario-papel">{esc(papel_usuario)}</div></div></div>'
        )
    with c_sair:
        if not modo_local():
            st.button("Sair", key="btn_sair", on_click=sair, type="tertiary")

telas = {
    "mapa": renderizar_tela_mapa,
    "reparo": renderizar_tela_solicitar_reparo,
    "ordens": renderizar_tela_ordens_servico,
    "cadastro": renderizar_tela_cadastrar,
    "importar": renderizar_tela_importar,
    "localizar": renderizar_tela_localizacao,
    "admin": renderizar_tela_administracao,
}

try:
    telas[st.session_state["pagina_atual"]]()
except Exception as erro:
    _tratar_erro_banco(erro)
