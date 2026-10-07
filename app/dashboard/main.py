"""
Ponto de Entrada Principal (Streamlit)
Gestão e Mapeamento de Postes de Energia (COSERN / Boa Saúde - RN)
Estruturado no mesmo padrão moderno, modular e elegante do AgroGestão (Projeto-Ramon).
"""

import os
import sys
from pathlib import Path

# Garante que o diretório raiz esteja no path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from app.dashboard.estilos import aplicar_estilos
from app.database.conexao import inicializar_banco
from app.seed_data import seed_database

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
    page_title="Iluminação Pública — Boa Saúde/RN",
    page_icon="⚡",
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
# 3. BARRA LATERAL (MENU DE NAVEGAÇÃO MODERNO ESTILO DEVLEADS)
# -------------------------------------------------------------
with st.sidebar:
    # Logo e Identidade Visual no topo da Sidebar
    logo_html = (
        '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; padding: 4px 2px;">'
        '<div style="width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg, rgba(2, 132, 199, 0.25), rgba(2, 132, 199, 0.05)); border: 1.5px solid #0284C7; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 16px rgba(2, 132, 199, 0.25);">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2v20M5 5h14M7 9h10M9 13h6"/>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-family: \'Montserrat\', sans-serif; font-size: 1.15rem; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF; line-height: 1.1;">'
        'Ilumina<span style="color: #0284C7;">Saúde</span>'
        '</div>'
        '<div style="font-size: 10px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">'
        'Boa Saúde / RN'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(logo_html, unsafe_allow_html=True)

    # Menu de Navegação Moderno com Material Symbols
    menu_opcoes = [
        ":material/map: Mapa e Postes",
        ":material/handyman: Solicitar reparo",
        ":material/assignment: Ordens de serviço",
        ":material/upload_file: Importar base COSERN",
        ":material/add_location_alt: Cadastrar poste",
    ]

    # Verifica se há redirecionamento de tela salvo na sessão
    pagina_selecionada = st.session_state.get("pagina_atual", menu_opcoes[0])

    menu = st.radio(
        "Navegação:",
        menu_opcoes,
        index=menu_opcoes.index(pagina_selecionada) if pagina_selecionada in menu_opcoes else 0,
        label_visibility="collapsed",
    )
    st.session_state["pagina_atual"] = menu

    # Divisor sutil
    st.markdown(
        """<div style="height: 1px; background: rgba(255, 255, 255, 0.07); margin: 1.5rem 0 1.2rem 0;"></div>""",
        unsafe_allow_html=True,
    )

    # Informações institucionais de rodapé na barra lateral
    st.markdown(
        """
        <div style="padding: 10px; background: rgba(255, 255, 255, 0.02); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.04); font-size: 11px; color: #94A3B8;">
            <b>Sec. de Infraestrutura</b><br>
            Rede: Neoenergia COSERN<br>
            Município: Boa Saúde / RN
        </div>
        """,
        unsafe_allow_html=True
    )

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
