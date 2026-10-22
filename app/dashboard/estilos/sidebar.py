CSS_SIDEBAR = """
/* =========================================================
   SEPARATED BRAND PILL & DUAL-MODE VERTICAL SIDEBAR (V14)
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
    width: 248px !important;
    min-width: 248px !important;
    max-width: 248px !important;
    transform: none !important;
    transition: width 0.22s ease, min-width 0.22s ease, max-width 0.22s ease !important;
}

section[data-testid="stSidebar"]::before,
section[data-testid="stSidebar"]::after,
[data-testid="stSidebarResizeHandle"] {
    display: none !important;
    content: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Separated Floating Brand Pill at Top-Left */
.v14-brand-pill {
    position: absolute !important;
    top: -58px !important;
    left: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 10px !important;
    background: #0D1522 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 999px !important;
    padding: 6px 16px 6px 6px !important;
    width: max-content !important;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    z-index: 1000 !important;
    white-space: nowrap !important;
}

.v14-brand-icon {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #10B981, #059669) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35) !important;
    flex-shrink: 0 !important;
}

.v14-brand-text {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.96rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.3px !important;
    color: #FFFFFF !important;
    line-height: 1 !important;
}

/* Contextual Sidebar Island below Brand Pill (Expanded State) */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #0D1522 !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 24px !important;
    margin-top: 58px !important;
    height: calc(100vh - 86px) !important;
    max-height: calc(100vh - 86px) !important;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    display: flex !important;
    flex-direction: column !important;
    position: relative !important;
    overflow: visible !important;
    padding: 0 !important;
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
    padding: 1.05rem 0.9rem !important;
    overflow: visible !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    border-radius: 24px !important;
    position: static !important;
}

/* Collapse Button in Expanded Mode */
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: absolute !important;
    right: 10px !important;
    top: 10px !important;
    z-index: 999999 !important;
    width: 28px !important;
    height: 28px !important;
}

[data-testid="stSidebarCollapseButton"] button {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 28px !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background-color: #131F31 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    cursor: pointer !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;
    transition: all 0.18s ease !important;
}

[data-testid="stSidebarCollapseButton"] button:hover {
    background-color: #10B981 !important;
    border-color: #10B981 !important;
    transform: scale(1.06);
}

[data-testid="stSidebarCollapseButton"] button * {
    font-size: 15px !important;
    color: #F8FAFC !important;
    fill: #F8FAFC !important;
}

/* =========================================================
   REDUCED / COLLAPSED ICON-ONLY VERTICAL RAIL (DESKTOP)
   ========================================================= */
.v14-collapsed-rail {
    display: none !important;
}

@media (min-width: 769px) {
    section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 72px !important;
        min-width: 72px !important;
        max-width: 72px !important;
        transform: none !important;
        padding: 14px 4px 14px 14px !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {
        padding: 0 !important;
        overflow: visible !important;
    }

    /* Hide all expanded widgets inside stSidebar when collapsed, except the 1st block containing brand pill + icon rail */
    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] > div:not(:first-child),
    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:not(:first-child) {
        display: none !important;
    }

    /* Show the Verto V14 Icon-Only Vertical Rail */
    section[data-testid="stSidebar"][aria-expanded="false"] .v14-collapsed-rail {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 12px !important;
        width: 48px !important;
        padding-top: 2px !important;
        user-select: none !important;
    }

    /* Make stSidebarCollapseButton cover the collapsed icon rail so clicking any icon expands the sidebar */
    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: auto !important;
        width: 48px !important;
        height: 360px !important;
        opacity: 0 !important;
        z-index: 999999 !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] button {
        width: 100% !important;
        height: 100% !important;
        border-radius: 999px !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"]:has([data-testid="stSidebarCollapseButton"]:hover) .v14-rail-mini,
    section[data-testid="stSidebar"][aria-expanded="false"]:has([data-testid="stSidebarCollapseButton"]:hover) .v14-rail-capsule {
        border-color: rgba(16, 185, 129, 0.4) !important;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.55), 0 0 14px rgba(16, 185, 129, 0.14) !important;
    }
}

.v14-rail-mini {
    width: 48px;
    background: #0D1522;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    padding: 6px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease;
}

.v14-rail-capsule {
    width: 48px;
    background: #0D1522;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    padding: 6px 0 8px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45);
    transition: all 0.2s ease;
}

.v14-rail-btn {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94A3B8;
    font-size: 18px;
    transition: all 0.18s ease;
}

.v14-rail-btn.active {
    background: #10B981;
    color: #052016;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
}

.v14-rail-btn.subtle {
    background: rgba(255, 255, 255, 0.04);
    color: #E2E8F0;
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
    transition: padding-left 0.22s ease !important;
}

@media (min-width: 769px) {
    /* When sidebar is collapsed (72px), offset top horizontal nav so it sits right next to the separated Ilumina Boa Saúde pill */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ * div.st-key-nav_mobile_wrap,
    .stApp:has(section[data-testid="stSidebar"][aria-expanded="false"]) div.st-key-nav_mobile_wrap {
        padding-left: 144px !important;
    }
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
    .v14-brand-pill {
        position: static !important;
        margin-bottom: 12px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        margin-top: 0 !important;
        height: calc(100vh - 28px) !important;
        max-height: calc(100vh - 28px) !important;
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
