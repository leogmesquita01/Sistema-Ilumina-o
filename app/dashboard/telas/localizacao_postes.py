"""Georreferenciamento dos postes no escritório.

Tela pensada para **uma pessoa** (coordenador), num computador: escolhe o poste
na lista, acha o local no mapa de satélite e clica. A coordenada clicada
substitui a estimada. Postes coletados com o Kobo já chegam com GPS.
"""
import math

import folium
import streamlit as st
from streamlit_folium import st_folium

from app.constantes import CENTRO_MUNICIPIO, NOME_MUNICIPIO, URL_SATELITE
from app.dashboard.html_seguro import esc
from app.dashboard.ui import html, kpis, kv, painel, painel_topo, tela, topo, vazio
from app.servicos.dados_postes import (
    definir_localizacao_poste,
    listar_postes,
    localizacao_pendente,
)

_ZOOM_PADRAO = 16
_RAIO_TERRA_KM = 6371.0
_LIMITE_AVISO_KM = 30.0
_MODOS = ["Pendentes", "Todos"]


def _distancia_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distância em km entre dois pontos (fórmula de Haversine)."""
    rad = math.radians
    d_lat = rad(lat2 - lat1)
    d_lng = rad(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(d_lng / 2) ** 2
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
        centro = CENTRO_MUNICIPIO

    mapa = folium.Map(location=list(centro), zoom_start=_ZOOM_PADRAO, tiles=None, control_scale=True)
    folium.TileLayer(tiles=URL_SATELITE, attr="Esri World Imagery", name="Satélite", show=True).add_to(mapa)
    folium.TileLayer(tiles="OpenStreetMap", name="Ruas", show=False).add_to(mapa)
    folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

    atual = _coordenada_do_poste(poste)
    if atual:
        folium.Marker(
            list(atual),
            tooltip="Localização atual",
            icon=folium.Icon(color="black", icon="map-marker", prefix="fa"),
        ).add_to(mapa)
    if candidato:
        folium.Marker(
            [candidato["lat"], candidato["lng"]],
            tooltip="Novo ponto — clique em Salvar",
            icon=folium.Icon(color="orange", icon="ok-sign", prefix="fa"),
        ).add_to(mapa)

    chave = "mapa_localizacao_" + (poste["codigo"] if poste else "nenhum")
    return st_folium(mapa, key=chave, height=520, use_container_width=True, returned_objects=["last_clicked"])


def _lado(poste, candidato) -> None:
    painel_topo("Poste")
    if not poste:
        html(vazio("Nenhum poste nesta lista", "Cadastre um poste ou troque o filtro."))
        return

    pendente = localizacao_pendente(poste)
    situacao = '<span class="il-status pendente">Localização pendente</span>' if pendente else '<span class="il-status normal">Localização definida</span>'
    atual = _coordenada_do_poste(poste)
    html(
        '<div class="il-ficha">'
        f'<div class="il-ficha-linha"><span class="il-codigo">{esc(poste["codigo"])}</span>{situacao}</div>'
        f'<div class="il-ficha-os">{esc(poste.get("logradouro"))} · {esc(poste.get("bairro"))}</div></div>'
    )
    html('<div class="il-sem-margem">' + kv(
        [("Coordenada atual", f"{atual[0]:.6f}, {atual[1]:.6f}" if atual else "—")], mono=("Coordenada atual",)
    ) + "</div>")

    if not candidato:
        html('<div class="il-nota">Ache o poste na imagem de satélite e <strong>clique no ponto exato</strong>. '
             "Um marcador âmbar aparece; depois é só salvar.</div>")
        return

    lat, lng = candidato["lat"], candidato["lng"]
    dist_centro = _distancia_km(CENTRO_MUNICIPIO[0], CENTRO_MUNICIPIO[1], lat, lng)
    linhas = [("Novo ponto", f"{lat:.6f}, {lng:.6f}")]
    if atual:
        deslocamento = _distancia_km(atual[0], atual[1], lat, lng)
        linhas.append(("Deslocamento", "mesmo ponto" if deslocamento < 0.02 else f"{deslocamento:.2f} km"))
    linhas.append(("Do centro", f"{dist_centro:.2f} km"))
    html('<div class="il-sem-margem">' + kv(linhas, mono=("Novo ponto", "Deslocamento", "Do centro")) + "</div>")

    if dist_centro > _LIMITE_AVISO_KM:
        st.warning(f"Este ponto está a {dist_centro:.0f} km do centro de {NOME_MUNICIPIO}. Confira se é o poste certo.")

    b1, b2 = st.columns(2, gap="small")
    with b1:
        if st.button("Salvar localização", type="primary", use_container_width=True, key="loc_salvar"):
            definir_localizacao_poste(poste["codigo"], lat, lng)
            st.session_state.pop("loc_candidato", None)
            st.session_state.pop("loc_ultimo_clique", None)
            st.session_state["loc_aviso"] = poste["codigo"]
            st.rerun()
    with b2:
        if st.button("Descartar ponto", use_container_width=True, key="loc_descartar"):
            st.session_state.pop("loc_candidato", None)
            st.session_state.pop("loc_ultimo_clique", None)
            st.rerun()


def renderizar_tela_localizacao() -> None:
    with tela("localizar"):
        postes = listar_postes()
        pendentes = [p for p in postes if localizacao_pendente(p)]
        topo(
            "Georreferenciamento",
            "Localizar postes",
            "Escolha um poste, ache o ponto exato no satélite e clique. Postes coletados pelo Kobo já chegam com GPS.",
        )
        html(kpis([
            ("Com localização", len(postes) - len(pendentes), "", ""),
            ("Pendentes", len(pendentes), "", "não aparecem no mapa"),
        ]))

        codigo_salvo = st.session_state.pop("loc_aviso", None)
        if codigo_salvo:
            st.success(f"Localização do poste {codigo_salvo} salva. O mapa principal já mostra o novo ponto.")

        f1, f2, f3 = st.columns([1, 1.4, 2.2], vertical_alignment="bottom", gap="small")
        with f1:
            modo = st.segmented_control("Lista", _MODOS, default="Pendentes", key="loc_modo") or "Pendentes"
        with f2:
            busca = st.text_input("Filtrar", placeholder="Código, rua ou bairro", key="loc_busca")
        base = pendentes if modo == "Pendentes" else postes
        if busca.strip():
            termo = busca.strip().lower()
            base = [
                p for p in base
                if termo in str(p["codigo"]).lower()
                or termo in (p.get("logradouro") or "").lower()
                or termo in (p.get("bairro") or "").lower()
            ]
        poste_sel = None
        with f3:
            if base:
                rotulos = {f"{p['codigo']} · {(p.get('logradouro') or '')[:40]}": p for p in base}
                poste_sel = rotulos[st.selectbox("Poste", list(rotulos), key="loc_poste")]
            else:
                st.selectbox("Poste", ["Nenhum poste nesta lista"], disabled=True, key="loc_poste_vazio")

        codigo_sel = poste_sel["codigo"] if poste_sel else None
        candidato = st.session_state.get("loc_candidato")
        if candidato and candidato.get("codigo") != codigo_sel:
            st.session_state.pop("loc_candidato", None)
            st.session_state.pop("loc_ultimo_clique", None)
            candidato = None

        col_mapa, col_lado = st.columns([2.3, 1], gap="medium")
        with col_mapa:
            with painel("localizar-mapa"):
                painel_topo("Satélite", "clique no ponto do poste")
                resultado = _renderizar_mapa(poste_sel, candidato)
                clique = (resultado or {}).get("last_clicked") if isinstance(resultado, dict) else None
                if clique and codigo_sel:
                    marca = (round(float(clique["lat"]), 7), round(float(clique["lng"]), 7))
                    registro = (codigo_sel, marca)
                    if st.session_state.get("loc_ultimo_clique") != registro:
                        st.session_state["loc_ultimo_clique"] = registro
                        st.session_state["loc_candidato"] = {"codigo": codigo_sel, "lat": marca[0], "lng": marca[1]}
                        st.rerun()
        with col_lado:
            with painel("localizar-lado"):
                _lado(poste_sel, st.session_state.get("loc_candidato"))
