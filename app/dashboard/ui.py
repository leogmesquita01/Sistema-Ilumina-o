"""Peças de interface reutilizadas pelas telas (HTML + contêineres do Streamlit).

Todo texto que vem do banco ou do usuário passa por ``esc`` antes de entrar no HTML.
As classes ``il-*`` estão em ``estilos/tema.py``.
"""
from typing import Iterable, Optional, Sequence, Tuple

import streamlit as st

from app.constantes import STATUS_CHAMADO, eh_urgente
from app.dashboard.html_seguro import esc

PAGINAS = {
    "mapa": ":material/map: Mapa e postes",
    "reparo": ":material/handyman: Solicitar reparo",
    "ordens": ":material/assignment: Ordens de serviço",
    "cadastro": ":material/add_location_alt: Cadastrar poste",
    "importar": ":material/upload_file: Importar planilha",
    "localizar": ":material/edit_location: Localizar",
}

STATUS_ROTULO = {"normal": "Operacional", "chamado": "Chamado aberto", "urgente": "Urgente", "pendente": "Sem localização"}


def tela(nome: str):
    """Contêiner da tela. A classe ``st-key-tela-<nome>`` dispara a animação de entrada."""
    return st.container(key=f"tela-{nome}")


def painel(nome: str):
    """Painel branco com borda fina (estilo em ``[class*=st-key-painel-]``)."""
    return st.container(key=f"painel-{nome}")


def html(conteudo: str) -> None:
    st.markdown(conteudo, unsafe_allow_html=True)


def topo(kicker: str, titulo: str, subtitulo: Optional[str] = None, meta: Optional[str] = None) -> None:
    """Título da tela. ``kicker``/``titulo``/``subtitulo`` são escapados; ``meta`` é HTML pronto."""
    sub = f'<p class="il-subtitulo">{esc(subtitulo)}</p>' if subtitulo else ""
    lado = f'<div class="il-meta">{meta}</div>' if meta else ""
    html(
        '<div class="il-topo"><div>'
        f'<div class="il-kicker">{esc(kicker)}</div>'
        f'<h1 class="il-titulo">{esc(titulo)}</h1>{sub}'
        f"</div>{lado}</div>"
    )


def kpis(itens: Iterable[Tuple[str, object, str, str]]) -> str:
    """Faixa de indicadores. Cada item: (rótulo, valor, classe extra do valor, subtítulo)."""
    blocos = []
    for rotulo, valor, classe, sub in itens:
        sub_html = f'<span class="il-kpi-sub">{esc(sub)}</span>' if sub else ""
        blocos.append(
            f'<div class="il-kpi"><span class="il-kpi-rotulo">{esc(rotulo)}</span>'
            f'<span class="il-kpi-valor {classe}">{esc(valor)}</span>{sub_html}</div>'
        )
    return f'<section class="il-kpis" aria-label="Indicadores">{"".join(blocos)}</section>'


def painel_topo(titulo: str, meta: str = "") -> None:
    """Faixa de título de um painel. ``meta`` é HTML pronto (já escapado)."""
    html(f'<div class="il-painel-topo"><h2 class="il-painel-titulo">{esc(titulo)}</h2><span class="il-meta">{meta}</span></div>')


def classe_status(status: Optional[str], pendente: bool = False) -> str:
    if pendente:
        return "pendente"
    if eh_urgente(status):
        return "urgente"
    if status == STATUS_CHAMADO:
        return "chamado"
    return "normal"


def status_html(status: Optional[str], pendente: bool = False, texto: Optional[str] = None) -> str:
    """Quadrado colorido + texto. ``texto`` troca o rótulo padrão (é escapado)."""
    classe = classe_status(status, pendente)
    return f'<span class="il-status {classe}">{esc(texto or STATUS_ROTULO[classe])}</span>'


def kv(linhas: Sequence[Tuple[str, object]], mono: Sequence[str] = ()) -> str:
    itens = []
    for chave, valor in linhas:
        estilo = ' class="mono"' if chave in mono else ""
        itens.append(f"<div><dt>{esc(chave)}</dt><dd{estilo}>{esc(valor)}</dd></div>")
    return f'<dl class="il-kv">{"".join(itens)}</dl>'


def esqueleto(alto: bool = False, linhas: int = 3) -> str:
    barras = '<i class="alto"></i>' if alto else ""
    barras += "".join('<i class="curto"></i>' if i == linhas - 1 else "<i></i>" for i in range(linhas))
    return f'<div class="il-esqueleto" aria-hidden="true">{barras}</div>'


def vazio(titulo: str, texto: str) -> str:
    return f'<div class="il-vazio"><strong>{esc(titulo)}</strong>{esc(texto)}</div>'


def ir_para(pagina: str) -> None:
    """Troca de tela a partir de um botão (o menu lê ``pagina_atual``)."""
    st.session_state["pagina_atual"] = pagina
    st.rerun()
