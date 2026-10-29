"""Tema visual do Ilumina: "prancheta técnica".

Fundo claro, linhas finas, cantos quase retos, IBM Plex (Sans no texto, Mono em
códigos e números) e um único destaque âmbar — a cor da lâmpada de vapor de
sódio. As cores ficam em variáveis (:root) para que as telas usem nomes
(var(--tinta)) em vez de códigos soltos.

Fluidez (só CSS — o Streamlit redesenha a página a cada clique):
* cada tela entra com um fade + leve subida, com os blocos em cascata;
* elementos em atualização ficam esmaecidos suavemente (em vez de "piscar");
* esqueletos de carregamento com brilho deslizante;
* transições curtas em botões, menu, linhas de tabela e painéis.
Tudo isso é desligado para quem pede menos movimento no sistema
(prefers-reduced-motion).
"""

# Uma animação de entrada por tela: quando a tela muda, o nome da animação muda
# junto com a classe do contêiner, e o navegador a reinicia.
TELAS_ANIMADAS = ("mapa", "reparo", "ordens", "cadastro", "importar", "localizar", "login")

_CASCATA = "\n".join(
    f'[class*="st-key-tela-"] > [data-testid]:nth-child({i}) {{ animation-delay: {(i - 1) * 55}ms; }}'
    for i in range(1, 11)
)

_ENTRADAS = "\n".join(
    f"@keyframes il-entra-{t} {{ from {{ opacity: 0; transform: translateY(10px); }} "
    f"to {{ opacity: 1; transform: none; }} }}\n"
    f".st-key-tela-{t} > [data-testid] {{ animation-name: il-entra-{t}; }}"
    for t in TELAS_ANIMADAS
)

CSS_TEMA = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --fundo: #F1F2EE;
    --superficie: #FFFFFF;
    --superficie-2: #F7F8F5;
    --tinta: #15171A;
    --tinta-2: #3F4448;
    --apagado: #545A5F;
    --linha: #D5D8D1;
    --linha-suave: #E7E9E4;
    --campo: #C7CAC3;
    --ambar: #D98E04;
    --ambar-claro: #F7EBD3;
    --ambar-texto: #8A5A00;
    --normal: #2B3035;
    --chamado: #E0A21B;
    --urgente: #B4361A;
    --urgente-claro: #F8E6E1;
    --ok: #1F6B48;
    --raio: 2px;
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --sans: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
    --curva: cubic-bezier(0.2, 0.7, 0.2, 1);
}

/* ---------- Base ---------- */
html, body, .stApp {
    background: var(--fundo) !important;
    color: var(--tinta);
    font-family: var(--sans);
    -webkit-font-smoothing: antialiased;
}
.stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp li, .stApp td, .stApp th {
    font-family: var(--sans);
}
.stApp h1, .stApp h2, .stApp h3 {
    font-family: var(--sans) !important;
    color: var(--tinta) !important;
    letter-spacing: -0.015em;
    margin: 0 !important;
    padding: 0 !important;
}
.mono, code { font-family: var(--mono) !important; font-variant-numeric: tabular-nums; }
.stApp a { color: var(--tinta); text-underline-offset: 3px; }
.stApp a:hover { color: var(--ambar-texto); }

[data-testid="stIconMaterial"], [class*="material-symbols"] {
    font-family: "Material Symbols Rounded" !important;
    font-feature-settings: "liga" 1 !important;
    text-transform: none !important;
    font-style: normal !important;
    line-height: 1 !important;
}

.block-container {
    max-width: 1440px !important;
    padding: 1rem 2rem 3rem !important;
}
header[data-testid="stHeader"] { height: 0 !important; min-height: 0 !important; background: transparent !important; }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"],
[data-testid="stToolbar"], .stDeployButton, [data-testid="stAppDeployButton"],
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] {
    display: none !important;
}

/* Blocos HTML do tema não têm margem final: anula o -1rem que o Streamlit põe no markdown. */
.stApp [data-testid="stMarkdownContainer"]:has(> [class^="il-"]),
.stApp [data-testid="stMarkdownContainer"]:has(> [class*=" il-"]),
.stApp [data-testid="stMarkdownContainer"]:has(> section.il-kpis) { margin-bottom: 0 !important; }

