CSS_BASE = """
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
    padding-top: 0.9rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1.15rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    pointer-events: none;
    height: 0 !important;
    min-height: 0 !important;
}

@media (min-width: 769px) {
    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }
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
"""
