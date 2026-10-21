import streamlit as st


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Public+Sans:wght@400;500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

        :root {
            --ground: #171719;
            --surface: #131217;
            --raised: #212023;
            --border: #222224;
            --rule: #1b1a1f;
            --control: #3a3a3e;
            --text: #ffffff;
            --muted: #8a8c92;
            --accent: #4a8ad6;
            --positive: #44a282;
            --negative: #e5566f;
            --warning: #d9a441;
            --pill-positive-bg: #1b2828;
            --pill-positive-ink: #5fc39c;
            --pill-negative-bg: #2c1a20;
            --pill-negative-ink: #e5566f;
            --pill-warning-bg: #2a2416;
            --pill-warning-ink: #d9a441;
            --pill-neutral-bg: #212023;
            --pill-neutral-ink: #bdbdc0;
            --radius-card: 6px;
            --radius-control: 6px;
            --gap: 24px;
            --pad: 32px;
        }

        html, body, .stApp {
            font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
            color: var(--text);
            background-color: var(--ground) !important;
            font-size: 13px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        p, label, input, textarea, select, button, .stMarkdown p {
            font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Public Sans', sans-serif !important;
            color: var(--text) !important;
            letter-spacing: -0.02em;
            margin-top: 0 !important;
        }

        .num, code, .mono, [data-testid="stMetricValue"] {
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
            padding-top: 28px !important;
            padding-bottom: 48px !important;
            padding-left: 32px !important;
            padding-right: 32px !important;
            max-width: 1360px !important;
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

        /* Sidebar — Ruled dark frame (#131217 surface on #171719 ground, 1px #222224 edge) */
        section[data-testid="stSidebar"] {
            background-color: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
            padding: 0 !important;
            z-index: 100 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: var(--surface) !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            height: 100vh !important;
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
            z-index: 9999 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding: 24px 16px !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            position: absolute !important;
            right: -13px !important;
            top: 22px !important;
            z-index: 999999 !important;
            width: 24px !important;
            height: 24px !important;
        }

        [data-testid="stSidebarCollapseButton"] button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 24px !important;
            height: 24px !important;
            border-radius: 4px !important;
            background-color: var(--raised) !important;
            border: 1px solid var(--control) !important;
            cursor: pointer !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebarCollapseButton"] button:hover {
            border-color: var(--text) !important;
        }

        [data-testid="stSidebarCollapseButton"] button * {
            font-size: 13px !important;
            color: var(--muted) !important;
            fill: var(--muted) !important;
        }

        /* Sidebar Navigation — Data Terminal 1px accent selection & brightness step */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 2px !important;
            display: flex !important;
            flex-direction: column !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label span[data-testid="stRadioButtonCustomObject"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            border-left: 2px solid transparent !important;
            border-radius: 0 4px 4px 0 !important;
            padding: 8px 12px !important;
            margin: 0 !important;
            min-height: 36px !important;
            cursor: pointer !important;
            transition: color 0.12s ease, background-color 0.12s ease !important;
            display: flex !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
            font-family: 'Public Sans', sans-serif !important;
            font-size: 13.5px !important;
            font-weight: 400 !important;
            color: var(--muted) !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.03) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
            color: var(--text) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: var(--raised) !important;
            border-left: 2px solid var(--accent) !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: var(--text) !important;
            font-weight: 500 !important;
        }

        /* App Screen Header Row */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            padding-bottom: 20px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
        }

        .page-title {
            font-family: 'Public Sans', sans-serif !important;
            font-size: 24px !important;
            font-weight: 600 !important;
            color: var(--text) !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            letter-spacing: -0.02em !important;
        }

        .page-subtitle {
            font-size: 13.5px;
            color: var(--muted);
            margin: 6px 0 0 0;
            line-height: 1.45;
        }

        .page-meta {
            text-align: right;
            font-size: 12px;
            color: var(--muted);
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 4px;
        }

        /* Divided KPI Strip — 1 container split by 1px hairlines */
        .kpi-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-card);
            margin-bottom: 24px;
            overflow: hidden;
        }

        .kpi-cell {
            padding: 16px 20px;
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .kpi-cell:last-child {
            border-right: none;
        }

        .kpi-label {
            font-size: 12px;
            font-weight: 400;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .kpi-value-row {
            display: flex;
            align-items: baseline;
            gap: 8px;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
            font-size: 24px;
            font-weight: 500;
            color: var(--text);
            line-height: 1.1;
        }

        .kpi-value.lead {
            font-size: 28px;
            font-weight: 600;
        }

        .kpi-unit {
            font-size: 12px;
            color: var(--muted);
            font-family: 'Public Sans', sans-serif;
        }

        .kpi-sub {
            font-size: 12px;
            color: var(--muted);
            margin-top: 6px;
            font-variant-numeric: tabular-nums;
        }

        /* Panels and Cards */
        .panel-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-card);
            padding: 20px;
            margin-bottom: 16px;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--rule);
        }

        .panel-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }

        .panel-meta {
            font-size: 12px;
            color: var(--muted);
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }

        /* Key-Value Technical Rows */
        .kv-list {
            display: flex;
            flex-direction: column;
        }

        .kv-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding: 8px 0;
            border-bottom: 1px solid var(--rule);
            font-size: 13px;
            gap: 12px;
        }

        .kv-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .kv-key {
            color: var(--muted);
            flex-shrink: 0;
        }

        .kv-val {
            color: var(--text);
            text-align: right;
            font-weight: 500;
        }

        .kv-val.mono {
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }

        /* Status Pills — Pale dark tint with high-contrast ink */
        .status-pill {
            display: inline-flex;
            align-items: center;
            height: 20px;
            padding: 0 8px;
            border-radius: 4px;
            font-size: 11.5px;
            font-weight: 500;
            white-space: nowrap;
            flex: none;
        }

        .status-pill.positive {
            background: var(--pill-positive-bg);
            color: var(--pill-positive-ink);
        }

        .status-pill.warning {
            background: var(--pill-warning-bg);
            color: var(--pill-warning-ink);
        }

        .status-pill.negative {
            background: var(--pill-negative-bg);
            color: var(--pill-negative-ink);
        }

        .status-pill.neutral {
            background: var(--pill-neutral-bg);
            color: var(--pill-neutral-ink);
        }

        /* Data Tables — 12px sentence-case grey headers, 1px rules, right-aligned numbers */
        .clean-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .clean-table th {
            text-align: left;
            font-size: 12px;
            font-weight: 400;
            color: var(--muted);
            padding: 8px 10px;
            border-bottom: 1px solid var(--border);
        }

        .clean-table th.num, .clean-table td.num {
            text-align: right;
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }

        .clean-table td {
            padding: 10px 10px;
            border-bottom: 1px solid var(--rule);
            color: var(--text);
            vertical-align: middle;
        }

        .clean-table tr:last-child td {
            border-bottom: none;
        }

        /* Bar List (Bairros / Luminarias) */
        .bar-list-row {
            margin-bottom: 10px;
        }

        .bar-list-row:last-child {
            margin-bottom: 0;
        }

        .bar-list-top {
            display: flex;
            justify-content: space-between;
            font-size: 12.5px;
            margin-bottom: 4px;
        }

        .bar-list-track {
            width: 100%;
            height: 4px;
            background: var(--raised);
            border-radius: 2px;
            overflow: hidden;
        }

        .bar-list-fill {
            height: 100%;
            background: var(--accent);
            border-radius: 2px;
        }

        /* Controls, Inputs, Buttons — Flat, no gradients, no glows */
        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] {
            border-radius: var(--radius-control) !important;
            background-color: var(--surface) !important;
            border: 1px solid var(--control) !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: var(--accent) !important;
        }

        .stTextInput label, .stSelectbox label, .stNumberInput label, .stTextArea label, .stFileUploader label {
            font-size: 13px !important;
            font-weight: 500 !important;
            color: var(--text) !important;
        }

        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background: var(--text) !important;
            color: #111111 !important;
            border: 1px solid var(--text) !important;
            border-radius: var(--radius-control) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            min-height: 36px !important;
            padding: 0 16px !important;
            box-shadow: none !important;
            transition: opacity 0.15s ease !important;
        }

        button[kind="primary"] *,
        [data-testid="stFormSubmitButton"] button * {
            color: #111111 !important;
            font-weight: 600 !important;
        }

        button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            opacity: 0.9 !important;
            transform: none !important;
            box-shadow: none !important;
        }

        button[kind="secondary"],
        .stDownloadButton button,
        .stLinkButton a {
            background: var(--raised) !important;
            color: var(--text) !important;
            border: 1px solid var(--control) !important;
            border-radius: var(--radius-control) !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            min-height: 36px !important;
            box-shadow: none !important;
            text-decoration: none !important;
        }

        button[kind="secondary"]:hover,
        .stDownloadButton button:hover,
        .stLinkButton a:hover {
            border-color: var(--muted) !important;
            background: #2a292d !important;
        }

        div[data-testid="stForm"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-card) !important;
            padding: 24px !important;
        }

        hr {
            border-color: var(--border) !important;
            margin: 24px 0 !important;
        }

        @media (max-width: 768px) {
            .kpi-strip {
                grid-template-columns: repeat(2, 1fr);
            }
            .kpi-cell:nth-child(2) {
                border-right: none;
            }
            .kpi-cell:nth-child(1), .kpi-cell:nth-child(2) {
                border-bottom: 1px solid var(--border);
            }
            .block-container {
                padding-left: 16px !important;
                padding-right: 16px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