/* ---------- Cabeçalho ---------- */
.il-marca { display: flex; align-items: center; gap: 12px; min-height: 56px; }
.il-marca-nome { font-family: var(--mono); font-weight: 600; font-size: 15px; letter-spacing: 0.14em; }
.il-marca-local { font-size: 13px; color: var(--apagado); }
.il-usuario { display: flex; align-items: center; justify-content: flex-end; gap: 10px; min-height: 56px; }
.il-avatar {
    width: 34px; height: 34px; flex-shrink: 0; background: var(--tinta); color: #FFFFFF;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--mono); font-size: 12px; font-weight: 600;
}
.il-usuario-nome { font-weight: 500; line-height: 1.2; }
.il-usuario-papel { font-size: 12px; color: var(--apagado); line-height: 1.2; }

/* Menu de telas: cápsula branca, tela ativa em âmbar. */
.st-key-nav_principal { width: 100%; display: flex; justify-content: center; }
.st-key-nav_principal [data-testid="stWidgetLabel"] { display: none; }
.st-key-nav_principal [role="radiogroup"] {
    display: flex; flex-wrap: wrap; gap: 4px; padding: 5px;
    background: var(--superficie); border: 1px solid var(--linha); border-radius: 999px;
    box-shadow: 0 6px 18px rgba(21, 23, 26, 0.06);
}
.st-key-nav_principal [data-testid="stRadioOption"] {
    margin: 0 !important; padding: 0 12px; min-height: 40px; border-radius: 999px;
    display: flex; align-items: center; cursor: pointer;
    transition: background-color 0.22s var(--curva), color 0.22s var(--curva);
}
.st-key-nav_principal [data-testid="stRadioOption"] > div { gap: 0 !important; }
.st-key-nav_principal [data-testid="stRadioOption"] > div > div:first-child { display: none !important; }
.st-key-nav_principal [data-testid="stRadioOption"] p {
    font-size: 14px !important; font-weight: 500; color: var(--tinta-2); white-space: nowrap;
    display: flex; align-items: center; gap: 8px; margin: 0;
}
.st-key-nav_principal [data-testid="stRadioOption"]:hover { background: var(--superficie-2); }
.st-key-nav_principal [data-testid="stRadioOption"][data-selected="true"] { background: var(--ambar); }
.st-key-nav_principal [data-testid="stRadioOption"][data-selected="true"] p { color: var(--tinta); font-weight: 600; }

/* ---------- Títulos de tela ---------- */
.il-topo { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 12px 32px; padding: 8px 0 4px; }
.il-kicker { font-family: var(--mono); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--apagado); }
.stApp .il-titulo { font-size: 28px !important; font-weight: 600 !important; letter-spacing: -0.02em; line-height: 1.2 !important; margin: 2px 0 0 !important; }
.il-subtitulo { color: var(--tinta-2); margin: 4px 0 0; max-width: 760px; }
.il-meta { font-family: var(--mono); font-size: 12px; color: var(--apagado); }

/* ---------- Indicadores (números soltos, separados por linhas) ---------- */
.il-kpis { display: flex; flex-wrap: wrap; row-gap: 16px; }
.il-kpi { display: flex; flex-direction: column; gap: 2px; padding: 0 28px; border-left: 1px solid var(--linha); }
.il-kpi:first-child { padding-left: 0; border-left: 0; }
.il-kpi-rotulo { font-family: var(--mono); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--apagado); }
.il-kpi-valor { font-size: 32px; font-weight: 600; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; line-height: 1.15; }
.il-kpi-valor.urgente { color: var(--urgente); }
.il-kpi-sub { font-size: 12px; color: var(--apagado); }

