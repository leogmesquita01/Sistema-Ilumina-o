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
    page_icon=":material/tungsten:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicializar_banco()
aplicar_estilos()

try:
    stats = obter_resumo_indicadores()
    total_postes = stats["total_postes"]
    total_led = stats["total_led"]
    taxa_led = stats["taxa_led"]
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
except Exception:
    total_postes = 0
    total_led = 0
    taxa_led = 0.0
    total_chamados = 0
    os_abertas = 0

with st.sidebar:
    brand_html = (
        '<div style="display: flex; align-items: center; gap: 10px; padding: 2px 4px 18px 4px; border-bottom: 1px solid #222224; margin-bottom: 16px;">'
        '<div style="width: 30px; height: 30px; border-radius: 6px; background: #212023; border: 1px solid #3a3a3e; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4a8ad6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v20M5 6h14M7 10h10M9 14h6"/>'
        '</svg>'
        '</div>'
        '<div style="min-width: 0;">'
        '<div style="font-size: 14px; font-weight: 600; color: #ffffff; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
        'Ilumina Boa Saúde'
        '</div>'
        '<div style="font-size: 11.5px; color: #8a8c92; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
        'Boa Saúde / RN · Infraestrutura'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(brand_html, unsafe_allow_html=True)

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
        '<div style="height: 1px; background: #222224; margin: 18px 0 16px 0;"></div>',
        unsafe_allow_html=True,
    )

    cor_chamados = "#e5566f" if total_chamados > 0 else "#8a8c92"
    well_html = (
        '<div style="background: #171719; border: 1px solid #222224; border-radius: 6px; padding: 12px 14px; margin-bottom: 16px;">'
        '<div style="font-size: 12px; color: #8a8c92; margin-bottom: 10px; font-weight: 500;">Base municipal</div>'
        '<div style="display: flex; justify-content: space-between; align-items: baseline; padding: 5px 0; border-bottom: 1px solid #1b1a1f; font-size: 12.5px;">'
        '<span style="color: #8a8c92;">Postes cadastrados</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-variant-numeric: tabular-nums; color: #ffffff; font-weight: 500;">{total_postes}</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: baseline; padding: 5px 0; border-bottom: 1px solid #1b1a1f; font-size: 12.5px;">'
        '<span style="color: #8a8c92;">Parque em LED</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-variant-numeric: tabular-nums; color: #ffffff; font-weight: 500;">{taxa_led}% <span style="color: #8a8c92; font-size: 11px;">({total_led})</span></span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: baseline; padding: 5px 0; border-bottom: 1px solid #1b1a1f; font-size: 12.5px;">'
        '<span style="color: #8a8c92;">Chamados ativos</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-variant-numeric: tabular-nums; color: {cor_chamados}; font-weight: 500;">{total_chamados}</span>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: baseline; padding: 5px 0 0 0; font-size: 12.5px;">'
        '<span style="color: #8a8c92;">O.S. abertas</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-variant-numeric: tabular-nums; color: #ffffff; font-weight: 500;">{os_abertas}</span>'
        '</div>'
        '</div>'
    )
    st.markdown(well_html, unsafe_allow_html=True)

    perfil_html = (
        '<div style="margin-top: auto; padding-top: 14px; border-top: 1px solid #222224; display: flex; justify-content: space-between; align-items: center;">'
        '<div>'
        '<div style="font-size: 13px; font-weight: 500; color: #ffffff; line-height: 1.2;">Leonardo Mesquita</div>'
        '<div style="font-size: 11.5px; color: #8a8c92; margin-top: 2px;">Secretaria de Infraestrutura</div>'
        '</div>'
        '<span class="status-pill positive">Supabase</span>'
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
