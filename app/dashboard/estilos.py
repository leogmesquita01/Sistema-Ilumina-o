import streamlit as st


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

        :root {
            --bg-deep: #080D14;
            --bg-card: #0F1724;
            --bg-card-hover: #141F31;
            --bg-elevated: #172336;
            --border-subtle: rgba(255, 255, 255, 0.07);
            --border-emerald: rgba(16, 185, 129, 0.28);
            --emerald: #10B981;
            --emerald-dark: #059669;
            --emerald-glow: rgba(16, 185, 129, 0.18);
            --cyan: #0EA5E9;
            --amber: #F59E0B;
            --rose: #F43F5E;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --radius-lg: 18px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        html, body, .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary);
            background-color: var(--bg-deep) !important;
            background-image:
                radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.07) 0px, transparent 45%),
                radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.06) 0px, transparent 45%) !important;
            background-attachment: fixed !important;
            -webkit-font-smoothing: antialiased;
        }

        p, label, input, textarea, select, button, .stMarkdown p {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.025em;
            margin-top: 0 !important;
        }

        .mono, code, [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-variant-numeric: tabular-nums !important;
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
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1440px !important;
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

        /* =========================================================
           FLOATING SIDEBAR ISLAND (CLEAN OUTER SHELL)
           ========================================================= */
        section[data-testid="stSidebar"],
        section.stSidebar,
        [data-testid="stSidebar"] {
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            border-right: none !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            padding: 14px 10px 14px 14px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            z-index: 100 !important;
        }

        section[data-testid="stSidebar"]::before,
        section[data-testid="stSidebar"]::after {
            display: none !important;
            content: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background: linear-gradient(180deg, #0F1826 0%, #0B121D 100%) !important;
            border: 1px solid rgba(16, 185, 129, 0.28) !important;
            border-radius: 24px !important;
            height: calc(100vh - 28px) !important;
            max-height: calc(100vh - 28px) !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
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
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
            width: 0 !important;
            overflow: visible !important;
            z-index: 9999 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding: 1.4rem 1.15rem !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            border-radius: 24px !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            position: absolute !important;
            right: -13px !important;
            top: 26px !important;
            z-index: 999999 !important;
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
            background-color: #131F31 !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            cursor: pointer !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: #172A3A !important;
            border-color: #10B981 !important;
            transform: scale(1.1);
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.4) !important;
        }

        [data-testid="stSidebarCollapseButton"] button * {
            font-size: 13px !important;
            color: #94A3B8 !important;
            fill: #94A3B8 !important;
        }

        /* Sidebar Navigation Pills (Remove radio circle & widget label) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 6px !important;
            display: flex !important;
            flex-direction: column !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            width: 100% !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 12px !important;
            padding: 10px 13px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: flex !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: #94A3B8 !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            transition: color 0.18s ease !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.04) !important;
            border-color: rgba(255, 255, 255, 0.06) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.18) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.14) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #10B981 !important;
            font-weight: 700 !important;
        }

        /* =========================================================
           COMMAND HERO HEADER
           ========================================================= */
        .command-hero {
            background: linear-gradient(135deg, rgba(15, 23, 36, 0.95) 0%, rgba(19, 32, 48, 0.85) 100%);
            border: 1px solid rgba(16, 185, 129, 0.24);
            border-left: 4px solid #10B981;
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            margin-bottom: 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(16, 185, 129, 0.12);
            color: #34D399;
            padding: 4px 11px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            border: 1px solid rgba(16, 185, 129, 0.3);
            margin-bottom: 8px;
        }

        .hero-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 10px #10B981;
        }

        .hero-title {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.75rem !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            margin: 0 0 4px 0 !important;
            letter-spacing: -0.02em !important;
            line-height: 1.15 !important;
        }

        .hero-subtitle {
            font-size: 0.88rem;
            color: var(--text-secondary);
            margin: 0;
        }

        .hero-right {
            text-align: right;
            background: rgba(8, 13, 20, 0.55);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 10px 16px;
        }

        /* =========================================================
           BENTO KPI CARDS GRID
           ========================================================= */
        .bento-kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }

        .bento-kpi-card {
            background: linear-gradient(180deg, #111A29 0%, #0D1420 100%);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .bento-kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(16, 185, 129, 0.35);
        }

        .bento-kpi-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .bento-kpi-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .bento-kpi-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .bento-kpi-icon.emerald {
            background: rgba(16, 185, 129, 0.14);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34D399;
        }

        .bento-kpi-icon.cyan {
            background: rgba(14, 165, 233, 0.14);
            border: 1px solid rgba(14, 165, 233, 0.3);
            color: #38BDF8;
        }

        .bento-kpi-icon.amber {
            background: rgba(245, 158, 11, 0.14);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #FBBF24;
        }

        .bento-kpi-icon.rose {
            background: rgba(244, 63, 94, 0.14);
            border: 1px solid rgba(244, 63, 94, 0.3);
            color: #FB7185;
        }

        .bento-kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
            font-size: 1.85rem;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.1;
            margin-bottom: 8px;
        }

        .bento-kpi-bar {
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .bento-kpi-bar-fill {
            height: 100%;
            border-radius: 999px;
        }

        .bento-kpi-sub {
            font-size: 0.76rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* =========================================================
           BENTO PANELS & DOSSIER CARDS
           ========================================================= */
        .panel-card {
            background: linear-gradient(180deg, #111A29 0%, #0D1420 100%);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .panel-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.02rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .panel-meta {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            background: rgba(255, 255, 255, 0.04);
            padding: 3px 9px;
            border-radius: 999px;
            border: 1px solid var(--border-subtle);
        }

        /* Mini Spec Grid inside Dossier */
        .spec-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 14px 0;
        }

        .spec-tile {
            background: rgba(8, 13, 20, 0.6);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 11px 13px;
        }

        .spec-tile-label {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .spec-tile-val {
            font-size: 0.92rem;
            font-weight: 700;
            color: #F8FAFC;
        }

        /* Key-Value List */
        .kv-list {
            display: flex;
            flex-direction: column;
        }

        .kv-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding: 9px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.85rem;
            gap: 12px;
        }

        .kv-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .kv-key {
            color: var(--text-secondary);
        }

        .kv-val {
            color: var(--text-primary);
            text-align: right;
            font-weight: 600;
        }

        /* Status Badges */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            height: 24px;
            padding: 0 10px;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            white-space: nowrap;
        }

        .status-pill.positive {
            background: rgba(16, 185, 129, 0.14);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }

        .status-pill.warning {
            background: rgba(245, 158, 11, 0.14);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }

        .status-pill.negative {
            background: rgba(244, 63, 94, 0.14);
            color: #FB7185;
            border: 1px solid rgba(244, 63, 94, 0.35);
        }

        .status-pill.neutral {
            background: rgba(148, 163, 184, 0.12);
            color: #CBD5E1;
            border: 1px solid rgba(148, 163, 184, 0.25);
        }

        /* Material Chip Tags */
        .chip-group {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .mat-chip {
            background: rgba(14, 165, 233, 0.1);
            border: 1px solid rgba(14, 165, 233, 0.25);
            color: #7DD3FC;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 8px;
        }

        /* Clean Modern Table */
        .clean-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }

        .clean-table th {
            text-align: left;
            font-size: 0.74rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted);
            padding: 9px 10px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .clean-table th.num, .clean-table td.num {
            text-align: right;
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }

        .clean-table td {
            padding: 11px 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: var(--text-primary);
            vertical-align: middle;
        }

        .clean-table tr:last-child td {
            border-bottom: none;
        }

        /* Bar List */
        .bar-list-row {
            margin-bottom: 12px;
        }

        .bar-list-row:last-child {
            margin-bottom: 0;
        }

        .bar-list-top {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            font-weight: 500;
            margin-bottom: 5px;
        }

        .bar-list-track {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-list-fill {
            height: 100%;
            background: linear-gradient(90deg, #10B981 0%, #0EA5E9 100%);
            border-radius: 999px;
        }

        /* Inputs, Forms & Buttons */
        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] {
            border-radius: 10px !important;
            background-color: #0B121E !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: #10B981 !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
        }

        .stTextInput label, .stSelectbox label, .stNumberInput label, .stTextArea label, .stFileUploader label {
            font-size: 0.84rem !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;
        }

        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(52, 211, 153, 0.4) !important;
            border-radius: 11px !important;
            font-weight: 700 !important;
            font-size: 0.88rem !important;
            min-height: 40px !important;
            padding: 0 18px !important;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.28) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"] *,
        [data-testid="stFormSubmitButton"] button * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.42) !important;
        }

        button[kind="secondary"],
        .stDownloadButton button,
        .stLinkButton a {
            background: #131E30 !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 11px !important;
            font-weight: 600 !important;
            font-size: 0.86rem !important;
            min-height: 40px !important;
            transition: all 0.18s ease !important;
            text-decoration: none !important;
        }

        button[kind="secondary"]:hover,
        .stDownloadButton button:hover,
        .stLinkButton a:hover {
            border-color: rgba(16, 185, 129, 0.45) !important;
            background: #17263C !important;
        }

        div[data-testid="stForm"] {
            background: linear-gradient(180deg, #111A29 0%, #0D1420 100%) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 18px !important;
            padding: 24px !important;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4) !important;
        }

        iframe {
            border: 1px solid rgba(16, 185, 129, 0.22) !important;
            border-radius: 16px !important;
            display: block !important;
            width: 100% !important;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45) !important;
        }

        @media (max-width: 900px) {
            .bento-kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