/* ---------- Painéis (contêineres com borda) ---------- */
[class*="st-key-painel-"] {
    background: var(--superficie);
    border: 1px solid var(--linha) !important;
    border-radius: var(--raio) !important;
    padding: 0 !important;
    gap: 0 !important;
    transition: border-color 0.25s var(--curva), box-shadow 0.25s var(--curva);
}
[class*="st-key-painel-"]:hover { border-color: #BFC3BB !important; box-shadow: 0 4px 14px rgba(21, 23, 26, 0.05); }
[class*="st-key-painel-"] > [data-testid] { padding: 0 18px; }
[class*="st-key-painel-"] > [data-testid]:last-child { padding-bottom: 16px; }
[class*="st-key-painel-"] > [data-testid]:has(.il-painel-topo) { padding: 0; }
[class*="st-key-painel-"] > [data-testid]:has(.il-painel-rodape) { padding: 0; }
[class*="st-key-painel-"] > [data-testid]:has(.il-sem-margem) { padding: 0; }
[class*="st-key-painel-"] > [data-testid] + [data-testid] { margin-top: 12px; }
[class*="st-key-painel-"] > [data-testid]:has(.il-painel-topo) + [data-testid] { margin-top: 14px; }
.il-painel-topo {
    display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 16px;
    padding: 14px 18px; border-bottom: 1px solid var(--linha-suave);
}
.stApp .il-painel-titulo { font-size: 16px !important; font-weight: 600 !important; line-height: 1.3 !important; margin: 0 !important; }
.il-painel-rodape {
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 24px;
    padding: 12px 18px; border-top: 1px solid var(--linha-suave); font-size: 13px; color: var(--tinta-2);
}
.il-painel-html { background: var(--superficie); border: 1px solid var(--linha); border-radius: var(--raio);
    transition: border-color 0.25s var(--curva), box-shadow 0.25s var(--curva); }
.il-painel-html:hover { border-color: #BFC3BB; box-shadow: 0 4px 14px rgba(21, 23, 26, 0.05); }
.il-corpo { padding: 14px 18px; }

/* ---------- Situação do poste: quadrado + texto ---------- */
.il-status { display: inline-flex; align-items: center; gap: 8px; font-weight: 600; white-space: nowrap; }
.il-status::before { content: ""; width: 9px; height: 9px; background: currentColor; flex-shrink: 0; }
.il-status.normal { color: var(--normal); }
.il-status.chamado { color: var(--ambar-texto); }
.il-status.chamado::before { background: var(--chamado); }
.il-status.urgente { color: var(--urgente); }
.il-status.concluida { color: var(--ok); }
.il-status.pendente { color: var(--apagado); }
.il-status.pendente::before { background: transparent; border: 1.5px solid var(--apagado); width: 7px; height: 7px; }

/* ---------- Listas chave-valor e tabelas ---------- */
.il-kv { margin: 0; padding: 0 18px; }
.il-kv > div { display: grid; grid-template-columns: 132px minmax(0, 1fr); gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--linha-suave); }
.il-kv > div:last-child { border-bottom: 0; }
.il-kv dt { color: var(--apagado); }
.il-kv dd { margin: 0; overflow-wrap: anywhere; }

.il-tabela-box { overflow-x: auto; }
.il-tabela { width: 100%; border-collapse: collapse; font-size: 13px; }
.il-tabela th {
    text-align: left; padding: 10px 8px; font-family: var(--mono); font-size: 11px; font-weight: 500;
    letter-spacing: 0.06em; text-transform: uppercase; color: var(--apagado); border-bottom: 1px solid var(--linha-suave);
}
.il-tabela td { padding: 11px 8px; border-bottom: 1px solid var(--linha-suave); vertical-align: top; }
.stApp .il-tabela, .stApp .il-tabela th, .stApp .il-tabela td, .stApp .il-tabela tr { border-left: 0 !important; border-right: 0 !important; border-top: 0 !important; }
.stApp .il-tabela { margin: 0 !important; }
.il-tabela th:first-child, .il-tabela td:first-child { padding-left: 18px; }
.il-tabela th:last-child, .il-tabela td:last-child { padding-right: 18px; }
.il-tabela tr:last-child td { border-bottom: 0; }
.il-tabela tbody tr { transition: background-color 0.18s var(--curva); }
.il-tabela tbody tr:hover { background: var(--superficie-2); }
.il-tabela .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }

