"""Mapa da rede: tamanho do HTML, reaproveitamento e dados só como JSON."""
import random
import time

from app.dashboard.telas import componentes_mapa as cm


def _postes(n):
    rnd = random.Random(1)
    return [{"codigo": f"P-{i:05d}", "logradouro": f"Rua {i}", "bairro": "Centro",
             "latitude": -6.16 + rnd.uniform(-.05, .05), "longitude": -35.6 + rnd.uniform(-.05, .05),
             "status": "normal", "tipo_luminaria": "LED", "potencia": 100} for i in range(n)]


def test_mapa_com_3000_postes_e_leve():
    cm._guardados.clear()
    inicio = time.perf_counter()
    html = cm.gerar_html_mapa(_postes(3000), [-6.16, -35.6], 15, "Ruas")
    assert time.perf_counter() - inicio < 2  # antes: ~4,6 s
    assert len(html.encode()) < 1_000_000  # antes: ~5,4 MB


def test_mapa_mesma_entrada_reaproveita_html():
    cm._guardados.clear()
    postes = _postes(50)
    a = cm.gerar_html_mapa(postes, [-6.16, -35.6], 15, "Ruas")
    assert cm.gerar_html_mapa(postes, [-6.16, -35.6], 15, "Ruas") is a
    assert cm.gerar_html_mapa(postes, [-6.16, -35.6], 15, "Satélite") is not a


def test_mapa_ignora_postes_sem_localizacao():
    postes = _postes(3) + [{"codigo": "SEM", "latitude": None, "longitude": None, "status": "normal"}]
    assert [d[2] for d in cm.dados_dos_marcadores(postes)] == ["P-00000", "P-00001", "P-00002"]


def test_mapa_texto_do_banco_vira_dado_json_escapado():
    postes = _postes(1)
    postes[0]["codigo"] = "</script><script>alert(1)</script>"
    html = cm.gerar_html_mapa(postes, [-6.16, -35.6], 15, "Ruas")
    assert "<script>alert(1)" not in html
    assert "\\u003cscript\\u003ealert(1)" in html
