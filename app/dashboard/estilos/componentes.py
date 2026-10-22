CSS_COMPONENTES = """
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
"""
