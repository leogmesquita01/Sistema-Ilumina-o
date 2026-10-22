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

with st.sidebar:
    logo_html = (
        '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.15rem; padding: 2px;">'
        '<div style="width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.28), rgba(14, 165, 233, 0.08)); border: 1.5px solid #10B981; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 16px rgba(16, 185, 129, 0.25); flex-shrink: 0;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v20M5 5h14M7 9h10M9 13h6"/>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-family: \'Outfit\', sans-serif; font-size: 1.02rem; font-weight: 800; letter-spacing: -0.3px; color: #FFFFFF; line-height: 1.1;">'
        'Ilumina <span style="color: #10B981;">Boa Saúde</span>'
        '</div>'
        '<div style="font-size: 9.5px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">'
        'Infraestrutura'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(logo_html, unsafe_allow_html=True)

    menu_opcoes = [
        ":material/map: Mapa e postes",
        ":material/handyman: Solicitar reparo",
        ":material/assignment: Ordens de serviço",
        ":material/add_location_alt: Cadastrar poste",
        ":material/upload_file: Importar planilha",
    ]

    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = menu_opcoes[0]

    mapa_antigo = {
        ":material/map: Mapa e Postes": menu_opcoes[0],
        ":material/upload_file: Importar base COSERN": menu_opcoes[4],
    }
    st.session_state["pagina_atual"] = mapa_antigo.get(
        st.session_state["pagina_atual"], st.session_state["pagina_atual"]
    )
    if st.session_state["pagina_atual"] not in menu_opcoes:
        st.session_state["pagina_atual"] = menu_opcoes[0]

    st.session_state["nav_desktop"] = st.session_state["pagina_atual"]
    st.session_state["nav_mobile"] = st.session_state["pagina_atual"]

    def _ao_mudar_desktop() -> None:
        st.session_state["pagina_atual"] = st.session_state["nav_desktop"]

    def _ao_mudar_mobile() -> None:
        st.session_state["pagina_atual"] = st.session_state["nav_mobile"]

    st.radio(
        "Navegação Desktop",
        menu_opcoes,
        key="nav_desktop",
        on_change=_ao_mudar_desktop,
        label_visibility="collapsed",
    )

    st.markdown(
        '<div style="height: 1px; background: rgba(255, 255, 255, 0.06); margin: 1rem 0 0.9rem 0;"></div>',
        unsafe_allow_html=True,
    )

    total_os = os_abertas + os_concluidas
    taxa_resolucao = int(round((os_concluidas / total_os) * 100)) if total_os > 0 else 100

    card_html = (
        '<div style="background: #0A101A; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 16px; padding: 12px 14px; margin-bottom: 1rem;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
        '<span style="font-size: 0.72rem; font-weight: 600; color: #F8FAFC;">Telemetria</span>'
        '<span style="display: inline-flex; align-items: center; gap: 4px; font-size: 0.65rem; color: #34D399; background: rgba(16, 185, 129, 0.12); padding: 2px 7px; border-radius: 999px; font-weight: 600;"><span style="width: 5px; height: 5px; border-radius: 50%; background: #10B981;"></span>Ativo</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
        '<span style="font-size: 0.74rem; color: #94A3B8;">Postes</span>'
        f'<span class="mono" style="font-size: 0.78rem; color: #F8FAFC; font-weight: 700;">{total_postes}</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; margin-top: 8px;">'
        '<span style="font-size: 0.74rem; color: #94A3B8;">LED</span>'
        f'<span class="mono" style="font-size: 0.74rem; color: #34D399; font-weight: 700;">{taxa_led}%</span>'
        '</div>'
        '<div style="width: 100%; height: 5px; background: rgba(255,255,255,0.06); border-radius: 999px; margin-bottom: 10px; overflow: hidden;">'
        f'<div style="width: {taxa_led}%; height: 100%; background: #10B981; border-radius: 999px;"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
        '<span style="font-size: 0.74rem; color: #94A3B8;">Resolução O.S.</span>'
        f'<span class="mono" style="font-size: 0.74rem; color: #38BDF8; font-weight: 700;">{taxa_resolucao}%</span>'
        '</div>'
        '<div style="width: 100%; height: 5px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden;">'
        f'<div style="width: {taxa_resolucao}%; height: 100%; background: #0EA5E9; border-radius: 999px;"></div>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    perfil_html = (
        '<div style="margin-top: auto; padding: 8px 10px; background: #0A101A; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 14px; display: flex; align-items: center; gap: 8px;">'
        '<div style="width: 30px; height: 30px; border-radius: 50%; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.72rem; color: #34D399; flex-shrink: 0;">LM</div>'
        '<div style="overflow: hidden;">'
        '<div style="font-size: 0.8rem; font-weight: 600; color: #FFFFFF; line-height: 1.15; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Leonardo Mesquita</div>'
        '<div style="font-size: 0.65rem; color: #64748B; margin-top: 1px;">Gestor Municipal</div>'
        '</div>'
        '</div>'
    )
    st.markdown(perfil_html, unsafe_allow_html=True)

mobile_topbar_html = (
    '<div class="v14-mobile-topbar">'
    '<div style="display: flex; align-items: center; gap: 10px;">'
    '<div style="width: 32px; height: 32px; border-radius: 10px; background: rgba(16, 185, 129, 0.2); border: 1.5px solid #10B981; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">'
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M5 5h14M7 9h10M9 13h6"/></svg>'
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
        "Navegação Mobile",
        menu_opcoes,
        key="nav_mobile",
        on_change=_ao_mudar_mobile,
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