.il-etiqueta {
    display: inline-flex; align-items: center; padding: 2px 8px; margin: 0 6px 6px 0;
    border: 1px solid var(--linha); border-radius: var(--raio); font-size: 12px; color: var(--tinta-2); background: var(--superficie-2);
}
.il-aviso {
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; padding: 12px 16px;
    background: var(--superficie); border: 1px solid var(--linha); border-left: 0;
    box-shadow: inset 3px 0 0 var(--chamado); font-size: 14px;
}
.il-vazio { padding: 28px 18px; text-align: center; color: var(--tinta-2); }
.il-vazio strong { display: block; color: var(--tinta); font-size: 16px; margin-bottom: 4px; }
.il-legenda { display: flex; flex-wrap: wrap; gap: 8px 20px; }
.il-legenda .il-status { font-weight: 400; color: var(--tinta-2); }
.il-legenda .il-status.normal::before { background: var(--normal); }
.il-legenda .il-status.urgente::before { background: var(--urgente); }

[class*="st-key-painel-"] > [data-testid]:has(iframe) { padding: 0; }
[class*="st-key-painel-"] > [data-testid]:has(iframe) + [data-testid] { margin-top: 0; }

/* ---------- Ficha do poste, O.S., notas ---------- */
.il-ficha { display: flex; flex-direction: column; gap: 4px; }
.il-ficha-linha { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px; }
.il-codigo { font-family: var(--mono); font-size: 24px; font-weight: 600; letter-spacing: 0.02em; }
.il-codigo.pequeno { font-size: 16px; }
.il-ficha-os { color: var(--tinta-2); }
.il-nota { color: var(--tinta-2); font-size: 13px; padding: 2px 0; }
.il-subsecao {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--apagado);
    padding-top: 8px; margin-top: 4px; border-top: 1px solid var(--linha-suave);
}
.il-confirmacao { display: flex; flex-direction: column; gap: 4px; padding-top: 14px; }
.il-os { display: flex; flex-direction: column; gap: 8px; padding-top: 14px; }
.il-os-linha { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px; }
.il-os-local { color: var(--tinta-2); }
.il-os-status { margin-left: auto; }
.il-os-defeito { font-size: 15px; font-weight: 600; }
.il-login-topo { display: flex; flex-direction: column; align-items: center; gap: 4px; margin: 10vh 0 20px; text-align: center; }
.il-login-topo .il-marca-nome { font-size: 18px; }

