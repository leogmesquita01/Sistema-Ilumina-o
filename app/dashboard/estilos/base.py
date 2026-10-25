CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root {
  --ground:#e9eee9; --frame:#e2e9e2; --surface:#fff; --raised:#f5f7f4;
  --active:#e9eee9; --border:#dfe5df; --rule:#ebefeb; --control:#b8c5b9;
  --text:#202923; --muted:#59665d; --soft:#758178; --accent:#2e644a;
  --positive:#236448; --negative:#a33d35; --warning:#895c1d;
  --radius-card:8px; --radius-control:6px; --radius-sheet:16px;
  --text-primary:#202923; --text-secondary:#59665d; --text-muted:#758178;
}
html,body,.stApp {font-family:'IBM Plex Sans',system-ui,sans-serif!important;color:var(--text)!important;background:var(--ground)!important;-webkit-font-smoothing:antialiased}
.stApp {background:var(--ground)!important}
p,label,input,textarea,select,button,.stMarkdown p {font-family:'IBM Plex Sans',system-ui,sans-serif}
h1,h2,h3,h4,h5,h6 {font-family:'IBM Plex Sans',system-ui,sans-serif!important;color:var(--text)!important;letter-spacing:-.025em}
.mono,code,[data-testid="stMetricValue"] {font-family:'IBM Plex Mono',monospace!important;font-variant-numeric:tabular-nums}
[data-testid*="Icon"],[data-testid="stIconMaterial"],[class*="material-symbols"],[class*="material-icons"] {font-family:"Material Symbols Rounded","Material Icons"!important;font-feature-settings:"liga" 1!important;line-height:1!important}
section[data-testid="stMain"] {background:var(--ground)!important}
[data-testid="stMainBlockContainer"] {box-sizing:border-box!important;max-width:none!important;margin:8px 8px 8px 0!important;padding:26px 28px 36px!important;background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sheet)!important;min-height:calc(100vh - 16px)}
header[data-testid="stHeader"] {background:transparent!important;height:0!important;min-height:0!important;pointer-events:none}
#MainMenu,footer,[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"],[data-testid="stToolbarActions"] {display:none!important}
[data-testid="stElementToolbar"] {display:none!important}
[data-testid="stVerticalBlock"] {gap:.85rem}
@media(max-width:768px){[data-testid="stMainBlockContainer"]{margin:0!important;padding:18px 16px 28px!important;border-radius:0!important;border:0!important;min-height:100vh}.block-container{padding:0!important}}
"""

CSS_BASE += """
.brand-lockup{display:flex;align-items:center;gap:11px;padding:4px 5px 18px;border-bottom:1px solid #d3ddd4;margin-bottom:18px}
.brand-mark{width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:#2e644a;color:#fff;border-radius:6px;flex:none}
.brand-lockup strong{display:block;color:#203328;font-size:1rem;font-weight:600;line-height:1.15}
.brand-lockup small{display:block;color:#66746a;font-size:.76rem;margin-top:3px}
.sidebar-kicker,.summary-label{font-size:.67rem;font-weight:600;letter-spacing:.08em;color:#69786c;margin:0 0 9px}
.sidebar-divider{height:1px;background:#d3ddd4;margin:17px 0 14px}
.sidebar-summary{padding:0 4px}
.summary-count{color:#26342a;font-size:1.08rem;font-weight:600;font-variant-numeric:tabular-nums}
.summary-count span{font-size:.76rem;font-weight:400;color:#647267}
.summary-detail{display:flex;justify-content:space-between;gap:8px;margin-top:6px;color:#68756b;font-size:.75rem}
.summary-led{color:#2e644a;font-weight:600}
.sidebar-footer{border-top:1px solid #d3ddd4;margin-top:18px;padding:12px 4px 0;color:#758178;font-size:.72rem;line-height:1.45}
"""

CSS_BASE += """
/* Compatibility pass for the existing page markup while it adopts the new light shell. */
[style*="#0A101A"],[style*="#0F1724"]{background:var(--raised)!important;background-color:var(--raised)!important;border-color:var(--border)!important;border-radius:6px!important;box-shadow:none!important}
[style*="color: #FFFFFF"],[style*="color:#FFFFFF"],[style*="color: #F8FAFC"],[style*="color:#F8FAFC"]{color:var(--text)!important}
[style*="color:#94A3B8"],[style*="color: #94A3B8"],[style*="color:#64748B"],[style*="color: #64748B"]{color:var(--muted)!important}
[style*="color:#34D399"],[style*="color: #34D399"],[style*="color:#10B981"],[style*="color: #10B981"]{color:var(--accent)!important}
[style*="background: rgba(255,255,255"],[style*="background:rgba(255,255,255"]{background:var(--raised)!important;background-color:var(--raised)!important}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
"""

CSS_BASE += "h1,h2,h3,h4,h5,h6{text-wrap:balance}"
