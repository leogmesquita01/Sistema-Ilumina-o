import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from app.dashboard.estilos import aplicar_estilos
from app.database.conexao import inicializar_banco
from app.servicos.dados_postes import obter_resumo_indicadores

from app.dashboard.telas.mapa_postes import renderizar_tela_mapa
from app.dashboard.telas.solicitar_reparo import renderizar_tela_solicitar_reparo
from app.dashboard.telas.ordens_servico import renderizar_tela_ordens_servico
from app.dashboard.telas.importar_base import renderizar_tela_importar
from app.dashboard.telas.cadastrar_poste import renderizar_tela_cadastrar
from app.dashboard.telas.localizacao_postes import renderizar_tela_localizacao

st.set_page_config(
    page_title="Ilumina Boa Saúde",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicializar_banco()
aplicar_estilos()

try:
    stats = obter_resumo_indicadores()
    total_postes = stats["total_postes"]
    taxa_led = int(round(stats["taxa_led"]))
    os_abertas = stats["os_abertas"]
except Exception:
    total_postes = 0
    taxa_led = 0
    os_abertas = 0

menu_opcoes = [
    ":material/map: Mapa e postes",
    ":material/handyman: Solicitar reparo",
    ":material/assignment: Ordens de serviço",
    ":material/add_location_alt: Cadastrar poste",
    ":material/upload_file: Importar planilha",
    ":material/edit_location: Localizar postes",
]

mapa_antigo = {
    ":material/map: Mapa e Postes": menu_opcoes[0],
    ":material/upload_file: Importar base COSERN": menu_opcoes[4],
    ":material/edit_location: Localizar": menu_opcoes[5],
}
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = menu_opcoes[0]
st.session_state["pagina_atual"] = mapa_antigo.get(
    st.session_state["pagina_atual"], st.session_state["pagina_atual"]
)
if st.session_state["pagina_atual"] not in menu_opcoes:
    st.session_state["pagina_atual"] = menu_opcoes[0]

with st.sidebar:
    st.markdown(
        '<div class="brand-lockup">'
        '<span class="brand-mark" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M13 2 5 13h6l-1 9 9-12h-6l1-8Z"/></svg></span>'
        '<span><strong>Ilumina</strong><small>Boa Saúde · RN</small></span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-kicker">OPERAÇÃO MUNICIPAL</div>', unsafe_allow_html=True)
    pagina_ativa = st.radio(
        "Navegação",
        menu_opcoes,
        key="pagina_atual",
        label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    resumo = (
        '<div class="sidebar-summary">'
        '<span class="summary-label">REDE DE ILUMINAÇÃO</span>'
        f'<div class="summary-count">{total_postes} postes cadastrados</div>'
        f'<div class="summary-detail"><span>{os_abertas} chamados em aberto</span>'
        f'<span class="summary-led">{taxa_led}% LED</span></div></div>'
    )
    st.markdown(resumo, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">Secretaria de Obras e Infraestrutura</div>', unsafe_allow_html=True)

if pagina_ativa == menu_opcoes[0]:
    renderizar_tela_mapa()
elif pagina_ativa == menu_opcoes[1]:
    renderizar_tela_solicitar_reparo()
elif pagina_ativa == menu_opcoes[2]:
    renderizar_tela_ordens_servico()
elif pagina_ativa == menu_opcoes[3]:
    renderizar_tela_cadastrar()
elif pagina_ativa == menu_opcoes[4]:
    renderizar_tela_importar()
elif pagina_ativa == menu_opcoes[5]:
    renderizar_tela_localizacao()
