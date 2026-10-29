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


# Caracteres que o ``html.escape`` deixa passar, mas que quebram um *template
# literal* JavaScript (texto entre crases). O folium coloca o HTML dos popups e
# tooltips dentro de crases: ``${alert(1)}`` num código de poste seria executado.
# Como entidades HTML, eles aparecem iguais na tela e não são avaliados pelo JS.
_JS_TEMPLATE = str.maketrans({"`": "&#96;", "$": "&#36;", "\\": "&#92;"})


def esc_js(valor: Any, padrao: str = "—") -> str:
    """Como :func:`esc`, mas seguro também dentro de template literal JS (mapa folium)."""
    return esc(valor, padrao).translate(_JS_TEMPLATE)