/* ---------- Esqueleto de carregamento ---------- */
.il-esqueleto { display: flex; flex-direction: column; gap: 12px; padding: 18px; }
.il-esqueleto i {
    display: block; height: 14px; border-radius: var(--raio);
    background: linear-gradient(90deg, #ECEEE9 0%, #F7F8F5 45%, #ECEEE9 90%);
    background-size: 200% 100%; animation: il-brilho 1.2s linear infinite;
}
.il-esqueleto i.alto { height: 220px; }
.il-esqueleto i.curto { width: 40%; }
@keyframes il-brilho { from { background-position: 100% 0; } to { background-position: -100% 0; } }

/* ---------- Controles do Streamlit ---------- */
.stApp [data-testid="stWidgetLabel"] p { font-size: 13px !important; color: var(--tinta-2) !important; font-weight: 500; }
[data-testid="stTextInputRootElement"], [data-baseweb="select"] > div, [data-baseweb="textarea"],
.stSelectbox .react-aria-ComboBox > [role="group"],
[data-testid="stNumberInputContainer"], [data-baseweb="input"] {
    background: var(--superficie) !important; border: 1px solid var(--campo) !important; border-radius: var(--raio) !important;
    transition: border-color 0.18s var(--curva), box-shadow 0.18s var(--curva);
}
[data-testid="stTextInputRootElement"]:focus-within, [data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within,
.stSelectbox .react-aria-ComboBox > [role="group"]:focus-within {
    border-color: var(--tinta) !important; box-shadow: 0 0 0 3px rgba(217, 142, 4, 0.25) !important;
}
.stApp input, .stApp textarea { color: var(--tinta) !important; }

.stApp button[data-testid^="stBaseButton"], .stApp a[data-testid^="stBaseLinkButton"] {
    min-height: 44px; border-radius: var(--raio) !important; font-weight: 500;
    transition: background-color 0.18s var(--curva), color 0.18s var(--curva), border-color 0.18s var(--curva), transform 0.12s var(--curva);
}
.stApp button[data-testid^="stBaseButton"]:active, .stApp a[data-testid^="stBaseLinkButton"]:active { transform: translateY(1px); }
.stApp button[data-testid="stBaseButton-primary"], .stApp button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--tinta) !important; color: #FFFFFF !important; border: 1px solid var(--tinta) !important; font-weight: 600;
}
.stApp button[data-testid="stBaseButton-primary"]:hover, .stApp button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: #2E3237 !important; border-color: #2E3237 !important;
}
.stApp button[data-testid="stBaseButton-primary"] p, .stApp button[data-testid="stBaseButton-primaryFormSubmit"] p { color: #FFFFFF !important; }
.stApp button[data-testid="stBaseButton-secondary"], .stApp button[data-testid="stBaseButton-secondaryFormSubmit"],
.stApp a[data-testid^="stBaseLinkButton"] {
    background: var(--superficie) !important; color: var(--tinta) !important; border: 1px solid var(--tinta) !important;
}
.stApp button[data-testid="stBaseButton-secondary"]:hover, .stApp a[data-testid^="stBaseLinkButton"]:hover {
    background: var(--superficie-2) !important; color: var(--tinta) !important;
}
.stApp button[data-testid="stBaseButton-tertiary"] { color: var(--tinta-2) !important; text-decoration: underline; min-height: 44px; }

/* Controle segmentado (camada do mapa, filtros) */
.stApp [data-testid="stButtonGroup"] [role="radiogroup"] { gap: 0 !important; border: 1px solid var(--campo); border-radius: var(--raio); width: fit-content; }
.stApp [data-testid="stButtonGroup"] button {
    border: 0 !important; border-radius: 0 !important; min-height: 40px; background: var(--superficie) !important; color: var(--tinta) !important;
    transition: background-color 0.18s var(--curva), color 0.18s var(--curva);
}
.stApp [data-testid="stButtonGroup"] button + button { border-left: 1px solid var(--campo) !important; }
.stApp [data-testid="stButtonGroup"] button[aria-checked="true"] { background: var(--tinta) !important; color: #FFFFFF !important; }
.stApp [data-testid="stButtonGroup"] button[aria-checked="true"] p { color: #FFFFFF !important; }

[data-testid="stForm"] { background: transparent; border: 0 !important; padding: 0 !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--superficie-2) !important; border: 1px dashed var(--campo) !important; border-radius: var(--raio) !important; }
[data-testid="stAlert"] { border-radius: var(--raio) !important; }
.stApp iframe { border: 0; display: block; }
[data-testid="stCheckbox"] label p { color: var(--tinta) !important; }

/* ---------- Fluidez ---------- */
[class*="st-key-tela-"] > [data-testid] {
    animation-duration: 0.45s;
    animation-timing-function: var(--curva);
    animation-fill-mode: both;
}
/* Enquanto o Streamlit recalcula, o conteúdo esmaece de leve em vez de piscar. */
.stApp [data-stale="true"] { opacity: 0.55 !important; transition: opacity 0.25s ease 0.12s !important; }
.stApp [data-stale="false"] { transition: opacity 0.2s ease !important; }

@media (max-width: 760px) {
    .block-container { padding: 0.75rem 1rem 2rem !important; }
    .il-kpi { padding: 0 16px; }
    .il-kpi-valor { font-size: 26px; }
    .stApp .il-titulo { font-size: 22px !important; }
    .il-usuario { justify-content: flex-start; }
    .st-key-nav_principal [role="radiogroup"] { border-radius: 20px; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}
""" + _ENTRADAS + "\n" + _CASCATA + "\n"
