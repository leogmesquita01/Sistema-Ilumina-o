CSS_SIDEBAR = """
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
"""
