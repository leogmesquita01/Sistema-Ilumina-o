"""
Tela: Mapa Realtime e Localizador de Postes (COSERN)
Monitoramento em tempo real da rede de iluminação pública de Boa Saúde / RN.
"""

import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import datetime
from app.servicos.dados_postes import listar_postes, obter_resumo_indicadores

def renderizar_tela_mapa():
    # Banner Hero com Status em Tempo Real
    hora_atual = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div class="hero-banner" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.2); color: #10B981; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 11px; border: 1px solid rgba(16, 185, 129, 0.4); text-transform: uppercase;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 10px #10B981;"></span>
                    MONITORAMENTO EM TEMPO REAL &bull; ONLINE
                </span>
                <h1 class="montserrat-title" style="margin: 8px 0 2px 0; font-size: 1.8rem;">Mapa da Rede Elétrica & Postes</h1>
                <p style="margin: 0; color: #8E8E93; font-size: 0.85rem;">Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura</p>
            </div>
            <div style="text-align: right;">
                <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #10B981; font-weight: 700;">📡 Sincronização: {hora_atual}</span>
                <div style="font-size: 0.75rem; color: #8E8E93; margin-top: 2px;">Rede: Neoenergia COSERN</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Cards de Indicadores Rápidos no Topo
    stats = obter_resumo_indicadores()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total de Postes", f"{stats['total_postes']:,}".replace(",", "."))
    with c2:
        st.metric("Postes em LED", f"{stats['taxa_led']}%", help=f"{stats['total_led']} de {stats['total_postes']} postes")
    with c3:
        st.metric("Chamados Ativos", stats['total_chamados'], delta="-1" if stats['total_chamados'] > 0 else "0", delta_color="inverse")
    with c4:
        st.metric("O.S. em Aberto", stats['os_abertas'])

    st.markdown("---")

    # 2. Controles de Tempo Real e Busca
    col_busca, col_filtro, col_realtime = st.columns([3, 1, 1])
    
    with col_busca:
        busca_termo = st.text_input(
            "Buscar por código da plaqueta ou logradouro:",
            placeholder="Digite o código (ex: CSR-1001, CSR-1004) ou rua...",
            help="Pressione Enter após digitar para filtrar no mapa."
        )

    with col_filtro:
        filtro_status = st.selectbox(
            "Status:",
            ["Todos", "normal", "chamado_aberto", "urgente"]
        )

    with col_realtime:
        modo_realtime = st.toggle("📡 Rastreio Realtime", value=True, help="Ativa controles de geolocalização e atualização dinâmica do mapa")

    # 3. Consulta de Postes
    postes = listar_postes(filtro_status=filtro_status, termo_busca=busca_termo)
    
    # 4. Poste Selecionado
    poste_focado = None
    if busca_termo:
        exatos = [p for p in postes if p["codigo"].lower() == busca_termo.strip().lower()]
        if exatos:
            poste_focado = exatos[0]
        elif postes:
            poste_focado = postes[0]

    # Centro do mapa
    if poste_focado:
        centro_mapa = [poste_focado["latitude"], poste_focado["longitude"]]
        zoom_inicial = 18
    else:
        centro_mapa = [-6.1611, -35.6025] # Boa Saúde Centro
        zoom_inicial = 15

    # 5. Layout com Mapa Realtime e Detalhes
    col_mapa, col_detalhes = st.columns([3, 2])

    with col_mapa:
        # Criação do Mapa Folium com suporte Realtime
        m = folium.Map(
            location=centro_mapa,
            zoom_start=zoom_inicial,
            tiles="OpenStreetMap",
            control_scale=True
        )

        # Adiciona camada de satélite de alta resolução (Esri)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="🛰️ Imagem de Satélite",
            overlay=False,
            control=True
        ).add_to(m)

        # Camada Dark Tech (CartoDB Dark Matter)
        folium.TileLayer(
            tiles="CartoDB dark_matter",
            attr="CartoDB Dark",
            name="🌃 Modo Noturno (Dark)",
            overlay=False,
            control=True
        ).add_to(m)

        # Plugin Realtime GPS: Rastreia a posição ao vivo do operador no mapa
        plugins.LocateControl(
            auto_start=False,
            position="topleft",
            strings={"title": "Mostrar minha localização GPS em tempo real"},
            locate_options={"enableHighAccuracy": True, "maxZoom": 18}
        ).add_to(m)

        # Plugin de Mini-Mapa de Navegação
        plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(m)

        # Controle de Camadas
        folium.LayerControl(position="topright").add_to(m)

        # Agrupador de marcadores (MarkerCluster)
        cluster = plugins.MarkerCluster(name="Postes").add_to(m)

        for p in postes:
            status = p["status"]
            cor = "green"
            icone = "bolt"
            if status == "chamado_aberto":
                cor = "orange"
                icone = "warning"
            elif status in ("urgente", "defeito_urgente"):
                cor = "red"
                icone = "exclamation"

            popup_html = f"""
                <div style="font-family: sans-serif; min-width: 170px;">
                    <b style="font-size: 14px; color: #10B981;">Poste {p['codigo']}</b><br>
                    <span style="font-size: 12px; color: #333;">{p['logradouro']} - {p['bairro']}</span><br>
                    <hr style="margin: 5px 0;">
                    <span style="font-size: 11px;">💡 {p['tipo_luminaria']} {p['potencia']}W</span><br>
                    <span style="font-size: 11px;">Status: <b>{p['status'].upper()}</b></span>
                </div>
            """

            marcador = folium.Marker(
                location=[p["latitude"], p["longitude"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"⚡ {p['codigo']} - {p['logradouro']}",
                icon=folium.Icon(color=cor, icon=icone, prefix="fa")
            )
            marcador.add_to(cluster)

        # Renderiza o mapa Folium no Streamlit
        st_folium(m, height=530, use_container_width=True)

    with col_detalhes:
        st.subheader("📋 Detalhes do Poste")

        if poste_focado:
            p = poste_focado
            
            # Badge de Status
            cor_badge = "#10B981"
            txt_badge = "OPERACIONAL NORMAL"
            if p["status"] == "chamado_aberto":
                cor_badge = "#F59E0B"
                txt_badge = "CHAMADO EM ABERTO"
            elif p["status"] in ("urgente", "defeito_urgente"):
                cor_badge = "#EF4444"
                txt_badge = "DEFEITO URGENTE"

            st.markdown(
                f"""
                <div style="background: #111E1A; border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 16px; padding: 16px; margin-bottom: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; text-transform: uppercase; color: #10B981; font-weight: 700;">Código COSERN</span>
                        <span style="background: {cor_badge}22; color: {cor_badge}; border: 1px solid {cor_badge}; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 20px;">
                            {txt_badge}
                        </span>
                    </div>
                    <div style="font-size: 26px; font-weight: 900; color: #FFFFFF; font-family: 'JetBrains Mono';">{p['codigo']}</div>
                    <div style="font-size: 12px; color: #8E8E93; margin-top: 4px;">📍 {p['latitude']:.6f}, {p['longitude']:.6f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Informações Técnicas
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Logradouro:**<br>{p['logradouro']}", unsafe_allow_html=True)
                st.markdown(f"**Luminária:**<br>`{p['tipo_luminaria']} ({p['potencia']}W)`", unsafe_allow_html=True)
            with col_info2:
                st.markdown(f"**Bairro/Comunidade:**<br>{p['bairro']}", unsafe_allow_html=True)
                st.markdown(f"**Estrutura:**<br>{p['tipo_poste']}", unsafe_allow_html=True)

            if p.get("referencia"):
                st.info(f"**Ponto de Referência:** {p['referencia']}", icon="ℹ️")

            st.markdown("---")

            # Botões de Ação
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={p['latitude']},{p['longitude']}"
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                st.link_button("🚗 Como Chegar (GPS)", maps_url, use_container_width=True)
            with c_btn2:
                if st.button("🛠️ Solicitar Reparo", type="primary", use_container_width=True):
                    st.session_state["poste_selecionado_os"] = p["codigo"]
                    st.session_state["pagina_atual"] = ":material/handyman: Solicitar reparo"
                    st.rerun()

        else:
            st.info("💡 Digite um código de poste na barra de pesquisa (ex: **CSR-1001**) ou clique em um poste no mapa para ver todos os detalhes.", icon="🔍")
            if postes:
                st.write("**Postes monitorados em tempo real:**")
                lista_rapida = [{"Código": x["codigo"], "Rua": x["logradouro"], "Status": x["status"]} for x in postes[:5]]
                st.dataframe(lista_rapida, use_container_width=True, hide_index=True)
