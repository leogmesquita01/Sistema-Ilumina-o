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
    total_led = stats["total_led"]
    taxa_led = int(round(stats["taxa_led"]))
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
    os_concluidas = stats["os_concluidas"]
except Exception:
    total_postes = 0
    total_led = 0
    taxa_led = 0
    total_chamados = 0
    os_abertas = 0
    os_concluidas = 0

menu_opcoes = [
    ":material/map: Mapa e postes",
    ":material/handyman: Solicitar reparo",
    ":material/assignment: Ordens de serviço",
    ":material/add_location_alt: Cadastrar poste",
    ":material/upload_file: Importar planilha",
    ":material/edit_location: Localizar",
]

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = menu_opcoes[0]

if "sidebar_reduzida" not in st.session_state:
    st.session_state["sidebar_reduzida"] = False

mapa_antigo = {
    ":material/map: Mapa e Postes": menu_opcoes[0],
    ":material/upload_file: Importar base COSERN": menu_opcoes[4],
}
st.session_state["pagina_atual"] = mapa_antigo.get(
    st.session_state["pagina_atual"], st.session_state["pagina_atual"]
)
if st.session_state["pagina_atual"] not in menu_opcoes:
    st.session_state["pagina_atual"] = menu_opcoes[0]

st.session_state["nav_mobile"] = st.session_state["pagina_atual"]


def _ao_mudar_topo() -> None:
    st.session_state["pagina_atual"] = st.session_state["nav_mobile"]


def _alternar_sidebar() -> None:
    st.session_state["sidebar_reduzida"] = not st.session_state.get("sidebar_reduzida", False)


sidebar_reduzida = st.session_state["sidebar_reduzida"]

if sidebar_reduzida:
    st.markdown(
        "<style>"
        "@media (min-width: 769px) {"
        "section[data-testid='stSidebar'], section.stSidebar, [data-testid='stSidebar'] {"
        "width: 76px !important; min-width: 76px !important; max-width: 76px !important;"
        "padding: 14px 4px 14px 14px !important;"
        "}"
        "div.st-key-nav_mobile_wrap { padding-left: 142px !important; }"
        "div.st-key-sb_toggle_wrap div[data-testid='stButton'] > button {"
        "width: 48px !important; min-width: 48px !important; max-width: 48px !important; padding: 0 !important;"
        "}"
        "}"
        "@media (max-width: 768px) {"
        "div.st-key-sb_toggle_wrap { display: block !important; }"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )

with st.sidebar:
    brand_pill_html = (
        '<div style="display: inline-flex; align-items: center; gap: 10px; background: #0D1522; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 999px; padding: 6px 16px 6px 6px; width: max-content; box-shadow: 0 10px 26px rgba(0, 0, 0, 0.38); margin-bottom: 10px; white-space: nowrap;">'
        '<div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #10B981, #059669); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35); flex-shrink: 0;">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#052016" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>'
        '</svg>'
        '</div>'
        '<span style="font-family: \'Outfit\', sans-serif; font-size: 0.96rem; font-weight: 800; letter-spacing: -0.3px; color: #FFFFFF; line-height: 1;">'
        'Ilumina <span style="color: #10B981;">Boa Saúde</span>'
        '</span>'
        '</div>'
    )
    st.markdown(brand_pill_html, unsafe_allow_html=True)

    with st.container(key="sb_toggle_wrap"):
        if sidebar_reduzida:
            st.button(
                ":material/keyboard_double_arrow_right:",
                key="btn_toggle_sb",
                on_click=_alternar_sidebar,
                help="Expandir controles da tela",
            )
        else:
            st.button(
                ":material/keyboard_double_arrow_left: Recolher barra",
                key="btn_toggle_sb",
                on_click=_alternar_sidebar,
                use_container_width=True,
            )

    if sidebar_reduzida:
        st.session_state["sb_card"] = None
        rail_icons_html = (
            '<div style="width: 48px; background: #0D1522; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 999px; padding: 7px 0 9px 0; display: flex; flex-direction: column; align-items: center; gap: 10px; box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45); margin-top: 6px;">'
            '<div style="width: 36px; height: 36px; border-radius: 50%; background: #10B981; color: #052016; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);" title="Painel ativo">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#052016" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>'
            '</div>'
            '<div style="width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94A3B8;" title="Pesquisar poste">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
            '</div>'
            '<div style="width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94A3B8;" title="Filtros da tela">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>'
            '</div>'
            '<div style="width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94A3B8;" title="Camadas do mapa">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>'
            '</div>'
            '<div style="width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94A3B8;" title="Inspecionar ativo">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
            '</div>'
            f'<div style="width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #10B981;" title="Cobertura LED: {taxa_led}%">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
            '</div>'
            '<div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.66rem; color: #34D399; margin-top: 2px;" title="Leonardo Mesquita · Gestor Municipal">LM</div>'
            '</div>'
        )
        st.markdown(rail_icons_html, unsafe_allow_html=True)
    else:
        st.session_state["sb_card"] = st.container(key="sb_card_expanded")

