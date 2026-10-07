"""
Tela: Mapa e Localizador de Postes (COSERN)
Busca por código, visualização geográfica e despacho rápido.
"""

import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from app.servicos.dados_postes import listar_postes, obter_poste_por_codigo, obter_resumo_indicadores

def renderizar_tela_mapa():
    st.markdown('<h1 class="montserrat-title">🗺️ Mapa & Localizador de Postes</h1>', unsafe_allow_html=True)
    st.caption("Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura")

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

    # 2. Barra de Busca em Destaque
    col_busca, col_filtro = st.columns([3, 1])
    
    with col_busca:
        busca_termo = st.text_input(
            "Buscar por código da plaqueta ou logradouro:",
            placeholder="Digite o código (ex: CSR-1001, CSR-1004) ou nome da rua...",
            help="Pressione Enter após digitar para filtrar no mapa."
        )

    with col_filtro:
        filtro_status = st.selectbox(
            "Filtrar por Status:",
            ["Todos", "normal", "chamado_aberto", "urgente"]
        )

    # 3. Consulta de Postes
    postes = listar_postes(filtro_status=filtro_status, termo_busca=busca_termo)
    
    # 4. Poste Selecionado (se houver busca direta ou escolha)
    poste_focado = None
    if busca_termo:
        # Tenta achar exato ou primeiro resultado
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

    # 5. Layout com Mapa e Detalhes do Poste
    col_mapa, col_detalhes = st.columns([3, 2])

    with col_mapa:
        # Criação do Mapa Folium
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

        # Controle de Camadas (Ruas vs Satélite)
        folium.LayerControl(position="topright").add_to(m)

        # Agrupador de marcadores (MarkerCluster)
        cluster = plugins.MarkerCluster(name="Postes").add_to(m)

        for p in postes:
            # Cor do Marcador
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
                <div style="font-family: sans-serif; min-width: 160px;">
                    <b style="font-size: 14px; color: #0284C7;">Poste {p['codigo']}</b><br>
                    <span style="font-size: 12px; color: #333;">{p['logradouro']} - {p['bairro']}</span><br>
                    <hr style="margin: 5px 0;">
                    <span style="font-size: 11px;">💡 {p['tipo_luminaria']} {p['potencia']}W</span><br>
                    <span style="font-size: 11px;">Status: <b>{p['status'].upper()}</b></span>
                </div>
            """

            marcador = folium.Marker(
                location=[p["latitude"], p["longitude"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{p['codigo']} - {p['logradouro']}",
                icon=folium.Icon(color=cor, icon=icone, prefix="fa")
            )
            marcador.add_to(cluster)

        # Renderiza o mapa Folium no Streamlit
        st_folium(m, height=520, use_container_width=True)

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
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; text-transform: uppercase; color: #0284C7; font-weight: 700;">Código COSERN</span>
                        <span style="background: {cor_badge}22; color: {cor_badge}; border: 1px solid {cor_badge}; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 20px;">
                            {txt_badge}
                        </span>
                    </div>
                    <div style="font-size: 26px; font-weight: 900; color: #FFFFFF; font-family: 'JetBrains Mono';">{p['codigo']}</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">📍 {p['latitude']:.6f}, {p['longitude']:.6f}</div>
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
                st.write("**Postes encontrados nesta região:**")
                lista_rapida = [{"Código": x["codigo"], "Rua": x["logradouro"], "Status": x["status"]} for x in postes[:5]]
                st.dataframe(lista_rapida, use_container_width=True, hide_index=True)
