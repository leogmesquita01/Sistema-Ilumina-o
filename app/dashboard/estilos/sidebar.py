CSS_SIDEBAR = """
/* =========================================================
   SEPARATED FLOATING ISLANDS SIDEBAR (V14)
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
    padding: 14px 6px 14px 14px !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    z-index: 100 !important;
}

/* Largura fixa e transform travado APENAS no desktop.
   No mobile o Streamlit usa transform: translateX(-largura) para esconder
   a sidebar; forçar transform: none deixava a sidebar invisível (fundo
   transparente) por cima do conteúdo, bloqueando todos os toques. */
@media (min-width: 769px) {
    section[data-testid="stSidebar"],
    section.stSidebar,
    [data-testid="stSidebar"] {
        width: 252px !important;
        min-width: 252px !important;
        max-width: 252px !important;
        transform: none !important;
    }
}

section[data-testid="stSidebar"]::before,
section[data-testid="stSidebar"]::after,
[data-testid="stSidebarResizeHandle"] {
    display: none !important;
    content: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Make stSidebarContent & stSidebarUserContent 100% transparent so islands are visually separated */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding: 0 !important;
    overflow: visible !important;
    height: auto !important;
    background: transparent !important;
}

/* Contextual Card Island (Expanded Mode) */
div.st-key-sb_card_expanded {
    background: #0D1522 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 22px !important;
    padding: 14px 12px !important;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    margin-top: 4px !important;
}

/* Toggle Button Pill inside Sidebar */
div.st-key-sb_toggle_wrap div[data-testid="stButton"] > button {
    background: #0D1522 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 999px !important;
    color: #94A3B8 !important;
    min-height: 36px !important;
    height: 36px !important;
    padding: 0 12px !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35) !important;
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
}

div.st-key-sb_toggle_wrap div[data-testid="stButton"] > button:hover {
    border-color: rgba(16, 185, 129, 0.4) !important;
    color: #FFFFFF !important;
    background: #131F31 !important;
}

/* =========================================================
   SIDEBAR RADIO & WIDGET STYLING
   ========================================================= */
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
    background: rgba(8, 13, 20, 0.55) !important;
    padding: 5px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 8px 10px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    display: flex !important;
    align-items: center !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
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
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) [data-testid="stIconMaterial"] {
    color: #10B981 !important;
}

/* =========================================================
   HORIZONTAL TOP CAPSULE NAVIGATION (DESKTOP & MOBILE)
   ========================================================= */
.v14-mobile-topbar {
    display: none;
}

div.st-key-nav_mobile_wrap {
    display: flex !important;
    justify-content: flex-start !important;
    margin-bottom: 14px !important;
    transition: padding-left 0.2s ease !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: inline-flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 6px !important;
    background: #0D1522 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 999px !important;
    padding: 5px 6px !important;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.32) !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar {
    display: none !important;
}

div.st-key-nav_mobile_wrap [data-testid="stRadioOption"] > div > div:first-child,
div.st-key-nav_mobile_wrap div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label {
    flex: 0 0 auto !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    padding: 7px 15px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label:hover {
    background: rgba(255, 255, 255, 0.04) !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label:has(input:checked) {
    background: #10B981 !important;
    border-color: #10B981 !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.32) !important;
}

div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label:has(input:checked) p,
div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label:has(input:checked) [data-testid="stIconMaterial"] {
    color: #052016 !important;
    font-weight: 700 !important;
}

@media (max-width: 768px) {
    /* Gaveta mobile: fundo sólido e rolagem própria; o Streamlit controla abrir/fechar */
    section[data-testid="stSidebar"],
    section.stSidebar,
    [data-testid="stSidebar"] {
        background: #080D14 !important;
        background-color: #080D14 !important;
        padding: 10px 10px 14px 10px !important;
    }

    section[data-testid="stSidebar"][aria-expanded="true"] {
        box-shadow: 12px 0 40px rgba(0, 0, 0, 0.6) !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        box-shadow: none !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        height: 100% !important;
        overflow-y: auto !important;
    }

    /* Mostra o cabeçalho nativo apenas com o botão de fechar */
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        height: 36px !important;
        min-height: 36px !important;
        margin: 0 0 6px 0 !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        display: inline-flex !important;
        visibility: visible !important;
    }

    /* "Recolher barra" (modo trilho) não faz sentido no mobile */
    div.st-key-sb_toggle_wrap {
        display: none !important;
    }

    /* Botão flutuante para reabrir a gaveta quando ela estiver fechada */
    [data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        left: 14px !important;
        bottom: 18px !important;
        z-index: 1000020 !important;
        pointer-events: auto !important;
        width: 46px !important;
        height: 46px !important;
        border-radius: 50% !important;
        background: #10B981 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.45) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] span {
        color: #052016 !important;
    }

    .v14-mobile-topbar {
        display: flex !important;
        justify-content: space-between;
        align-items: center;
        background: #0D1522;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 10px 14px;
        margin-bottom: 8px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
    }

    div.st-key-nav_mobile_wrap {
        display: block !important;
        margin-bottom: 14px !important;
        padding-left: 0 !important;
    }

    div.st-key-nav_mobile_wrap div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        border-radius: 16px !important;
    }

    div.st-key-nav_mobile_wrap div[data-testid="stRadio"] label {
        border-radius: 11px !important;
        padding: 8px 12px !important;
    }
}
"""
