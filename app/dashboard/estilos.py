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
            --border-subtle: rgba(255, 255, 255, 0.06);
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
            --radius-xl: 24px;
            --radius-lg: 20px;
            --radius-md: 14px;
            --radius-sm: 10px;
        }

        html, body, .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary);
            background-color: var(--bg-deep) !important;
            background-image:
                radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.06) 0px, transparent 45%),
                radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 45%) !important;
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
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
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

        @keyframes v14FadeUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* =========================================================
           FLOATING SIDEBAR ISLAND (V14 MINIMAL SHELL)
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
            background: #0D1522 !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 26px !important;
            height: calc(100vh - 28px) !important;
            max-height: calc(100vh - 28px) !important;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
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
            border-radius: 26px !important;
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
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            cursor: pointer !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: #10B981 !important;
            border-color: #10B981 !important;
            transform: scale(1.08);
        }

        [data-testid="stSidebarCollapseButton"] button * {
            font-size: 13px !important;
            color: #F8FAFC !important;
            fill: #F8FAFC !important;
        }

        /* Sidebar Navigation Pills — V14 Capsule Style */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 6px !important;
            display: flex !important;
            flex-direction: column !important;
            background: rgba(8, 13, 20, 0.55) !important;
            padding: 6px !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
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
            font-size: 0.88rem !important;
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
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: #172336 !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) [data-testid="stIconMaterial"] {
            color: #10B981 !important;
        }

        /* =========================================================
           V14 GREETING HEADER (MODERN & MINIMAL UI)
           ========================================================= */
        .v14-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
            padding-bottom: 4px;
            animation: v14FadeUp 0.35s ease-out both;
        }

        .v14-greeting-title {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.95rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            margin: 0 0 4px 0 !important;
            letter-spacing: -0.03em !important;
            line-height: 1.15 !important;
        }

        .v14-greeting-sub {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin: 0;
            font-weight: 400;
        }

        .v14-header-pills {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .v14-sync-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 0.78rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        /* Legacy command-hero fallback adapted to V14 */
        .command-hero {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 22px 26px;
            margin-bottom: 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            animation: v14FadeUp 0.35s ease-out both;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(16, 185, 129, 0.1);
            color: #34D399;
            padding: 4px 11px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.03em;
            border: 1px solid rgba(16, 185, 129, 0.24);
            margin-bottom: 8px;
        }

        .hero-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
        }

        .hero-title {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.65rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            margin: 0 0 4px 0 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.15 !important;
        }

        .hero-subtitle {
            font-size: 0.88rem;
            color: var(--text-secondary);
            margin: 0;
        }

        .hero-right {
            text-align: right;
            background: #0A101A;
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 12px 18px;
        }

        /* =========================================================
           V14 OVERVIEW BENTO GRID (3-COLUMN VERTO LAYOUT)
           ========================================================= */
        .v14-overview-grid {
            display: grid;
            grid-template-columns: 1.15fr 1fr 1.25fr;
            gap: 16px;
            margin-bottom: 22px;
            animation: v14FadeUp 0.45s ease-out both;
        }

        .v14-balance-card {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
            position: relative;
            overflow: hidden;
        }

        .v14-card-label {
            font-size: 0.84rem;
            color: var(--text-secondary);
            font-weight: 500;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .v14-big-number {
            font-family: 'Outfit', sans-serif;
            font-variant-numeric: tabular-nums;
            font-size: 2.75rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.03em;
            line-height: 1.05;
            margin: 12px 0 8px 0;
        }

        .v14-trend-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.14);
            color: #34D399;
        }

        .v14-action-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 18px;
        }

        .v14-btn-dark {
            background: #172336;
            color: #F8FAFC;
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
        }

        .v14-btn-emerald {
            background: #10B981;
            color: #06281E;
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 0.8rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
        }

        /* 2x2 Mini Stat Grid (Verto signature with 1 featured solid accent card) */
        .v14-stat-2x2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 12px;
        }

        .v14-mini-stat {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 16px 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .v14-mini-stat:hover {
            transform: translateY(-2px);
            border-color: rgba(16, 185, 129, 0.35);
        }

        .v14-mini-stat.featured {
            background: linear-gradient(145deg, #10B981 0%, #059669 100%);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 12px 28px rgba(16, 185, 129, 0.25);
        }

        .v14-mini-stat.featured .v14-mini-label {
            color: rgba(255, 255, 255, 0.88);
        }

        .v14-mini-stat.featured .v14-mini-val {
            color: #FFFFFF;
        }

        .v14-mini-stat.featured .v14-mini-sub {
            color: rgba(255, 255, 255, 0.82);
        }

        .v14-mini-label {
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .v14-mini-val {
            font-family: 'Outfit', sans-serif;
            font-variant-numeric: tabular-nums;
            font-size: 1.65rem;
            font-weight: 700;
            color: #FFFFFF;
            margin: 6px 0 2px 0;
            line-height: 1.1;
        }

        .v14-mini-sub {
            font-size: 0.72rem;
            color: var(--text-muted);
            font-weight: 500;
        }

        /* Vertical Bar Chart Card (Total Income style from V14) */
        .v14-chart-card {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
        }

        .v14-bars-wrap {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 12px;
            height: 126px;
            padding-top: 18px;
            margin-top: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 10px;
        }

        .v14-bar-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
            justify-content: flex-end;
            gap: 6px;
        }

        .v14-bar-pair {
            display: flex;
            align-items: flex-end;
            gap: 4px;
            height: 92px;
            width: 100%;
            justify-content: center;
        }

        .v14-bar-pill {
            width: 12px;
            border-radius: 6px 6px 3px 3px;
            transition: height 0.3s ease;
        }

        .v14-bar-lbl {
            font-size: 0.7rem;
            color: var(--text-secondary);
            max-width: 64px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: center;
        }

        /* Radial / Donut Goal Cards (Savings & Goals style from V14) */
        .v14-goals-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }

        .v14-goal-card {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 16px 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .v14-goal-card:hover {
            transform: translateY(-2px);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .v14-ring {
            width: 68px;
            height: 68px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 10px 0;
            position: relative;
        }

        .v14-ring-inner {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: #0F1724;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Outfit', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: #FFFFFF;
        }

        /* Realism Asset Pass Card (Manage Card style from V14) */
        .v14-asset-pass {
            background: linear-gradient(135deg, #162235 0%, #090F1A 60%, #0D1F22 100%);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 22px;
            padding: 22px 24px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
            margin-bottom: 14px;
        }

        .v14-asset-pass::after {
            content: "";
            position: absolute;
            right: -30px;
            bottom: -40px;
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, transparent 70%);
            pointer-events: none;
        }

        /* =========================================================
           BENTO KPI CARDS GRID (SECONDARY SCREENS)
           ========================================================= */
        .bento-kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
            animation: v14FadeUp 0.4s ease-out both;
        }

        .bento-kpi-card {
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
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
            font-weight: 500;
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
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.25);
            color: #34D399;
        }

        .bento-kpi-icon.cyan {
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(14, 165, 233, 0.25);
            color: #38BDF8;
        }

        .bento-kpi-icon.amber {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.25);
            color: #FBBF24;
        }

        .bento-kpi-icon.rose {
            background: rgba(244, 63, 94, 0.12);
            border: 1px solid rgba(244, 63, 94, 0.25);
            color: #FB7185;
        }

        .bento-kpi-value {
            font-family: 'Outfit', sans-serif;
            font-variant-numeric: tabular-nums;
            font-size: 1.95rem;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.1;
            margin-bottom: 10px;
        }

        .bento-kpi-bar {
            width: 100%;
            height: 5px;
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
            background: #0F1724;
            border: 1px solid var(--border-subtle);
            border-radius: 22px;
            padding: 22px 24px;
            margin-bottom: 16px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
            animation: v14FadeUp 0.45s ease-out both;
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
            padding: 4px 10px;
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
            background: #0A101A;
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 12px 14px;
        }

        .spec-tile-label {
            font-size: 0.72rem;
            color: var(--text-muted);
            font-weight: 500;
            margin-bottom: 4px;
        }

        .spec-tile-val {
            font-size: 0.92rem;
            font-weight: 700;
            color: #F8FAFC;
        }

        /* Key-Value List / V14 Card Controls style */
        .kv-list {
            display: flex;
            flex-direction: column;
        }

        .kv-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
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

        /* Recent Activities List (V14 Activity Feed style) */
        .v14-activity-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 11px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            gap: 12px;
        }

        .v14-activity-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .v14-activity-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .v14-avatar {
            width: 38px;
            height: 38px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
            font-weight: 700;
            flex-shrink: 0;
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
            font-weight: 600;
            white-space: nowrap;
        }

        .status-pill.positive {
            background: rgba(16, 185, 129, 0.14);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-pill.warning {
            background: rgba(245, 158, 11, 0.14);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .status-pill.negative {
            background: rgba(244, 63, 94, 0.14);
            color: #FB7185;
            border: 1px solid rgba(244, 63, 94, 0.3);
        }

        .status-pill.neutral {
            background: rgba(148, 163, 184, 0.12);
            color: #CBD5E1;
            border: 1px solid rgba(148, 163, 184, 0.22);
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
            border: 1px solid rgba(14, 165, 233, 0.24);
            color: #7DD3FC;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 999px;
        }

        /* Clean Modern Table */
        .clean-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }

        .clean-table th {
            text-align: left;
            font-size: 0.75rem;
            font-weight: 500;
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
            border-radius: 12px !important;
            background-color: #0B121E !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: #10B981 !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
        }

        .stTextInput label, .stSelectbox label, .stNumberInput label, .stTextArea label, .stFileUploader label {
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            color: #94A3B8 !important;
        }

        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background: #10B981 !important;
            color: #052016 !important;
            border: 1px solid rgba(52, 211, 153, 0.4) !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 0.86rem !important;
            min-height: 40px !important;
            padding: 0 18px !important;
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.24) !important;
            transition: all 0.2s ease !important;
        }

        button[kind="primary"] *,
        [data-testid="stFormSubmitButton"] button * {
            color: #052016 !important;
            font-weight: 700 !important;
        }

        button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background: #34D399 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.35) !important;
        }

        button[kind="secondary"],
        .stDownloadButton button,
        .stLinkButton a {
            background: #131E30 !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
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
            background: #0F1724 !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 22px !important;
            padding: 24px !important;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28) !important;
        }

        iframe {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 20px !important;
            display: block !important;
            width: 100% !important;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35) !important;
        }

        @media (max-width: 1024px) {
            .v14-overview-grid {
                grid-template-columns: 1fr;
            }
            .bento-kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .v14-goals-grid {
                grid-template-columns: 1fr;
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
