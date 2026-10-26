import folium
from folium import plugins
import streamlit.components.v1 as components

from app.constantes import STATUS_CHAMADO, eh_urgente
from app.dashboard.html_seguro import esc
from app.servicos.dados_postes import localizacao_pendente

URL_ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# Nome mostrado no controle da tela -> (tiles, atribuição)
CAMADAS = {
    "Ruas": ("OpenStreetMap", None),
    "Satélite": (URL_ESRI, "Esri World Imagery"),
    "Noturno": ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", "CartoDB Dark"),
}

ALTURA_MAPA = 480


def _aparencia(status: str):
    """Cor do marcador (folium.Icon), ícone e rótulo — no padrão preto/âmbar/vermelho do tema."""
    if eh_urgente(status):
        return "red", "exclamation", "Urgente"
    if status == STATUS_CHAMADO:
        return "orange", "warning", "Chamado aberto"
    return "black", "bolt", "Operacional"


def renderizar_mapa_folium(postes: list, centro_mapa: list, zoom_inicial: int, camada_padrao: str) -> None:
    # Postes sem coordenada confiável não entram no mapa: desenhá-los no ponto
    # padrão empilharia a base no centro da cidade. Eles ficam na tela "Localizar".
    postes_mapeaveis = [p for p in postes if not localizacao_pendente(p)]

    m = folium.Map(location=centro_mapa, zoom_start=zoom_inicial, tiles=None, control_scale=True)
    for nome, (tiles, atribuicao) in CAMADAS.items():
        folium.TileLayer(
            tiles=tiles, attr=atribuicao, name=nome, overlay=False, control=True,
            show=(nome == camada_padrao),
        ).add_to(m)

    plugins.LocateControl(
        auto_start=False, position="topleft",
        strings={"title": "Minha localização"},
        locate_options={"enableHighAccuracy": True, "maxZoom": 18},
    ).add_to(m)
    cluster = plugins.MarkerCluster(name="Postes").add_to(m)

    for p in postes_mapeaveis:
        cor, icone, rotulo = _aparencia(p["status"])
        popup_html = (
            '<div style="font-family: \'IBM Plex Sans\', system-ui, sans-serif; min-width: 190px; color: #15171A;">'
            f'<div style="font-family: \'IBM Plex Mono\', monospace; font-weight: 600; font-size: 13px; margin-bottom: 2px;">{esc(p["codigo"])}</div>'
            f'<div style="font-size: 12px; color: #3F4448; margin-bottom: 6px;">{esc(p.get("logradouro"))} · {esc(p.get("bairro"))}</div>'
            '<div style="border-top: 1px solid #E7E9E4; padding-top: 6px; font-size: 12px;">'
            f'Luminária: <b>{esc(p.get("tipo_luminaria"))} {esc(p.get("potencia") or 100)} W</b><br>'
            f"Situação: <b>{rotulo}</b></div></div>"
        )
        folium.Marker(
            location=[p["latitude"], p["longitude"]],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=esc(f"{p['codigo']} · {p.get('logradouro') or '—'}"),
            icon=folium.Icon(color=cor, icon=icone, prefix="fa"),
        ).add_to(cluster)

    components.html(m.get_root().render(), height=ALTURA_MAPA)
