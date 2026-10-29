"""QA — injeção de JavaScript no mapa (folium) via template literal ${...}.

esc() (html.escape) não neutraliza "${". O folium 0.20 embute popup e tooltip em
template literals JS (`...`). Avalia o trecho gerado com o Node para provar a execução.
"""
import shutil
import subprocess

import pytest

from app.dashboard.telas import componentes_mapa as cm

CARGA = "${globalThis.PWN=String.fromCharCode(88,83,83)}"


def _html_mapa(monkeypatch, poste):
    capturado = {}
    monkeypatch.setattr(cm.components, "html", lambda h, height=None: capturado.setdefault("h", h))
    cm.renderizar_mapa_folium([poste], [-6.15, -35.61], 15, "Ruas")
    return capturado["h"]


@pytest.mark.defeito("DEF-10")
@pytest.mark.skipif(shutil.which("node") is None, reason="node indisponível")
@pytest.mark.parametrize("campo", ["logradouro", "codigo", "bairro", "tipo_luminaria"])
def test_qa090_template_literal_no_popup_nao_executa(monkeypatch, campo):
    poste = {"codigo": "P-01", "logradouro": "Rua A", "bairro": "Centro", "status": "normal",
             "latitude": -6.15, "longitude": -35.61, "tipo_luminaria": "LED", "potencia": 100}
    poste[campo] = CARGA
    h = _html_mapa(monkeypatch, poste)
    linha = next(l.strip() for l in h.splitlines() if l.strip().startswith("var html_"))
    literal = linha[linha.index("$(") + 2:linha.rindex(")[0]")]
    saida = subprocess.run(["node", "-e", f"const s={literal}; console.log(String(globalThis.PWN))"],
                           capture_output=True, text=True, timeout=30)
    assert saida.stdout.strip() != "XSS", f"JS executado a partir do campo {campo!r}"
