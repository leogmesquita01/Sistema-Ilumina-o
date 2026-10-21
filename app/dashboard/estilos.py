import streamlit as st

def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');
        
        html, body, .stApp {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #F1F5F9;
            background-color: #0C1412 !important;
        }

        p, label, input, textarea, select, button, .stMarkdown p {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        h1, h2, h3, h4, h5, h6, .montserrat-title {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: #FFFFFF !important;
        }

        .metric-mono, [data-testid="stMetricValue"], code, .jetbrains-mono {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }

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

        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            pointer-events: none;
        }

        #MainMenu, 
        [data-testid="stMainMenu"], 
        footer, 
        [data-testid="stDecoration"], 
        [data-testid="stStatusWidget"],
        .stDeployButton,
        [data-testid="stAppDeployButton"],
        [data-testid="stToolbarActions"] {
            display: none !important;
            visibility: hidden !important;
        }

        section[data-testid="stSidebar"] {
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            padding: 14px 10px 14px 14px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            z-index: 100 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #111E1A !important;
            border: 1px solid rgba(16, 185, 129, 0.18) !important;
            border-radius: 24px !important;
            height: calc(100vh - 28px) !important;
            max-height: calc(100vh - 28px) !important;
            box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85) !important;
            display: flex !important;
            flex-direction: column !important;
            position: relative !important;
            overflow: visible !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
            width: 0 !important;
            overflow: visible !important;
            z-index: 9999 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding: 1.4rem 1.1rem !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            border-radius: 24px !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
            width: 4px;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            position: absolute !important;
            right: -13px !important;
            top: 24px !important;
            z-index: 999999 !important;
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            width: 26px !important;
            height: 26px !important;
        }

        [data-testid="stSidebarCollapseButton"] button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 26px !important;
            height: 26px !important;
            border-radius: 50% !important;
            background-color: #152420 !important;
            border: 1px solid rgba(16, 185, 129, 0.25) !important;
            cursor: pointer !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: #1A3327 !important;
            border-color: #10B981 !important;
            transform: scale(1.12);
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.4) !important;
        }

        [data-testid="stSidebarCollapseButton"] button * {
            font-size: 13px !important;
            color: #94A3B8 !important;
            fill: #94A3B8 !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover * {
            color: #10B981 !important;
            fill: #10B981 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 4px !important;
            display: flex !important;
            flex-direction: column !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label span[data-testid="stRadioButtonCustomObject"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            width: 100% !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 12px !important;
            padding: 9px 12px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.18s ease-in-out !important;
            display: flex !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
            font-family: 'Manrope', sans-serif !important;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            color: #8E8E93 !important;
            transition: color 0.18s ease-in-out !important;
            margin: 0 !important;
            letter-spacing: -0.2px !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.04) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: rgba(16, 185, 129, 0.14) !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.15) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #10B981 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stMetric"] {
            background: #111E1A !important;
            border: 1px solid rgba(16, 185, 129, 0.18) !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }

        .hero-banner {
            background: linear-gradient(90deg, #13221C 0%, #1A3327 100%);
            border-left: 4px solid #10B981;
            border-radius: 14px;
            padding: 1.1rem 1.4rem;
            margin-bottom: 1.5rem;
            border-top: 1px solid rgba(16, 185, 129, 0.18);
            border-right: 1px solid rgba(16, 185, 129, 0.18);
            border-bottom: 1px solid rgba(16, 185, 129, 0.18);
        }

        div[data-baseweb="input"], div[data-baseweb="select"] {
            border-radius: 10px !important;
            background-color: #14241F !important;
            border-color: rgba(16, 185, 129, 0.2) !important;
        }

        button[kind="primary"] {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            padding: 0.65rem 1.4rem !important;
            box-shadow: 0 4px 18px rgba(16, 185, 129, 0.35) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 24px rgba(16, 185, 129, 0.5) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
