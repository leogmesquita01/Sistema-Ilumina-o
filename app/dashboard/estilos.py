"""
Módulo de Estilos Visuais Modernos (Streamlit)
Inspirado na identidade visual limpa, modo escuro elegante e fluído (estilo AgroGestão / DevLeads)
com foco na gestão de energia e iluminação pública de Boa Saúde / RN.
"""

import streamlit as st

def aplicar_estilos() -> None:
    """Aplica o tema escuro moderno com azul elétrico (#0284C7) e verde esmeralda (#10B981)."""
    st.markdown(
        """
        <style>
        /* Importação das fontes modernas */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');
        
        /* Tipografia Base Global */
        html, body, .stApp {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #F1F5F9;
            background-color: #0A0F18 !important;
        }

        p, label, input, textarea, select, button, .stMarkdown p {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Títulos com Montserrat marcante */
        h1, h2, h3, h4, h5, h6, .montserrat-title {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: #FFFFFF !important;
        }

        /* Códigos e Números com JetBrains Mono */
        .metric-mono, [data-testid="stMetricValue"], code, .jetbrains-mono {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }

        /* Preservação dos ícones Material Symbols do Streamlit */
        [data-testid*="Icon"],
        [data-testid*="icon"],
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-symbols-sharp,
        [class*="material-symbols"],
        [class*="material-icons"] {
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
            font-feature-settings: "liga" 1, "dlig" 1 !important;
            text-transform: none !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
            font-style: normal !important;
            display: inline-block !important;
            line-height: 1 !important;
        }

        /* Espaçamento superior da área principal */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px !important;
        }

        /* Cabeçalho transparente */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Sidebar Moderna Estilo Ilha / DevLeads */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
            padding-top: 1rem !important;
        }

        /* Menu de Navegação na Barra Lateral (Radio) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
            gap: 6px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 10px !important;
            padding: 9px 14px !important;
            margin-bottom: 3px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(2, 132, 199, 0.12) !important;
            border-color: rgba(2, 132, 199, 0.35) !important;
            transform: translateX(3px) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, rgba(2, 132, 199, 0.22), rgba(2, 132, 199, 0.06)) !important;
            border-color: #0284C7 !important;
            box-shadow: 0 0 16px rgba(2, 132, 199, 0.2) !important;
        }

        /* Cards e Containers com Bordas Suaves */
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }

        /* Inputs e Caixas de Texto */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            border-radius: 10px !important;
            background-color: #131F2E !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* Botões Primários */
        button[kind="primary"] {
            background: linear-gradient(135deg, #0284C7, #0369A1) !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 0.55rem 1.2rem !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
