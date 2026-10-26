"""Escape de texto antes de montar HTML.

Tudo o que vem do banco, de planilhas ou de formulários passa por :func:`esc`
antes de entrar num ``st.markdown(..., unsafe_allow_html=True)`` ou num popup do
mapa. Sem isso, um ``<`` numa célula quebra o layout e um texto malicioso pode
injetar links e elementos falsos na tela.
"""
import html
from typing import Any


def esc(valor: Any, padrao: str = "—") -> str:
    """Texto seguro para HTML. ``None``/vazio vira ``padrao``."""
    if valor is None:
        return html.escape(padrao)
    texto = str(valor)
    if not texto.strip():
        return html.escape(padrao)
    return html.escape(texto)
