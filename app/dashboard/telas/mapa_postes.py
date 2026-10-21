import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import datetime
from collections import Counter
from app.servicos.dados_postes import listar_postes, obter_resumo_indicadores, obter_poste_por_codigo


def _status_pill_html(status: str) -> str:
    if status in ("urgente", "defeito_urgente"):
        return '<span class="status-pill negative">Defeito urgente</span>'
    if status == "chamado_aberto":
        return '<span class="status-pill warning">Chamado aberto</span>'
    return '<span class="status-pill positive">Operacional</span>'


def renderizar_tela_mapa():
    hora_atual = datetime.datetime.now().strftime("%H:%M")
    stats = obter_resumo_indicadores()

    total_postes = stats["total_postes"]
    total_led = stats["total_led"]
    taxa_led = stats["taxa_led"]
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
    os_concluidas = stats["os_concluidas"]

    # Finding factual a partir dos dados reais
    if total_chamados > 0:
        finding_texto = (
            f"{total_chamados} postes aguardam manutenção na rede municipal ({os_abertas} O.S. em aberto)."
        )
    else:
        finding_texto = "Todos os postes mapeados operam sem chamados pendentes."

    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1 class="page-title">Mapa da rede e ativos COSERN</h1>
                <p class="page-subtitle">{finding_texto}</p>
            </div>
            <div class="page-meta">
                <span>Sincronizado às <span class="mono" style="color: #ffffff;">{hora_atual}</span></span>
                <span>Município de Boa Saúde / RN</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Divided KPI Strip (1 container, 4 colunas separadas por 1px hairline)
    cor_chamado_val = "color: #e5566f;" if total_chamados > 0 else ""
    st.markdown(
        f"""
        <div class="kpi-strip">
            <div class="kpi-cell">
                <div class="kpi-label">Postes mapeados</div>
                <div class="kpi-value-row">
                    <span class="kpi-value lead">{total_postes:,}</span>
                    <span class="kpi-unit">ativos</span>
                </div>
                <div class="kpi-sub">Base georreferenciada COSERN</div>
            </div>
            <div class="kpi-cell">
                <div class="kpi-label">Cobertura em LED</div>
                <div class="kpi-value-row">
                    <span class="kpi-value">{taxa_led}%</span>
                    <span class="kpi-unit">{total_led} de {total_postes}</span>
                </div>
                <div class="kpi-sub">{total_postes - total_led} lâmpadas convencionais</div>
            </div>
            <div class="kpi-cell">
                <div class="kpi-label">Postes com defeito</div>
                <div class="kpi-value-row">
                    <span class="kpi-value" style="{cor_chamado_val}">{total_chamados}</span>
                    <span class="kpi-unit">pontos</span>
                </div>
                <div class="kpi-sub">Chamados abertos ou urgentes</div>
            </div>
            <div class="kpi-cell">
                <div class="kpi-label">Ordens de serviço</div>
                <div class="kpi-value-row">
                    <span class="kpi-value">{os_abertas}</span>
                    <span class="kpi-unit">abertas</span>
                </div>
                <div class="kpi-sub">{os_concluidas} concluídas no histórico</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_busca, col_filtro, col_camada = st.columns([3, 1.2, 1.2])

    with col_busca:
        busca_termo = st.text_input(
            "Buscar por plaqueta ou logradouro",
            placeholder="Ex: CSR-1001, CSR-1004, Rua Manoel Cirilo...",
        )

    with col_filtro:
        opcoes_status = {
            "Todos os status": "Todos",
            "Operacional (normal)": "normal",
            "Chamado aberto": "chamado_aberto",
            "Defeito urgente": "defeito_urgente",
        }
        escolha_status_label = st.selectbox("Filtrar por status", list(opcoes_status.keys()))
        filtro_status = opcoes_status[escolha_status_label]

    with col_camada:
        camada_padrao = st.selectbox(
            "Camada base do mapa",
            ["Modo noturno (Dark)", "Mapa de ruas", "Satélite (Esri)"],
        )

    postes = listar_postes(filtro_status=filtro_status, termo_busca=busca_termo)

    poste_focado = None
    if busca_termo:
        exatos = [p for p in postes if p["codigo"].lower() == busca_termo.strip().lower()]
        if exatos:
            poste_focado = exatos[0]
        elif postes:
            poste_focado = postes[0]

    if poste_focado:
        centro_mapa = [poste_focado["latitude"], poste_focado["longitude"]]
        zoom_inicial = 18
    else:
        centro_mapa = [-6.1611, -35.6025]
        zoom_inicial = 15

    col_mapa, col_detalhes = st.columns([3.1, 1.9], gap="medium")

    with col_mapa:
        tiles_inicial = "CartoDB dark_matter" if camada_padrao == "Modo noturno (Dark)" else "OpenStreetMap"
        m = folium.Map(
            location=centro_mapa,
            zoom_start=zoom_inicial,
            tiles=tiles_inicial,
            control_scale=True,
        )

        if camada_padrao == "Satélite (Esri)":
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri World Imagery",
                name="Satélite (Esri)",
                overlay=False,
                control=True,
            ).add_to(m)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="Mapa de ruas",
            overlay=False,
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles="CartoDB dark_matter",
            attr="CartoDB Dark",
            name="Modo noturno (Dark)",
            overlay=False,
            control=True,
        ).add_to(m)

        if camada_padrao != "Satélite (Esri)":
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri World Imagery",
                name="Satélite (Esri)",
                overlay=False,
                control=True,
            ).add_to(m)

        plugins.LocateControl(
            auto_start=False,
            position="topleft",
            strings={"title": "Localização GPS em campo"},
            locate_options={"enableHighAccuracy": True, "maxZoom": 18},
        ).add_to(m)

        folium.LayerControl(position="topright").add_to(m)
        cluster = plugins.MarkerCluster(name="Postes").add_to(m)

        for p in postes:
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

            popup_html = f"""
                <div style="font-family: 'Public Sans', sans-serif; min-width: 180px; color: #111111;">
                    <div style="font-family: monospace; font-weight: 700; font-size: 13px; margin-bottom: 2px;">{p['codigo']}</div>
                    <div style="font-size: 12px; color: #4b4d4f; margin-bottom: 6px;">{p['logradouro']} · {p['bairro']}</div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 6px; font-size: 11.5px;">
                        Luminária: <b>{p['tipo_luminaria']} {p['potencia']}W</b><br>
                        Status: <b>{status_label}</b>
                    </div>
                </div>
            """

            marcador = folium.Marker(
                location=[p["latitude"], p["longitude"]],
                popup=folium.Popup(popup_html, max_width=240),
                tooltip=f"{p['codigo']} · {p['logradouro']} ({p['tipo_luminaria']} {p['potencia']}W)",
                icon=folium.Icon(color=cor, icon=icone, prefix="fa"),
            )
            marcador.add_to(cluster)

        mapa_interacao = st_folium(m, height=520, use_container_width=True)

        # Se o usuário clicou em um marcador no mapa, foca nele automaticamente
        if not poste_focado and mapa_interacao and mapa_interacao.get("last_object_clicked_tooltip"):
            tooltip_clicado = mapa_interacao["last_object_clicked_tooltip"]
            cod_clicado = tooltip_clicado.split("·")[0].strip()
            encontrados = [p for p in postes if p["codigo"] == cod_clicado]
            if encontrados:
                poste_focado = encontrados[0]

    with col_detalhes:
        if poste_focado:
            p_completo = obter_poste_por_codigo(poste_focado["codigo"]) or poste_focado
            pill_html = _status_pill_html(p_completo["status"])
            potencia_val = p_completo.get("potencia", 100)
            consumo_mensal_kwh = round((potencia_val * 12 * 30) / 1000, 1)

            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="panel-header">
                        <div>
                            <div style="font-size: 11.5px; color: #8a8c92;">Plaqueta COSERN</div>
                            <div class="mono" style="font-size: 20px; font-weight: 600; color: #ffffff; margin-top: 2px;">{p_completo['codigo']}</div>
                        </div>
                        {pill_html}
                    </div>
                    <div class="kv-list">
                        <div class="kv-row">
                            <span class="kv-key">Logradouro</span>
                            <span class="kv-val">{p_completo['logradouro']}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Bairro / Comunidade</span>
                            <span class="kv-val">{p_completo['bairro']}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Referência</span>
                            <span class="kv-val">{p_completo.get('referencia') or '—'}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Coordenadas GPS</span>
                            <span class="kv-val mono">{p_completo['latitude']:.5f}, {p_completo['longitude']:.5f}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Luminária e potência</span>
                            <span class="kv-val">{p_completo['tipo_luminaria']} <span class="mono">{potencia_val}W</span></span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Consumo estimado (12h/dia)</span>
                            <span class="kv-val mono">{consumo_mensal_kwh} kWh/mês</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Estrutura e braço</span>
                            <span class="kv-val">{p_completo['tipo_poste']} · {p_completo['tipo_braco']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if p_completo.get("observacoes"):
                st.markdown(
                    f"""
                    <div class="panel-card" style="padding: 14px 16px;">
                        <div style="font-size: 12px; color: #8a8c92; margin-bottom: 4px;">Observações de campo</div>
                        <div style="font-size: 13px; color: #ffffff;">{p_completo['observacoes']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={p_completo['latitude']},{p_completo['longitude']}"
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Abrir O.S. de reparo", type="primary", use_container_width=True):
                    st.session_state["poste_selecionado_os"] = p_completo["codigo"]
                    st.session_state["pagina_atual"] = ":material/handyman: Solicitar reparo"
                    st.rerun()
            with c_btn2:
                st.link_button("Rota no Google Maps", maps_url, use_container_width=True)

        else:
            # Painel de distribuição por bairro/comunidade + fila de pontos com defeito
            contagem_bairros = Counter(p.get("bairro", "Centro") for p in postes)
            maior_qtd = max(contagem_bairros.values()) if contagem_bairros else 1
            barras_html = ""
            for bairro_nome, qtd in contagem_bairros.most_common(5):
                largura_pct = int((qtd / maior_qtd) * 88)
                barras_html += (
                    '<div class="bar-list-row">'
                    '<div class="bar-list-top">'
                    f'<span style="color: #ffffff;">{bairro_nome}</span>'
                    f'<span class="mono" style="color: #8a8c92;">{qtd}</span>'
                    '</div>'
                    '<div class="bar-list-track">'
                    f'<div class="bar-list-fill" style="width: {largura_pct}%;"></div>'
                    '</div>'
                    '</div>'
                )

            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="panel-header">
                        <span class="panel-title">Distribuição por localidade</span>
                        <span class="panel-meta">{len(postes)} exibidos</span>
                    </div>
                    {barras_html if barras_html else '<div style="color: #8a8c92; font-size: 13px;">Nenhum poste no filtro atual.</div>'}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Tabela enxuta dos postes prioritários / visíveis
            postes_prioritarios = sorted(
                postes,
                key=lambda x: 0 if x["status"] in ("urgente", "defeito_urgente") else (1 if x["status"] == "chamado_aberto" else 2),
            )[:6]

            linhas_tabela = ""
            for item in postes_prioritarios:
                pill = _status_pill_html(item["status"])
                linhas_tabela += (
                    '<tr>'
                    f'<td class="mono" style="font-weight: 500;">{item["codigo"]}</td>'
                    f'<td>{item["logradouro"]}<div style="font-size: 11.5px; color: #8a8c92;">{item["bairro"]}</div></td>'
                    f'<td class="num">{item["potencia"]}W</td>'
                    f'<td style="text-align: right;">{pill}</td>'
                    '</tr>'
                )

            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="panel-header">
                        <span class="panel-title">Ativos prioritários</span>
                        <span class="panel-meta">Clique no mapa para inspecionar</span>
                    </div>
                    <table class="clean-table">
                        <thead>
                            <tr>
                                <th>Plaqueta</th>
                                <th>Localização</th>
                                <th class="num">Potência</th>
                                <th style="text-align: right;">Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {linhas_tabela}
                        </tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
