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
    agora = datetime.datetime.now()
    hora_atual = agora.strftime("%H:%M")
    if agora.hour < 12:
        saudacao = "Bom dia"
    elif agora.hour < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    stats = obter_resumo_indicadores()

    total_postes = stats["total_postes"]
    total_led = stats["total_led"]
    taxa_led = int(round(stats["taxa_led"]))
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
    os_concluidas = stats["os_concluidas"]
    operacionais = max(0, total_postes - total_chamados)
    taxa_disponibilidade = int(round((operacionais / total_postes) * 100)) if total_postes > 0 else 100
    total_os = os_abertas + os_concluidas
    taxa_os = int(round((os_concluidas / total_os) * 100)) if total_os > 0 else 100

    if total_postes == 0:
        subtitulo = "Acompanhe seus ativos de iluminação, metas de eficiência LED e ordens de campo."
    elif total_chamados > 0:
        subtitulo = f"Acompanhamento em tempo real — {total_chamados} ponto(s) aguardam manutenção ({os_abertas} O.S. na fila)."
    else:
        subtitulo = "Acompanhe os pontos monitorados, eficiência energética e chamados da rede municipal."

    st.markdown(
        f"""
        <div class="v14-header">
            <div>
                <h1 class="v14-greeting-title">{saudacao}, Leonardo Mesquita</h1>
                <p class="v14-greeting-sub">{subtitulo}</p>
            </div>
            <div class="v14-header-pills">
                <div class="v14-sync-pill">
                    <span class="hero-dot"></span>
                    <span>Boa Saúde / RN &bull; Sincronizado às <strong class="mono" style="color: #F8FAFC;">{hora_atual}</strong></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    todos_postes_base = listar_postes()
    contagem_geral_bairros = Counter(p.get("bairro", "Centro") for p in todos_postes_base)
    top_bairros = contagem_geral_bairros.most_common(5)
    if not top_bairros:
        top_bairros = [("Centro", 0), ("Bela Vista", 0), ("Lagoa", 0), ("Córrego", 0)]
    max_b = max((q for _, q in top_bairros), default=1) or 1

    colunas_barras_html = ""
    for b_nome, q_total in top_bairros:
        q_led_b = sum(
            1
            for p in todos_postes_base
            if p.get("bairro", "Centro") == b_nome and "LED" in str(p.get("tipo_luminaria", "")).upper()
        )
        h_tot = max(10, int((q_total / max_b) * 86)) if q_total > 0 else 8
        h_led = max(8, int((q_led_b / max_b) * 86)) if q_led_b > 0 else 6
        colunas_barras_html += (
            '<div class="v14-bar-col">'
            '<div class="v14-bar-pair">'
            f'<div class="v14-bar-pill" style="height: {h_tot}px; background: #1E293B;" title="Total: {q_total}"></div>'
            f'<div class="v14-bar-pill" style="height: {h_led}px; background: #10B981;" title="LED: {q_led_b}"></div>'
            '</div>'
            f'<span class="v14-bar-lbl">{b_nome}</span>'
            '</div>'
        )

    potencia_total_kw = round(sum(float(p.get("potencia", 100) or 100) for p in todos_postes_base) / 1000, 1)

    st.markdown(
        f"""
        <div class="v14-overview-grid">
            <div class="v14-balance-card">
                <div>
                    <div class="v14-card-label">
                        <span>Total de Ativos na Rede</span>
                        <span class="v14-trend-pill">● {taxa_disponibilidade}% disponível</span>
                    </div>
                    <div class="v14-big-number">{total_postes:,} <span style="font-size: 1.05rem; font-weight: 500; color: #94A3B8;">postes</span></div>
                    <div style="font-size: 0.8rem; color: #64748B;">
                        Carga instalada estimada: <strong class="mono" style="color: #E2E8F0;">{potencia_total_kw} kW</strong>
                    </div>
                </div>
                <div class="v14-action-row">
                    <div class="v14-btn-dark">
                        <span style="width: 7px; height: 7px; border-radius: 50%; background: #10B981;"></span>
                        <span>{operacionais} Operacionais</span>
                    </div>
                    <div class="v14-btn-emerald">
                        <span>⚡ {taxa_led}% LED</span>
                    </div>
                </div>
            </div>

            <div class="v14-stat-2x2">
                <div class="v14-mini-stat featured">
                    <div class="v14-mini-label">
                        <span>Luminárias LED</span>
                        <span>↗</span>
                    </div>
                    <div class="v14-mini-val">{total_led}</div>
                    <div class="v14-mini-sub">{taxa_led}% da planta municipal</div>
                </div>
                <div class="v14-mini-stat">
                    <div class="v14-mini-label">
                        <span>Em Alerta</span>
                        <span style="color: #FB7185;">●</span>
                    </div>
                    <div class="v14-mini-val" style="{'color: #FB7185;' if total_chamados > 0 else ''}">{total_chamados}</div>
                    <div class="v14-mini-sub">Aguardando reparo</div>
                </div>
                <div class="v14-mini-stat">
                    <div class="v14-mini-label">
                        <span>O.S. Abertas</span>
                        <span style="color: #FBBF24;">●</span>
                    </div>
                    <div class="v14-mini-val">{os_abertas}</div>
                    <div class="v14-mini-sub">Em fila de campo</div>
                </div>
                <div class="v14-mini-stat">
                    <div class="v14-mini-label">
                        <span>Concluídas</span>
                        <span style="color: #38BDF8;">✓</span>
                    </div>
                    <div class="v14-mini-val">{os_concluidas}</div>
                    <div class="v14-mini-sub">{taxa_os}% resolução</div>
                </div>
            </div>

            <div class="v14-chart-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.96rem; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">Bairros &amp; Eficiência</div>
                        <div style="font-size: 0.76rem; color: #64748B;">Comparativo Total vs. LED por localidade</div>
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 0.72rem; color: #94A3B8; align-items: center;">
                        <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 7px; height: 7px; border-radius: 2px; background: #1E293B;"></span>Total</span>
                        <span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 7px; height: 7px; border-radius: 2px; background: #10B981;"></span>LED</span>
                    </div>
                </div>
                <div class="v14-bars-wrap">
                    {colunas_barras_html}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #94A3B8; padding-top: 6px;">
                    <span>Localidades mapeadas: <strong style="color: #F8FAFC;">{len(contagem_geral_bairros)}</strong></span>
                    <span class="mono" style="color: #34D399;">Meta 100% LED</span>
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
                <div class="v14-asset-pass">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 28px; height: 28px; border-radius: 8px; background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; display: flex; align-items: center; justify-content: center; color: #34D399; font-weight: 800; font-size: 0.78rem;">⚡</div>
                            <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.95rem; color: #FFFFFF;">Ilumina &bull; Passaporte do Ativo</span>
                        </div>
                        {pill_html}
                    </div>
                    <div style="margin-bottom: 20px;">
                        <div style="font-size: 0.72rem; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase;">Identificador Oficial</div>
                        <div class="mono" style="font-size: 1.75rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.04em; margin-top: 2px;">{p_completo['codigo']}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px;">
                        <div>
                            <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase;">Localidade</div>
                            <div style="font-size: 0.84rem; font-weight: 600; color: #E2E8F0;">{p_completo['bairro']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase;">Luminária</div>
                            <div class="mono" style="font-size: 0.84rem; font-weight: 700; color: #34D399;">{p_completo['tipo_luminaria']} {potencia_val}W</div>
                        </div>
                    </div>
                </div>

                <div class="panel-card">
                    <div class="panel-header">
                        <span class="panel-title">Parâmetros &amp; Controles do Poste</span>
                        <span class="panel-meta">{consumo_mensal_kwh} kWh/mês</span>
                    </div>
                    <div class="kv-list">
                        <div class="kv-row">
                            <span class="kv-key">Logradouro</span>
                            <span class="kv-val">{p_completo['logradouro']}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Ponto de referência</span>
                            <span class="kv-val">{p_completo.get('referencia') or '—'}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Estrutura física</span>
                            <span class="kv-val">{p_completo['tipo_poste']}</span>
                        </div>
                        <div class="kv-row">
                            <span class="kv-key">Braço / Suporte</span>
                            <span class="kv-val">{p_completo['tipo_braco']}</span>
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
                        <div style="font-size: 0.74rem; color: #94A3B8; font-weight: 600; margin-bottom: 4px;">Observações de Campo</div>
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
            st.markdown(
                f"""
                <div class="v14-goals-grid">
                    <div class="v14-goal-card">
                        <div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Modernização LED</div>
                        <div class="v14-ring" style="background: conic-gradient(#10B981 {taxa_led * 3.6}deg, rgba(255,255,255,0.07) 0deg);">
                            <div class="v14-ring-inner">{taxa_led}%</div>
                        </div>
                        <div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{total_led} de {total_postes}</div>
                        <div style="font-size: 0.7rem; color: #64748B;">Luminárias eficientes</div>
                    </div>
                    <div class="v14-goal-card">
                        <div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Rede Operacional</div>
                        <div class="v14-ring" style="background: conic-gradient(#0EA5E9 {taxa_disponibilidade * 3.6}deg, rgba(255,255,255,0.07) 0deg);">
                            <div class="v14-ring-inner">{taxa_disponibilidade}%</div>
                        </div>
                        <div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{operacionais} ativos</div>
                        <div style="font-size: 0.7rem; color: #64748B;">Sem falha aberta</div>
                    </div>
                    <div class="v14-goal-card">
                        <div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Resolução O.S.</div>
                        <div class="v14-ring" style="background: conic-gradient(#34D399 {taxa_os * 3.6}deg, rgba(255,255,255,0.07) 0deg);">
                            <div class="v14-ring-inner">{taxa_os}%</div>
                        </div>
                        <div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{os_concluidas} concluídas</div>
                        <div style="font-size: 0.7rem; color: #64748B;">Atendimento de rua</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            postes_prioritarios = sorted(
                postes,
                key=lambda x: 0 if x["status"] in ("urgente", "defeito_urgente") else (1 if x["status"] == "chamado_aberto" else 2),
            )[:5]

            if postes_prioritarios:
                linhas_atividades = ""
                for item in postes_prioritarios:
                    pill = _status_pill_html(item["status"])
                    st_item = item["status"]
                    if st_item in ("urgente", "defeito_urgente"):
                        av_bg = "rgba(244, 63, 94, 0.14)"
                        av_col = "#FB7185"
                        av_border = "rgba(244, 63, 94, 0.3)"
                    elif st_item == "chamado_aberto":
                        av_bg = "rgba(245, 158, 11, 0.14)"
                        av_col = "#FBBF24"
                        av_border = "rgba(245, 158, 11, 0.3)"
                    else:
                        av_bg = "rgba(16, 185, 129, 0.12)"
                        av_col = "#34D399"
                        av_border = "rgba(16, 185, 129, 0.25)"

                    linhas_atividades += (
                        '<div class="v14-activity-row">'
                        '<div class="v14-activity-left">'
                        f'<div class="v14-avatar" style="background: {av_bg}; color: {av_col}; border: 1px solid {av_border};">{item["codigo"][:4]}</div>'
                        '<div>'
                        f'<div style="font-size: 0.86rem; font-weight: 600; color: #F8FAFC;">{item["codigo"]} &bull; {item["logradouro"]}</div>'
                        f'<div style="font-size: 0.75rem; color: #94A3B8;">{item["bairro"]} &bull; {item["tipo_luminaria"]} {item["potencia"]}W</div>'
                        '</div>'
                        '</div>'
                        f'<div style="text-align: right;">{pill}</div>'
                        '</div>'
                    )

                st.markdown(
                    f"""
                    <div class="panel-card">
                        <div class="panel-header">
                            <span class="panel-title">Atividades &amp; Monitoramento Recente</span>
                            <span class="panel-meta">{len(postes)} ativos</span>
                        </div>
                        <div>
                            {linhas_atividades}
                        </div>
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
