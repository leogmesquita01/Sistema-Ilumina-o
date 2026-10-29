from app.dashboard.html_seguro import esc


def test_esc():
    assert esc('<img src=x onerror="alert(1)">') == "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;"
    assert esc(None) == "—"
    assert esc("  ", "") == ""
    assert esc(100) == "100"


def test_esc_js_neutraliza_template_literal():
    from app.dashboard.html_seguro import esc_js

    assert esc_js("P1${alert(1)}") == "P1&#36;{alert(1)}"
    assert esc_js("a`+b+`c") == "a&#96;+b+&#96;c"
    assert esc_js("x\\y") == "x&#92;y"
    assert esc_js("<b>") == "&lt;b&gt;"


def test_mapa_nao_leva_payload_js_dos_dados(monkeypatch):
    """Popup e tooltip do folium ficam dentro de crases: ${...} vindo do banco não pode passar."""
    from app.dashboard.telas import componentes_mapa

    capturado = {}
    monkeypatch.setattr(componentes_mapa, "_exibir_html", lambda h, altura: capturado.setdefault("html", h))
    payloads = {"codigo": "P1${alert(1)}", "logradouro": "Rua `+alert(2)+`", "bairro": "B\\`",
                "tipo_luminaria": "LED${x}"}
    componentes_mapa.renderizar_mapa_folium(
        [{**payloads, "latitude": -6.15, "longitude": -35.6, "status": "normal", "potencia": 100}],
        [-6.15, -35.6], 15, "Ruas",
    )
    html = capturado["html"]
    for valor in payloads.values():
        assert valor not in html
    assert "${alert" not in html and "`+alert" not in html