mobile_topbar_html = (
    '<div class="v14-mobile-topbar">'
    '<div style="display: flex; align-items: center; gap: 10px;">'
    '<div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #10B981, #059669); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">'
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#052016" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
    '</div>'
    '<div>'
    '<div style="font-family: \'Outfit\', sans-serif; font-size: 0.98rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">Ilumina <span style="color: #10B981;">Boa Saúde</span></div>'
    '<div style="font-size: 0.65rem; color: #94A3B8;">Infraestrutura Municipal</div>'
    '</div>'
    '</div>'
    '<div style="display: flex; align-items: center; gap: 8px;">'
    f'<span class="mono" style="font-size: 0.72rem; color: #34D399; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.28); padding: 3px 9px; border-radius: 999px; font-weight: 700;">{total_postes} postes &bull; {taxa_led}% LED</span>'
    '<div style="width: 28px; height: 28px; border-radius: 50%; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.68rem; color: #34D399;">LM</div>'
    '</div>'
    '</div>'
)
st.markdown(mobile_topbar_html, unsafe_allow_html=True)

with st.container(key="nav_mobile_wrap"):
    st.radio(
        "Navegação Principal",
        menu_opcoes,
        key="nav_mobile",
        on_change=_ao_mudar_topo,
        horizontal=True,
        label_visibility="collapsed",
    )

pagina_ativa = st.session_state["pagina_atual"]

if pagina_ativa == ":material/map: Mapa e postes":
    renderizar_tela_mapa()
elif pagina_ativa == ":material/handyman: Solicitar reparo":
    renderizar_tela_solicitar_reparo()
elif pagina_ativa == ":material/assignment: Ordens de serviço":
    renderizar_tela_ordens_servico()
elif pagina_ativa == ":material/add_location_alt: Cadastrar poste":
    renderizar_tela_cadastrar()
elif pagina_ativa == ":material/upload_file: Importar planilha":
    renderizar_tela_importar()
elif pagina_ativa == ":material/edit_location: Localizar":
    renderizar_tela_localizacao()

if not sidebar_reduzida and st.session_state.get("sb_card") is not None:
    with st.session_state["sb_card"]:
        rodape_sidebar_html = (
            '<div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(255, 255, 255, 0.06);">'
            '<div style="background: #0A101A; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 14px; padding: 10px 12px; margin-bottom: 0.7rem;">'
            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
            '<span style="font-size: 0.72rem; color: #94A3B8;">Cobertura LED</span>'
            f'<span class="mono" style="font-size: 0.74rem; color: #34D399; font-weight: 700;">{taxa_led}%</span>'
            '</div>'
            '<div style="width: 100%; height: 4px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden;">'
            f'<div style="width: {taxa_led}%; height: 100%; background: #10B981; border-radius: 999px;"></div>'
            '</div>'
            '</div>'
            '<div style="padding: 8px 10px; background: #0A101A; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 14px; display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 28px; height: 28px; border-radius: 50%; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.7rem; color: #34D399; flex-shrink: 0;">LM</div>'
            '<div style="overflow: hidden;">'
            '<div style="font-size: 0.78rem; font-weight: 600; color: #FFFFFF; line-height: 1.15; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Leonardo Mesquita</div>'
            '<div style="font-size: 0.64rem; color: #64748B;">Gestor Municipal</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(rodape_sidebar_html, unsafe_allow_html=True)
