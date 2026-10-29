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
    cm._guardados.clear()
    return cm.gerar_html_mapa([poste], [-6.15, -35.61], 15, "Ruas")


@pytest.mark.defeito("DEF-10")
@pytest.mark.skipif(shutil.which("node") is None, reason="node indisponível")
@pytest.mark.parametrize("campo", ["logradouro", "codigo", "bairro", "tipo_luminaria"])
def test_qa090_template_literal_no_popup_nao_executa(monkeypatch, campo):
    poste = {"codigo": "P-01", "logradouro": "Rua A", "bairro": "Centro", "status": "normal",
             "latitude": -6.15, "longitude": -35.61, "tipo_luminaria": "LED", "potencia": 100}
    poste[campo] = CARGA
    h = _html_mapa(monkeypatch, poste)
    # Desde a correção do mapa, os textos do banco vão como dados JSON do
    # FastMarkerCluster; avalia essa linha e confirma que nada foi executado.
    linha = next(l.strip() for l in h.splitlines() if l.strip().startswith("var data = "))
    saida = subprocess.run(["node", "-e", f"{linha} console.log(String(globalThis.PWN))"],
                           capture_output=True, text=True, timeout=30)
    assert saida.stdout.strip() != "XSS", f"JS executado a partir do campo {campo!r}"
