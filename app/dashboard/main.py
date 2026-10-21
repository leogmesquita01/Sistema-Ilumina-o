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
        '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; padding: 4px 2px;">'
        '<div style="width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.28), rgba(14, 165, 233, 0.08)); border: 1.5px solid #10B981; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(16, 185, 129, 0.28); flex-shrink: 0;">'
        '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v20M5 5h14M7 9h10M9 13h6"/>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-family: \'Outfit\', sans-serif; font-size: 1.18rem; font-weight: 800; letter-spacing: -0.4px; color: #FFFFFF; line-height: 1.1;">'
        'Ilumina <span style="color: #10B981;">Boa Saúde</span>'
        '</div>'
        '<div style="font-size: 10.5px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 3px;">'
        'Sec. de Infraestrutura'
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

    pagina_selecionada = st.session_state.get("pagina_atual", menu_opcoes[0])
    mapa_antigo = {
        ":material/map: Mapa e Postes": menu_opcoes[0],
        ":material/upload_file: Importar base COSERN": menu_opcoes[4],
    }
    pagina_selecionada = mapa_antigo.get(pagina_selecionada, pagina_selecionada)
    idx_padrao = menu_opcoes.index(pagina_selecionada) if pagina_selecionada in menu_opcoes else 0

    menu = st.radio(
        "Navegação",
        menu_opcoes,
        index=idx_padrao,
        label_visibility="collapsed",
    )
    st.session_state["pagina_atual"] = menu

    st.markdown(
        '<div style="height: 1px; background: rgba(255, 255, 255, 0.07); margin: 1.3rem 0 1.1rem 0;"></div>',
        unsafe_allow_html=True,
    )

    total_os = os_abertas + os_concluidas
    taxa_resolucao = int(round((os_concluidas / total_os) * 100)) if total_os > 0 else 100

    card_html = (
        '<div style="background: rgba(8, 13, 20, 0.65); border: 1px solid rgba(16, 185, 129, 0.22); border-radius: 16px; padding: 15px 16px; margin-bottom: 1.2rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 11px;">'
        '<span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399;">Telemetria da Base</span>'
        '<span style="display: inline-flex; align-items: center; gap: 5px; font-size: 0.7rem; color: #94A3B8;"><span style="width: 6px; height: 6px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></span>Supabase</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Postes Cadastrados</span>'
        f'<span class="mono" style="font-size: 0.82rem; color: #F8FAFC; font-weight: 700;">{total_postes}</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; margin-top: 10px;">'
        '<span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Eficiência LED</span>'
        f'<span class="mono" style="font-size: 0.8rem; color: #34D399; font-weight: 700;">{taxa_led}%</span>'
        '</div>'
        '<div style="width: 100%; height: 5px; background: rgba(255,255,255,0.07); border-radius: 999px; margin-bottom: 12px; overflow: hidden;">'
        f'<div style="width: {taxa_led}%; height: 100%; background: linear-gradient(90deg, #10B981, #0EA5E9); border-radius: 999px;"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Taxa de Resolução O.S.</span>'
        f'<span class="mono" style="font-size: 0.8rem; color: #38BDF8; font-weight: 700;">{taxa_resolucao}%</span>'
        '</div>'
        '<div style="width: 100%; height: 5px; background: rgba(255,255,255,0.07); border-radius: 999px; overflow: hidden;">'
        f'<div style="width: {taxa_resolucao}%; height: 100%; background: linear-gradient(90deg, #0EA5E9, #38BDF8); border-radius: 999px;"></div>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    perfil_html = (
        '<div style="margin-top: auto; padding-top: 1.1rem; border-top: 1px solid rgba(255, 255, 255, 0.07); display: flex; align-items: center; gap: 10px;">'
        '<div style="width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #17263C, #0F1826); border: 1px solid rgba(255,255,255,0.12); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.78rem; color: #34D399;">LM</div>'
        '<div>'
        '<div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Leonardo Mesquita</div>'
        '<div class="mono" style="font-size: 0.65rem; font-weight: 600; color: #64748B; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px;">CRIADOR · GESTOR</div>'
        '</div>'
        '</div>'
    )
    st.markdown(perfil_html, unsafe_allow_html=True)

if menu == ":material/map: Mapa e postes":
    renderizar_tela_mapa()
elif menu == ":material/handyman: Solicitar reparo":
    renderizar_tela_solicitar_reparo()
elif menu == ":material/assignment: Ordens de serviço":
    renderizar_tela_ordens_servico()
elif menu == ":material/add_location_alt: Cadastrar poste":
    renderizar_tela_cadastrar()
elif menu == ":material/upload_file: Importar planilha":
    renderizar_tela_importar()
