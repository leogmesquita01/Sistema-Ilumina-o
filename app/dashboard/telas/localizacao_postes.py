"""Georreferenciamento dos postes no escritório.

Tela pensada para **uma pessoa** (coordenador), num computador: escolhe o poste
na lista, acha o local no mapa de satélite e clica. A coordenada clicada
substitui a estimada. Nada aqui exige que a equipe de campo use GPS ou formulário
— o trabalho em campo continua sendo anotar o código, como já é feito.
"""
import math

import folium
import streamlit as st
from streamlit_folium import st_folium

from app.constantes import NOME_MUNICIPIO
from app.dashboard.html_seguro import esc
from app.servicos.dados_postes import (
    COORDENADA_PADRAO,
    definir_localizacao_poste,
    listar_postes,
    localizacao_pendente,
)

_URL_ESRI = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)
_ATRIB_ESRI = "Esri World Imagery"
_ZOOM_PADRAO = 16
_RAIO_TERRA_KM = 6371.0
_LIMITE_AVISO_KM = 30.0


def _distancia_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distância em km entre dois pontos (fórmula de Haversine)."""
    rad = math.radians
    d_lat = rad(lat2 - lat1)
    d_lng = rad(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(d_lng / 2) ** 2
    )
    return 2 * _RAIO_TERRA_KM * math.asin(math.sqrt(a))


def _coordenada_do_poste(poste: dict):
    if not poste or localizacao_pendente(poste):
        return None
    return (float(poste["latitude"]), float(poste["longitude"]))


def _renderizar_mapa(poste, candidato):
    """Mapa de satélite clicável. Devolve o resultado do componente."""
    centro = _coordenada_do_poste(poste)
    if candidato:
        centro = (candidato["lat"], candidato["lng"])
    if centro is None:
        centro = COORDENADA_PADRAO

    mapa = folium.Map(location=list(centro), zoom_start=_ZOOM_PADRAO, tiles=None, control_scale=True)
    folium.TileLayer(tiles=_URL_ESRI, attr=_ATRIB_ESRI, name="Satélite (Esri)", show=True).add_to(mapa)
    folium.TileLayer(tiles="OpenStreetMap", name="Mapa de ruas", show=False).add_to(mapa)
    folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

    atual = _coordenada_do_poste(poste)
    if atual:
        folium.Marker(
            list(atual),
            tooltip="Localização atual (estimada)",
            icon=folium.Icon(color="blue", icon="map-marker", prefix="fa"),
        ).add_to(mapa)

    if candidato:
        folium.Marker(
            [candidato["lat"], candidato["lng"]],
            tooltip="Novo ponto — clique em Salvar",
            icon=folium.Icon(color="green", icon="ok-sign", prefix="fa"),
        ).add_to(mapa)

    chave = "mapa_localizacao_" + (poste["codigo"] if poste else "nenhum")
    return st_folium(
        mapa,
        key=chave,
        height=520,
        use_container_width=True,
        returned_objects=["last_clicked"],
    )


def _renderizar_card(poste, candidato) -> None:
    if not poste:
        st.markdown(
            '<div class="panel-card" style="border-style: dashed; text-align: center; padding: 24px 18px;">'
            '<div style="font-size: 0.9rem; color: #94A3B8;">Nenhum poste para localizar.<br>'
            'Cadastre um poste ou troque o filtro na barra lateral.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    pendente = localizacao_pendente(poste)
    pill = (
        '<span class="status-pill warning">● Localização pendente</span>'
        if pendente
        else '<span class="status-pill positive">● Localização definida</span>'
    )
    atual = _coordenada_do_poste(poste)
    texto_atual = f"{atual[0]:.6f}, {atual[1]:.6f}" if atual else "—"

    st.markdown(
        '<div class="panel-card" style="padding: 18px 20px;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 10px;">'
        f'<span class="mono" style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF;">{esc(poste["codigo"])}</span>'
        f'{pill}'
        '</div>'
        f'<div style="font-size: 0.86rem; color: #E2E8F0; font-weight: 600;">{esc(poste.get("logradouro"))}</div>'
        f'<div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 12px;">{esc(poste.get("bairro"))}</div>'
        '<div class="kv-list">'
        f'<div class="kv-row"><span class="kv-key">Coordenada atual</span><span class="kv-val mono" style="font-size: 0.78rem;">{texto_atual}</span></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if not candidato:
        st.markdown(
            '<div class="panel-card" style="padding: 14px 16px; border-color: rgba(16, 185, 129, 0.3);">'
            '<div style="font-size: 0.84rem; color: #94A3B8; line-height: 1.5;">'
            'Ache o poste na imagem de satélite e <strong style="color: #F8FAFC;">clique no ponto exato</strong>. '
            'Um marcador verde aparece; depois é só salvar.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    lat, lng = candidato["lat"], candidato["lng"]
    dist_centro = _distancia_km(COORDENADA_PADRAO[0], COORDENADA_PADRAO[1], lat, lng)
    dist_atual = _distancia_km(atual[0], atual[1], lat, lng) if atual else None

    linhas = ""
    if dist_atual is not None:
        if dist_atual < 0.02:
            linhas += '<div class="kv-row"><span class="kv-key">Deslocamento</span><span class="kv-val" style="color: #94A3B8;">mesmo ponto</span></div>'
        else:
            linhas += (
                '<div class="kv-row"><span class="kv-key">Deslocamento</span>'
                f'<span class="kv-val mono" style="color: #FBBF24;">{dist_atual:.2f} km</span></div>'
            )
    linhas += (
        '<div class="kv-row"><span class="kv-key">Do centro</span>'
        f'<span class="kv-val mono" style="font-size: 0.8rem;">{dist_centro:.2f} km</span></div>'
    )

    st.markdown(
        '<div class="panel-card" style="padding: 16px 18px; border-color: rgba(16, 185, 129, 0.4);">'
        '<div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; font-weight: 700; margin-bottom: 8px;">Novo ponto</div>'
        f'<div class="mono" style="font-size: 0.95rem; color: #FFFFFF; font-weight: 700;">{lat:.6f}, {lng:.6f}</div>'
        f'<div class="kv-list" style="margin-top: 8px;">{linhas}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if dist_centro > _LIMITE_AVISO_KM:
        st.warning(f"Este ponto está a {dist_centro:.0f} km do centro de {NOME_MUNICIPIO}. Confira se é o poste certo.")

    if st.button("Salvar localização", type="primary", use_container_width=True, key="loc_salvar"):
        definir_localizacao_poste(poste["codigo"], lat, lng)
        st.session_state.pop("loc_candidato", None)
        st.session_state.pop("loc_ultimo_clique", None)
        st.session_state["loc_aviso"] = poste["codigo"]
        st.rerun()

    if st.button("Descartar ponto", use_container_width=True, key="loc_descartar"):
        st.session_state.pop("loc_candidato", None)
        st.session_state.pop("loc_ultimo_clique", None)
        st.rerun()


def renderizar_tela_localizacao() -> None:
    postes = listar_postes()
    pendentes = [p for p in postes if localizacao_pendente(p)]
    confirmados = len(postes) - len(pendentes)

    st.markdown(
        f'<div class="command-hero">'
        f'<div>'
        f'<div class="hero-badge"><span class="hero-dot"></span>Georreferenciamento · Escritório</div>'
        f'<h1 class="hero-title">Localizar Postes no Mapa</h1>'
        f'<p class="hero-subtitle">Clique no ponto exato do poste na imagem de satélite. O trabalho de campo continua sendo anotar o código — nada aqui exige GPS.</p>'
        f'</div>'
        f'<div class="hero-right">'
        f'<div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">Cobertura</div>'
        f'<div class="mono" style="font-size: 1.05rem; font-weight: 700; color: #10B981; margin-top: 2px;">{confirmados} de {len(postes)}</div>'
        f'<div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">com localização definida</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.pop("loc_aviso", None):
        st.success("Localização salva. O mapa principal já mostra o novo ponto.")

    sidebar_reduzida = st.session_state.get("sidebar_reduzida", False)
    sb_target = st.session_state.get("sb_card")

    poste_sel = None
    if not sidebar_reduzida and sb_target is not None:
        with sb_target:
            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; margin-bottom: 8px;">Fila de Localização</div>',
                unsafe_allow_html=True,
            )
            modo = st.radio(
                "Lista",
                ["Somente pendentes", "Todos os postes"],
                key="loc_modo",
                label_visibility="collapsed",
            )
            busca = st.text_input(
                "Filtrar poste",
                placeholder="Código, rua ou bairro...",
                key="loc_busca",
            )

            base = pendentes if modo == "Somente pendentes" else postes
            if busca and busca.strip():
                termo = busca.strip().lower()
                base = [
                    p
                    for p in base
                    if termo in p["codigo"].lower()
                    or termo in (p.get("logradouro") or "").lower()
                    or termo in (p.get("bairro") or "").lower()
                ]

            if base:
                rotulos = {
                    f"{p['codigo']} · {(p.get('logradouro') or '')[:30]}": p for p in base
                }
                escolha = st.selectbox("Poste", list(rotulos.keys()), key="loc_poste")
                poste_sel = rotulos[escolha]
            else:
                st.caption("Nenhum poste nesta lista.")

            st.markdown(
                '<div style="background:#0A101A; border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:10px 12px; margin-top:8px; font-size:0.74rem; color:#94A3B8; line-height:1.45;">'
                '<div style="color:#F8FAFC; font-weight:600; margin-bottom:4px;">O que conta como pendente</div>'
                'Postes sem coordenada e os que estão na coordenada padrão do centro — o cadastro antigo empilhava todos lá.'
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        poste_sel = pendentes[0] if pendentes else (postes[0] if postes else None)

    codigo_sel = poste_sel["codigo"] if poste_sel else None
    candidato = st.session_state.get("loc_candidato")
    if candidato and candidato.get("codigo") != codigo_sel:
        st.session_state.pop("loc_candidato", None)
        st.session_state.pop("loc_ultimo_clique", None)
        candidato = None

    col_mapa, col_lado = st.columns([2.35, 1], gap="medium")

    with col_mapa:
        st.markdown(
            '<div style="display: flex; justify-content: space-between; align-items: center; background: #0F1724; border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 11px 18px; margin-bottom: 10px;">'
            f'<span style="font-size: 0.82rem; font-weight: 700; color: #F8FAFC;">Satélite &bull; {NOME_MUNICIPIO}</span>'
            '<span style="font-size: 0.75rem; color: #94A3B8;">Clique no poste &bull; arraste para navegar</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        resultado = _renderizar_mapa(poste_sel, candidato)
        clique = (resultado or {}).get("last_clicked") if isinstance(resultado, dict) else None

        if clique and codigo_sel:
            marca = (round(float(clique["lat"]), 7), round(float(clique["lng"]), 7))
            registro = (codigo_sel, marca)
            if st.session_state.get("loc_ultimo_clique") != registro:
                st.session_state["loc_ultimo_clique"] = registro
                st.session_state["loc_candidato"] = {
                    "codigo": codigo_sel,
                    "lat": marca[0],
                    "lng": marca[1],
                }
                st.rerun()

    with col_lado:
        _renderizar_card(poste_sel, st.session_state.get("loc_candidato"))
