"""
Ponto de Entrada Principal (Streamlit)
Ilumina Boa Saúde — Gestão e Mapeamento de Postes de Energia (COSERN / Boa Saúde - RN)
Sidebar Island flutuante fiel ao AgroGestão (Projeto-Ramon).
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from app.dashboard.estilos import aplicar_estilos
from app.database.conexao import inicializar_banco
from app.seed_data import seed_database
from app.servicos.dados_postes import obter_resumo_indicadores

# Telas Modulares
from app.dashboard.telas.mapa_postes import renderizar_tela_mapa
from app.dashboard.telas.solicitar_reparo import renderizar_tela_solicitar_reparo
from app.dashboard.telas.ordens_servico import renderizar_tela_ordens_servico
from app.dashboard.telas.importar_base import renderizar_tela_importar
from app.dashboard.telas.cadastrar_poste import renderizar_tela_cadastrar

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ilumina Boa Saúde — COSERN",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# 2. INICIALIZAÇÃO DO BANCO & ESTILOS VISUAIS
# -------------------------------------------------------------
inicializar_banco()
seed_database()
aplicar_estilos()

# -------------------------------------------------------------
# 3. BARRA LATERAL EM ILHA FLUTUANTE (SIDEBAR ISLAND)
# -------------------------------------------------------------
with st.sidebar:
    # Logo e Nome no topo da ilha com ícone neon
    logo_html = (
        '<div style="display: flex; align-items: center; gap: 11px; margin-bottom: 1.4rem; padding: 4px 2px 2px 2px;">'
        '<div style="width: 36px; height: 36px; border-radius: 11px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(16, 185, 129, 0.04)); border: 1.5px solid #10B981; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 16px rgba(16, 185, 129, 0.25);">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v20M5 5h14M7 9h10M9 13h6"/>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-family: \'Montserrat\', sans-serif; font-size: 1.15rem; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF; line-height: 1.1;">'
        'Ilumina <span style="color: #10B981;">Boa Saúde</span>'
        '</div>'
        '<div style="font-size: 10px; color: #8E8E93; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">'
        'Sec. de Infraestrutura'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(logo_html, unsafe_allow_html=True)

    # Menu de Navegação moderno (SEM o texto Navegação:)
    menu_opcoes = [
        ":material/map: Mapa e Postes",
        ":material/handyman: Solicitar reparo",
        ":material/assignment: Ordens de serviço",
        ":material/upload_file: Importar base COSERN",
        ":material/add_location_alt: Cadastrar poste",
    ]

    # Estado de navegação
    pagina_selecionada = st.session_state.get("pagina_atual", menu_opcoes[0])
    idx_padrao = menu_opcoes.index(pagina_selecionada) if pagina_selecionada in menu_opcoes else 0

    menu = st.radio(
        "",
        menu_opcoes,
        index=idx_padrao,
        label_visibility="collapsed",
    )
    st.session_state["pagina_atual"] = menu

    # Divisor sutil estilo DevLeads
    st.markdown(
        """<div style="height: 1px; background: rgba(255, 255, 255, 0.06); margin: 1.4rem 0 1.2rem 0;"></div>""",
        unsafe_allow_html=True,
    )

    # Cartão de Capacidade & Status com barras de progresso
    try:
        stats = obter_resumo_indicadores()
        total_postes = stats["total_postes"]
        taxa_led = int(stats["taxa_led"])
    except Exception:
        total_postes = 12
        taxa_led = 58

    meta_postes = 2000
    pct_rede = min(100, int((total_postes / meta_postes) * 100)) if total_postes > 0 else 5

    card_html = (
        '<div style="background: #111E1A; border: 1px solid rgba(16, 185, 129, 0.18); border-radius: 16px; padding: 14px 15px; margin-bottom: 1.5rem;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">Rede Mapeada</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #F4F4F5; font-weight: 600;">{total_postes:,} / {meta_postes:,}</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #1A2D27; border-radius: 2px; margin-bottom: 13px; overflow: hidden;">'
        f'<div style="width: {pct_rede}%; height: 100%; background: #10B981; border-radius: 2px; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">Parque em LED</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #F4F4F5; font-weight: 600;">{taxa_led}%</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #1A2D27; border-radius: 2px; margin-bottom: 13px; overflow: hidden;">'
        f'<div style="width: {taxa_led}%; height: 100%; background: #10B981; border-radius: 2px; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">Rede COSERN</span>'
        '<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #10B981; font-weight: 600;">Ativo • Online</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #1A2D27; border-radius: 2px; overflow: hidden;">'
        '<div style="width: 100%; height: 100%; background: #10B981; border-radius: 2px; box-shadow: 0 0 6px rgba(16, 185, 129, 0.4);"></div>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Perfil do Usuário no rodapé
    perfil_html = (
        '<div style="margin-top: auto; padding-top: 1.2rem; border-top: 1px solid rgba(255, 255, 255, 0.06);">'
        '<div style="font-family: \'Manrope\', sans-serif; font-size: 1.05rem; font-weight: 800; color: #FFFFFF; line-height: 1.2; letter-spacing: -0.3px;">'
        'Leonardo Mesquita'
        '</div>'
        '<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.65rem; font-weight: 600; color: #71717A; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px;">'
        'CRIADOR'
        '</div>'
        '</div>'
    )
    st.markdown(perfil_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. ROTEAMENTO DAS TELAS
# -------------------------------------------------------------
if menu == ":material/map: Mapa e Postes":
    renderizar_tela_mapa()
elif menu == ":material/handyman: Solicitar reparo":
    renderizar_tela_solicitar_reparo()
elif menu == ":material/assignment: Ordens de serviço":
    renderizar_tela_ordens_servico()
elif menu == ":material/upload_file: Importar base COSERN":
    renderizar_tela_importar()
elif menu == ":material/add_location_alt: Cadastrar poste":
    renderizar_tela_cadastrar()
