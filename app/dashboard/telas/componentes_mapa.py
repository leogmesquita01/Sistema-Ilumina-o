import folium
from folium import plugins
import streamlit as st
import streamlit.components.v1 as components

from app.servicos.dados_postes import localizacao_pendente


def status_pill_html(status: str) -> str:
    if status in ("urgente", "defeito_urgente"):
        return '<span class="status-pill negative">● Defeito Urgente</span>'
    if status == "chamado_aberto":
        return '<span class="status-pill warning">● Chamado Aberto</span>'
    return '<span class="status-pill positive">● Operacional</span>'


def renderizar_mapa_folium(postes: list, centro_mapa: list, zoom_inicial: int, camada_padrao: str) -> None:
    # Postes sem coordenada confiável não entram no mapa: desenhá-los no ponto
    # padrão empilharia a base no centro da cidade, mostrando uma precisão que
    # não existe. Eles aparecem na tela "Localizar postes".
    postes_mapeaveis = [p for p in postes if not localizacao_pendente(p)]
    sem_localizacao = len(postes) - len(postes_mapeaveis)
    aviso_sem_local = (
        f'<span style="display: inline-flex; align-items: center; gap: 5px; color: #FBBF24;">'
        f'<span style="width: 8px; height: 8px; border-radius: 50%; background: #F59E0B; opacity: 0.5;"></span>'
        f'{sem_localizacao} sem localização</span>'
    ) if sem_localizacao else ""

    st.markdown(
        '<div style="display: flex; justify-content: space-between; align-items: center; background: #0F1724; border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 11px 18px; margin-bottom: 10px;">'
        '<span style="font-size: 0.82rem; font-weight: 700; color: #F8FAFC;">Geolocalização &bull; Boa Saúde / RN</span>'
        '<div style="display: flex; gap: 14px; font-size: 0.75rem; color: #94A3B8;">'
        f'{aviso_sem_local}'
        '<span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></span>Operacional</span>'
        '<span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #F59E0B;"></span>Chamado</span>'
        '<span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #F43F5E;"></span>Urgente</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    m = folium.Map(
        location=centro_mapa,
        zoom_start=zoom_inicial,
        tiles=None,
        control_scale=True,
    )

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Mapa de ruas",
        overlay=False,
        control=True,
        show=(camada_padrao == "Mapa de ruas"),
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite (Esri)",
        overlay=False,
        control=True,
        show=(camada_padrao == "Satélite (Esri)"),
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Dark",
        name="Modo noturno (Dark)",
        overlay=False,
        control=True,
        show=(camada_padrao == "Modo noturno (Dark)"),
    ).add_to(m)

    plugins.LocateControl(
        auto_start=False,
        position="topleft",
        strings={"title": "Localização GPS em campo"},
        locate_options={"enableHighAccuracy": True, "maxZoom": 18},
    ).add_to(m)

    plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    folium.LayerControl(position="topright").add_to(m)

    cluster = plugins.MarkerCluster(name="Postes").add_to(m)

    for p in postes_mapeaveis:
        status = p["status"]
        cor = "green"
        icone = "bolt"
        status_label = "Operacional"
        if status == "chamado_aberto":
            cor = "orange"
            icone = "warning"
            status_label = "Chamado aberto"
        elif status in ("urgente", "defeito_urgente"):
            cor = "red"
            icone = "exclamation"
            status_label = "Defeito urgente"

        popup_html = (
            '<div style="font-family: \'Plus Jakarta Sans\', sans-serif; min-width: 185px; color: #0F172A;">'
            f'<div style="font-family: monospace; font-weight: 800; font-size: 13.5px; color: #059669; margin-bottom: 2px;">Poste {p["codigo"]}</div>'
            f'<div style="font-size: 12px; color: #334155; margin-bottom: 6px;">{p["logradouro"]} &bull; {p["bairro"]}</div>'
            '<div style="border-top: 1px solid #E2E8F0; padding-top: 6px; font-size: 11.5px;">'
            f'Luminária: <b>{p["tipo_luminaria"]} {p["potencia"]}W</b><br>'
            f'Status: <b>{status_label}</b>'
            '</div>'
            '</div>'
        )

        marcador = folium.Marker(
            location=[p["latitude"], p["longitude"]],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{p['codigo']} · {p['logradouro']} ({p['tipo_luminaria']} {p['potencia']}W)",
            icon=folium.Icon(color=cor, icon=icone, prefix="fa"),
        )
        marcador.add_to(cluster)

    components.html(m.get_root().render(), height=500)
