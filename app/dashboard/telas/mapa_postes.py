import streamlit as st
import streamlit.components.v1 as components
import folium
from folium import plugins
import datetime
import urllib.parse
from collections import Counter
from app.servicos.dados_postes import listar_postes, obter_resumo_indicadores, obter_poste_por_codigo


def _status_pill_html(status: str) -> str:
    if status in ("urgente", "defeito_urgente"):
        return '<span class="status-pill negative">● Defeito Urgente</span>'
    if status == "chamado_aberto":
        return '<span class="status-pill warning">● Chamado Aberto</span>'
    return '<span class="status-pill positive">● Operacional</span>'


def renderizar_tela_mapa():
    hora_atual = datetime.datetime.now().strftime("%H:%M")
    stats = obter_resumo_indicadores()

    total_postes = stats["total_postes"]
    total_led = stats["total_led"]
    taxa_led = stats["taxa_led"]
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
    os_concluidas = stats["os_concluidas"]

    if total_postes == 0:
        subtitulo = "Base municipal pronta — cadastre postes em campo ou importe sua planilha de controle."
    elif total_chamados > 0:
        subtitulo = f"Atenção operacional: {total_chamados} ponto(s) aguardam manutenção ({os_abertas} O.S. em aberto)."
    else:
        subtitulo = "Rede operando com 100% de disponibilidade nos pontos monitorados."

    st.markdown(
        f"""
        <div class="command-hero">
            <div>
                <div class="hero-badge">
                    <span class="hero-dot"></span>
                    CENTRO DE OPERAÇÕES &bull; BOA SAÚDE / RN
                </div>
                <h1 class="hero-title">Mapa da Rede &amp; Ativos de Iluminação</h1>
                <p class="hero-subtitle">{subtitulo}</p>
            </div>
            <div class="hero-right">
                <div class="mono" style="font-size: 0.85rem; color: #34D399; font-weight: 700;">Sincronizado às {hora_atual}</div>
                <div style="font-size: 0.74rem; color: #94A3B8; margin-top: 3px;">Secretaria de Obras e Infraestrutura</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pct_chamados = min(100, int((total_chamados / total_postes) * 100)) if total_postes > 0 else 0
    total_os = os_abertas + os_concluidas
    pct_os_concluidas = int((os_concluidas / total_os) * 100) if total_os > 0 else 100

    st.markdown(
        f"""
        <div class="bento-kpi-grid">
            <div class="bento-kpi-card">
                <div class="bento-kpi-top">
                    <span class="bento-kpi-label">Postes Cadastrados</span>
                    <div class="bento-kpi-icon emerald">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2v20M5 6h14M7 10h10"/></svg>
                    </div>
                </div>
                <div class="bento-kpi-value">{total_postes:,}</div>
                <div class="bento-kpi-bar">
                    <div class="bento-kpi-bar-fill" style="width: {100 if total_postes > 0 else 8}%; background: linear-gradient(90deg, #10B981, #34D399);"></div>
                </div>
                <div class="bento-kpi-sub">
                    <span>Base própria municipal</span>
                    <span class="mono" style="color: #34D399;">Ativo</span>
                </div>
            </div>
            <div class="bento-kpi-card">
                <div class="bento-kpi-top">
                    <span class="bento-kpi-label">Cobertura em LED</span>
                    <div class="bento-kpi-icon cyan">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2"/></svg>
                    </div>
                </div>
                <div class="bento-kpi-value">{taxa_led}%</div>
                <div class="bento-kpi-bar">
                    <div class="bento-kpi-bar-fill" style="width: {taxa_led}%; background: linear-gradient(90deg, #0EA5E9, #38BDF8);"></div>
                </div>
                <div class="bento-kpi-sub">
                    <span>{total_led} luminárias LED</span>
                    <span class="mono">{total_postes - total_led} convenc.</span>
                </div>
            </div>
            <div class="bento-kpi-card">
                <div class="bento-kpi-top">
                    <span class="bento-kpi-label">Pontos em Alerta</span>
                    <div class="bento-kpi-icon rose">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    </div>
                </div>
                <div class="bento-kpi-value" style="{'color: #FB7185;' if total_chamados > 0 else ''}">{total_chamados}</div>
                <div class="bento-kpi-bar">
                    <div class="bento-kpi-bar-fill" style="width: {pct_chamados}%; background: linear-gradient(90deg, #F59E0B, #F43F5E);"></div>
                </div>
                <div class="bento-kpi-sub">
                    <span>Chamados pendentes</span>
                    <span class="mono">{pct_chamados}% da rede</span>
                </div>
            </div>
            <div class="bento-kpi-card">
                <div class="bento-kpi-top">
                    <span class="bento-kpi-label">Ordens de Serviço</span>
                    <div class="bento-kpi-icon amber">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                    </div>
                </div>
                <div class="bento-kpi-value">{os_abertas}</div>
                <div class="bento-kpi-bar">
                    <div class="bento-kpi-bar-fill" style="width: {pct_os_concluidas}%; background: linear-gradient(90deg, #F59E0B, #10B981);"></div>
                </div>
                <div class="bento-kpi-sub">
                    <span>Em fila de campo</span>
                    <span class="mono" style="color: #34D399;">{os_concluidas} concluídas</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_busca, col_filtro, col_camada = st.columns([3, 1.2, 1.2])

    with col_busca:
        busca_termo = st.text_input(
            "Pesquisar poste por código, rua ou comunidade",
            placeholder="Digite o código anotado (ex: P-01), rua ou bairro...",
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
            "Visualização do mapa",
            ["Mapa de ruas", "Satélite (Esri)", "Modo noturno (Dark)"],
        )

    postes = listar_postes(filtro_status=filtro_status, termo_busca=busca_termo)

    poste_focado = None
    if busca_termo and busca_termo.strip():
        exatos = [p for p in postes if p["codigo"].lower() == busca_termo.strip().lower()]
        if exatos:
            poste_focado = exatos[0]
        elif postes:
            poste_focado = postes[0]

    col_mapa, col_detalhes = st.columns([3, 2], gap="medium")

    with col_detalhes:
        opcoes_inspecao = ["Visão geral da rede"] + [
            f"{p['codigo']} · {p['logradouro']} ({p['bairro']})" for p in postes
        ]
        idx_inspecao = 0
        if poste_focado:
            for i, p in enumerate(postes, start=1):
                if p["codigo"] == poste_focado["codigo"]:
                    idx_inspecao = i
                    break

        selecao_inspecao = st.selectbox(
            "Selecionar ativo para inspeção",
            options=opcoes_inspecao,
            index=idx_inspecao,
        )
        if selecao_inspecao != "Visão geral da rede":
            cod_sel = selecao_inspecao.split("·")[0].strip()
            encontrados = [p for p in postes if p["codigo"] == cod_sel]
            if encontrados:
                poste_focado = encontrados[0]

    if poste_focado:
        centro_mapa = [poste_focado["latitude"], poste_focado["longitude"]]
        zoom_inicial = 18
    else:
        centro_mapa = [-6.1611, -35.6025]
        zoom_inicial = 15

    with col_mapa:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; background: #111A29; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 10px 16px; margin-bottom: 10px;">
                <span style="font-size: 0.82rem; font-weight: 700; color: #F8FAFC;">Geolocalização &bull; Boa Saúde / RN</span>
                <div style="display: flex; gap: 14px; font-size: 0.75rem; color: #94A3B8;">
                    <span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></span>Operacional</span>
                    <span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #F59E0B;"></span>Chamado</span>
                    <span style="display: inline-flex; align-items: center; gap: 5px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #F43F5E;"></span>Urgente</span>
                </div>
            </div>
            """,
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
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 185px; color: #0F172A;">
                    <div style="font-family: monospace; font-weight: 800; font-size: 13.5px; color: #059669; margin-bottom: 2px;">Poste {p['codigo']}</div>
                    <div style="font-size: 12px; color: #334155; margin-bottom: 6px;">{p['logradouro']} &bull; {p['bairro']}</div>
                    <div style="border-top: 1px solid #E2E8F0; padding-top: 6px; font-size: 11.5px;">
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

        components.html(m.get_root().render(), height=500)

    with col_detalhes:
        if poste_focado:
            p_completo = obter_poste_por_codigo(poste_focado["codigo"]) or poste_focado
            pill_html = _status_pill_html(p_completo["status"])
            potencia_val = p_completo.get("potencia", 100)
            consumo_mensal_kwh = round((potencia_val * 12 * 30) / 1000, 1)

            st.markdown(
                f"""
                <div class="panel-card" style="border-color: rgba(16, 185, 129, 0.3);">
                    <div class="panel-header">
                        <div>
                            <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; font-weight: 700;">Dossiê Técnico do Ativo</div>
                            <div class="mono" style="font-size: 1.55rem; font-weight: 800; color: #FFFFFF; margin-top: 2px;">{p_completo['codigo']}</div>
                        </div>
                        {pill_html}
                    </div>
                    <div class="spec-grid">
                        <div class="spec-tile">
                            <div class="spec-tile-label">Luminária</div>
                            <div class="spec-tile-val" style="color: #38BDF8;">{p_completo['tipo_luminaria']} <span class="mono">{potencia_val}W</span></div>
                        </div>
                        <div class="spec-tile">
                            <div class="spec-tile-label">Consumo (12h/dia)</div>
                            <div class="spec-tile-val mono" style="color: #34D399;">{consumo_mensal_kwh} kWh/mês</div>
                        </div>
                        <div class="spec-tile">
                            <div class="spec-tile-label">Estrutura</div>
                            <div class="spec-tile-val">{p_completo['tipo_poste']}</div>
                        </div>
                        <div class="spec-tile">
                            <div class="spec-tile-label">Braço</div>
                            <div class="spec-tile-val">{p_completo['tipo_braco']}</div>
                        </div>
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
                            <span class="kv-key">Ponto de referência</span>
                            <span class="kv-val">{p_completo.get('referencia') or '—'}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if p_completo.get("observacoes"):
                st.markdown(
                    f"""
                    <div class="panel-card" style="padding: 14px 18px;">
                        <div style="font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.04em; color: #94A3B8; font-weight: 700; margin-bottom: 4px;">Observações de Campo</div>
                        <div style="font-size: 0.86rem; color: #F8FAFC;">{p_completo['observacoes']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if round(float(p_completo.get("latitude", -6.1611)), 4) != -6.1611 or round(float(p_completo.get("longitude", -35.6025)), 4) != -35.6025:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={p_completo['latitude']},{p_completo['longitude']}"
            else:
                end_q = urllib.parse.quote(f"{p_completo.get('logradouro', '')}, {p_completo.get('bairro', '')}, Boa Saúde - RN")
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={end_q}"

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Solicitar Reparo", type="primary", use_container_width=True):
                    st.session_state["poste_selecionado_os"] = p_completo["codigo"]
                    st.session_state["pagina_atual"] = ":material/handyman: Solicitar reparo"
                    st.rerun()
            with c_btn2:
                st.link_button("Abrir no Google Maps", maps_url, use_container_width=True)

        else:
            contagem_bairros = Counter(p.get("bairro", "Centro") for p in postes)
            maior_qtd = max(contagem_bairros.values()) if contagem_bairros else 1
            barras_html = ""
            for bairro_nome, qtd in contagem_bairros.most_common(5):
                largura_pct = int((qtd / maior_qtd) * 100)
                barras_html += (
                    '<div class="bar-list-row">'
                    '<div class="bar-list-top">'
                    f'<span style="color: #F8FAFC;">{bairro_nome}</span>'
                    f'<span class="mono" style="color: #34D399; font-weight: 700;">{qtd} poste(s)</span>'
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
                        <span class="panel-title">Distribuição por Localidade</span>
                        <span class="panel-meta">{len(postes)} ativos</span>
                    </div>
                    {barras_html if barras_html else '<div style="color: #94A3B8; font-size: 0.85rem; padding: 8px 0;">Nenhum poste cadastrado ainda. Utilize os botões abaixo para iniciar sua base.</div>'}
                </div>
                """,
                unsafe_allow_html=True,
            )

            postes_prioritarios = sorted(
                postes,
                key=lambda x: 0 if x["status"] in ("urgente", "defeito_urgente") else (1 if x["status"] == "chamado_aberto" else 2),
            )[:6]

            if postes_prioritarios:
                linhas_tabela = ""
                for item in postes_prioritarios:
                    pill = _status_pill_html(item["status"])
                    linhas_tabela += (
                        '<tr>'
                        f'<td class="mono" style="font-weight: 700; color: #38BDF8;">{item["codigo"]}</td>'
                        f'<td><div style="font-weight: 600;">{item["logradouro"]}</div><div style="font-size: 0.75rem; color: #94A3B8;">{item["bairro"]}</div></td>'
                        f'<td class="num">{item["potencia"]}W</td>'
                        f'<td style="text-align: right;">{pill}</td>'
                        '</tr>'
                    )

                st.markdown(
                    f"""
                    <div class="panel-card">
                        <div class="panel-header">
                            <span class="panel-title">Postes Monitorados</span>
                            <span class="panel-meta">Visão rápida</span>
                        </div>
                        <table class="clean-table">
                            <thead>
                                <tr>
                                    <th>Código</th>
                                    <th>Localização</th>
                                    <th class="num">Potência</th>
                                    <th style="text-align: right;">Status</th>
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
            else:
                st.markdown(
                    """
                    <div class="panel-card" style="border-style: dashed; border-color: rgba(16, 185, 129, 0.35); text-align: center; padding: 24px 20px;">
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Comece a Alimentar a Base Municipal</div>
                        <div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 4px;">Cadastre um poste individualmente ou envie sua planilha com a relação que já possui anotada.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c_ac1, c_ac2 = st.columns(2)
                with c_ac1:
                    if st.button("Cadastrar Poste", type="primary", use_container_width=True):
                        st.session_state["pagina_atual"] = ":material/add_location_alt: Cadastrar poste"
                        st.rerun()
                with c_ac2:
                    if st.button("Importar Planilha", use_container_width=True):
                        st.session_state["pagina_atual"] = ":material/upload_file: Importar planilha"
                        st.rerun()
