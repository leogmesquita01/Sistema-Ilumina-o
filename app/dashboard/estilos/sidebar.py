CSS_SIDEBAR = """
section[data-testid="stSidebar"],section.stSidebar,[data-testid="stSidebar"] {background:var(--frame)!important;border:0!important;box-shadow:none!important;padding:20px 14px!important;box-sizing:border-box!important}
@media(min-width:769px){section[data-testid="stSidebar"],section.stSidebar,[data-testid="stSidebar"]{width:260px!important;min-width:260px!important;max-width:260px!important;transform:none!important}}
section[data-testid="stSidebar"]::before,section[data-testid="stSidebar"]::after,[data-testid="stSidebarResizeHandle"]{display:none!important}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{background:transparent!important;border:0!important;box-shadow:none!important;padding:0!important;overflow:visible!important}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],[data-testid="stSidebarCollapseButton"]{display:none!important}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3{font-size:1rem!important}
section[data-testid="stSidebar"] hr{border-color:#d3ddd4!important;margin:16px 0!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stWidgetLabel"]{display:none!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"]>div[role="radiogroup"]{gap:3px!important;display:flex!important;flex-direction:column!important;background:transparent!important;padding:0!important;border:0!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label{width:100%!important;background:transparent!important;border:1px solid transparent!important;border-radius:6px!important;padding:10px 11px!important;margin:0!important;cursor:pointer!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label p{font-size:.88rem!important;font-weight:500!important;color:var(--muted)!important;margin:0!important;display:flex!important;align-items:center!important;gap:9px!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover{background:rgba(255,255,255,.55)!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked){background:rgba(255,255,255,.8)!important;border-color:#d4ded5!important;box-shadow:none!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p{color:var(--accent)!important;font-weight:600!important}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) [data-testid="stIconMaterial"]{color:var(--accent)!important}
@media(max-width:768px){section[data-testid="stSidebar"]{background:var(--frame)!important;padding:18px 14px!important;box-shadow:8px 0 24px rgba(25,43,29,.12)!important;pointer-events:auto!important}section[data-testid="stSidebar"] [data-testid="stSidebarHeader"]{display:flex!important;justify-content:flex-end!important;align-items:center!important;height:42px!important;background:transparent!important}[data-testid="stSidebarCollapseButton"]{display:flex!important;visibility:visible!important;width:40px!important;height:40px!important;border-radius:6px!important;background:white!important;border:1px solid var(--border)!important} [data-testid="stExpandSidebarButton"]{position:fixed!important;left:12px!important;bottom:14px!important;z-index:1000020!important;width:44px!important;height:44px!important;border-radius:6px!important;background:var(--accent)!important;border:0!important}[data-testid="stExpandSidebarButton"] span{color:white!important}}
"""
