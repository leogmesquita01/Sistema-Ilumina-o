CSS_SIDEBAR = """
/* =========================================================
   COMPACT VERTICAL SIDEBAR ISLAND (DESKTOP)
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
    padding: 14px 8px 14px 14px !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    z-index: 100 !important;
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    padding: 0 !important;
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
    border-radius: 24px !important;
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
    padding: 1.15rem 0.9rem !important;
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
    right: -12px !important;
    top: 24px !important;
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
    font-size: 12px !important;
    color: #F8FAFC !important;
    fill: #F8FAFC !important;
}

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
    justify-content: center;
    margin-bottom: 18px !important;
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
    section[data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
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
