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
from app.database.conexao import (
    ErroConfiguracao,
    SessaoNecessaria,
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


def _sessao_expirada(erro: Exception) -> bool:
    texto = str(erro).lower()
    return isinstance(erro, SessaoNecessaria) or "jwt" in texto or "pgrst301" in texto


def _tratar_erro_banco(erro: Exception) -> None:
    """Mostra o erro do banco na tela em vez de esconder (ou desloga se expirou)."""
    if _sessao_expirada(erro):
        sair("Sua sessão expirou. Entre novamente.")
        st.rerun()
    st.error(
        "Não foi possível falar com o banco de dados. Verifique a internet e tente de novo.\n\n"
        f"Detalhe técnico: {erro}"
    )


# ---- Navegação ---------------------------------------------------------------
# `pagina_atual` é a fonte da verdade; o menu só a espelha. Assim qualquer botão
# pode trocar de tela (ui.ir_para) sem mexer no estado de um widget já criado.
if st.session_state.get("pagina_atual") not in PAGINAS:
    st.session_state["pagina_atual"] = "mapa"
st.session_state["nav_principal"] = st.session_state["pagina_atual"]


def _ao_trocar_tela() -> None:
    st.session_state["pagina_atual"] = st.session_state["nav_principal"]


# ---- Cabeçalho: marca · menu · quem está logado ------------------------------
usuario = usuario_atual()
nome_usuario = usuario["nome"]
papel_usuario = "Administrador" if usuario.get("papel") == "admin" else "Operador"

col_marca, col_menu, col_usuario = st.columns([1, 6.4, 1.7], vertical_alignment="center", gap="small")
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
        list(PAGINAS),
        format_func=lambda chave: PAGINAS[chave],
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
}

try:
    telas[st.session_state["pagina_atual"]]()
except Exception as erro:
    _tratar_erro_banco(erro)
