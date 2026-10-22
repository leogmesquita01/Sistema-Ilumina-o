import datetime
import urllib.parse
from collections import Counter
import streamlit as st
from app.servicos.dados_postes import listar_postes, obter_resumo_indicadores, obter_poste_por_codigo
from app.dashboard.telas.componentes_mapa import status_pill_html, renderizar_mapa_folium
from app.fuso import agora_local


def _renderizar_overview(stats: dict, todos_postes_base: list) -> tuple[int, int, int]:
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

    contagem_bairros = Counter(p.get("bairro", "Centro") for p in todos_postes_base)
    top_bairros = contagem_bairros.most_common(5) or [("Centro", 0), ("Bela Vista", 0), ("Lagoa", 0), ("Córrego", 0)]
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

    overview_html = (
        '<div class="v14-overview-grid">'
        '<div class="v14-balance-card">'
        '<div>'
        '<div class="v14-card-label">'
        '<span>Total de Ativos na Rede</span>'
        f'<span class="v14-trend-pill">● {taxa_disponibilidade}% disponível</span>'
        '</div>'
        f'<div class="v14-big-number">{total_postes:,} <span style="font-size: 1.05rem; font-weight: 500; color: #94A3B8;">postes</span></div>'
        '<div style="font-size: 0.8rem; color: #64748B;">'
        f'Carga instalada estimada: <strong class="mono" style="color: #E2E8F0;">{potencia_total_kw} kW</strong>'
        '</div>'
        '</div>'
        '<div class="v14-action-row">'
        '<div class="v14-btn-dark">'
        '<span style="width: 7px; height: 7px; border-radius: 50%; background: #10B981;"></span>'
        f'<span>{operacionais} Operacionais</span>'
        '</div>'
        '<div class="v14-btn-emerald">'
        f'<span>⚡ {taxa_led}% LED</span>'
        '</div>'
        '</div>'
        '</div>'
        '<div class="v14-stat-2x2">'
        '<div class="v14-mini-stat featured">'
        '<div class="v14-mini-label"><span>Luminárias LED</span><span>↗</span></div>'
        f'<div class="v14-mini-val">{total_led}</div>'
        f'<div class="v14-mini-sub">{taxa_led}% da planta municipal</div>'
        '</div>'
        '<div class="v14-mini-stat">'
        '<div class="v14-mini-label"><span>Em Alerta</span><span style="color: #FB7185;">●</span></div>'
        f'<div class="v14-mini-val" style="{"color: #FB7185;" if total_chamados > 0 else ""}">{total_chamados}</div>'
        '<div class="v14-mini-sub">Aguardando reparo</div>'
        '</div>'
        '<div class="v14-mini-stat">'
        '<div class="v14-mini-label"><span>O.S. Abertas</span><span style="color: #FBBF24;">●</span></div>'
        f'<div class="v14-mini-val">{os_abertas}</div>'
        '<div class="v14-mini-sub">Em fila de campo</div>'
        '</div>'
        '<div class="v14-mini-stat">'
        '<div class="v14-mini-label"><span>Concluídas</span><span style="color: #38BDF8;">✓</span></div>'
        f'<div class="v14-mini-val">{os_concluidas}</div>'
        f'<div class="v14-mini-sub">{taxa_os}% resolução</div>'
        '</div>'
        '</div>'
        '<div class="v14-chart-card">'
        '<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
        '<div>'
        '<div style="font-size: 0.96rem; font-weight: 700; color: #FFFFFF; font-family: \'Outfit\', sans-serif;">Bairros &amp; Eficiência</div>'
        '<div style="font-size: 0.76rem; color: #64748B;">Comparativo Total vs. LED por localidade</div>'
        '</div>'
        '<div style="display: flex; gap: 10px; font-size: 0.72rem; color: #94A3B8; align-items: center;">'
        '<span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 7px; height: 7px; border-radius: 2px; background: #1E293B;"></span>Total</span>'
        '<span style="display: inline-flex; align-items: center; gap: 4px;"><span style="width: 7px; height: 7px; border-radius: 2px; background: #10B981;"></span>LED</span>'
        '</div>'
        '</div>'
        f'<div class="v14-bars-wrap">{colunas_barras_html}</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #94A3B8; padding-top: 6px;">'
        f'<span>Localidades mapeadas: <strong style="color: #F8FAFC;">{len(contagem_bairros)}</strong></span>'
        '<span class="mono" style="color: #34D399;">Meta 100% LED</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(overview_html, unsafe_allow_html=True)
    return operacionais, taxa_disponibilidade, taxa_os


def renderizar_tela_mapa() -> None:
    agora = agora_local()
    hora_atual = agora.strftime("%H:%M")
    saudacao = "Bom dia" if agora.hour < 12 else ("Boa tarde" if agora.hour < 18 else "Boa noite")

    stats = obter_resumo_indicadores()
    total_postes = stats["total_postes"]
    total_led = stats["total_led"]
    taxa_led = int(round(stats["taxa_led"]))
    total_chamados = stats["total_chamados"]
    os_abertas = stats["os_abertas"]
    os_concluidas = stats["os_concluidas"]

    if total_postes == 0:
        subtitulo = "Acompanhe seus ativos de iluminação, metas de eficiência LED e ordens de campo."
    elif total_chamados > 0:
        subtitulo = f"Acompanhamento em tempo real — {total_chamados} ponto(s) aguardam manutenção ({os_abertas} O.S. na fila)."
    else:
        subtitulo = "Acompanhe os pontos monitorados, eficiência energética e chamados da rede municipal."

    st.markdown(
        '<div class="v14-header">'
        '<div>'
        f'<h1 class="v14-greeting-title">{saudacao}, Leonardo Mesquita</h1>'
        f'<p class="v14-greeting-sub">{subtitulo}</p>'
        '</div>'
        '<div class="v14-header-pills">'
        '<div class="v14-sync-pill">'
        '<span class="hero-dot"></span>'
        f'<span>Boa Saúde / RN &bull; Sincronizado às <strong class="mono" style="color: #F8FAFC;">{hora_atual}</strong></span>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    todos_postes_base = listar_postes()
    operacionais, taxa_disponibilidade, taxa_os = _renderizar_overview(stats, todos_postes_base)

    opcoes_status = {
        "Todos os status": "Todos",
        "Operacional (normal)": "normal",
        "Chamado aberto": "chamado_aberto",
        "Defeito urgente": "defeito_urgente",
    }
    opcoes_camada = ["Mapa de ruas", "Satélite (Esri)", "Modo noturno (Dark)"]
    sidebar_reduzida = st.session_state.get("sidebar_reduzida", False)
    sb_target = st.session_state.get("sb_card")

    if not sidebar_reduzida and sb_target is not None:
        with sb_target:
            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; margin-bottom: 8px;">Controles do Mapa</div>',
                unsafe_allow_html=True,
            )
            busca_termo = st.text_input(
                "Pesquisar poste",
                placeholder="Código (P-01), rua ou bairro...",
                key="mapa_busca_sidebar",
            )
            escolha_status_label = st.selectbox(
                "Filtrar por status",
                list(opcoes_status.keys()),
                key="mapa_status_sidebar",
            )
            filtro_status = opcoes_status[escolha_status_label]

            camada_padrao = st.selectbox(
                "Camada do mapa",
                opcoes_camada,
                key="mapa_camada_sidebar",
            )
    else:
        busca_termo = ""
        filtro_status = "Todos"
        camada_padrao = "Mapa de ruas"

    postes = listar_postes(filtro_status=filtro_status, termo_busca=busca_termo)

    poste_focado = None
    if busca_termo and busca_termo.strip():
        exatos = [p for p in postes if p["codigo"].lower() == busca_termo.strip().lower()]
        poste_focado = exatos[0] if exatos else (postes[0] if postes else None)

    opcoes_inspecao = ["Visão geral da rede"] + [
        f"{p['codigo']} · {p['logradouro']} ({p['bairro']})" for p in postes
    ]
    idx_inspecao = 0
    if poste_focado:
        for i, p in enumerate(postes, start=1):
            if p["codigo"] == poste_focado["codigo"]:
                idx_inspecao = i
                break

    if not sidebar_reduzida and sb_target is not None:
        with sb_target:
            selecao_inspecao = st.selectbox(
                "Inspecionar ativo",
                options=opcoes_inspecao,
                index=idx_inspecao,
                key="mapa_inspecao_sidebar",
            )
            if selecao_inspecao != "Visão geral da rede":
                cod_sel = selecao_inspecao.split("·")[0].strip()
                encontrados = [p for p in postes if p["codigo"] == cod_sel]
                if encontrados:
                    poste_focado = encontrados[0]

    col_mapa, col_detalhes = st.columns([3, 2], gap="medium")

    centro_mapa = [poste_focado["latitude"], poste_focado["longitude"]] if poste_focado else [-6.1611, -35.6025]
    zoom_inicial = 18 if poste_focado else 15

    with col_mapa:
        renderizar_mapa_folium(postes, centro_mapa, zoom_inicial, camada_padrao)

    with col_detalhes:
        if poste_focado:
            p_completo = obter_poste_por_codigo(poste_focado["codigo"]) or poste_focado
            pill_html = status_pill_html(p_completo["status"])
            potencia_val = p_completo.get("potencia", 100)
            consumo_mensal_kwh = round((potencia_val * 12 * 30) / 1000, 1)

            dossie_html = (
                '<div class="v14-asset-pass">'
                '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px;">'
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<div style="width: 28px; height: 28px; border-radius: 8px; background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; display: flex; align-items: center; justify-content: center; color: #34D399; font-weight: 800; font-size: 0.78rem;">⚡</div>'
                '<span style="font-family: \'Outfit\', sans-serif; font-weight: 700; font-size: 0.95rem; color: #FFFFFF;">Ilumina &bull; Passaporte do Ativo</span>'
                '</div>'
                f'{pill_html}'
                '</div>'
                '<div style="margin-bottom: 20px;">'
                '<div style="font-size: 0.72rem; color: #94A3B8; letter-spacing: 0.06em; text-transform: uppercase;">Identificador Oficial</div>'
                f'<div class="mono" style="font-size: 1.75rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.04em; margin-top: 2px;">{p_completo["codigo"]}</div>'
                '</div>'
                '<div style="display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px;">'
                '<div>'
                '<div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase;">Localidade</div>'
                f'<div style="font-size: 0.84rem; font-weight: 600; color: #E2E8F0;">{p_completo["bairro"]}</div>'
                '</div>'
                '<div style="text-align: right;">'
                '<div style="font-size: 0.68rem; color: #64748B; text-transform: uppercase;">Luminária</div>'
                f'<div class="mono" style="font-size: 0.84rem; font-weight: 700; color: #34D399;">{p_completo["tipo_luminaria"]} {potencia_val}W</div>'
                '</div>'
                '</div>'
                '</div>'
                '<div class="panel-card">'
                '<div class="panel-header">'
                '<span class="panel-title">Parâmetros &amp; Controles do Poste</span>'
                f'<span class="panel-meta">{consumo_mensal_kwh} kWh/mês</span>'
                '</div>'
                '<div class="kv-list">'
                f'<div class="kv-row"><span class="kv-key">Logradouro</span><span class="kv-val">{p_completo["logradouro"]}</span></div>'
                f'<div class="kv-row"><span class="kv-key">Ponto de referência</span><span class="kv-val">{p_completo.get("referencia") or "—"}</span></div>'
                f'<div class="kv-row"><span class="kv-key">Estrutura física</span><span class="kv-val">{p_completo["tipo_poste"]}</span></div>'
                f'<div class="kv-row"><span class="kv-key">Braço / Suporte</span><span class="kv-val">{p_completo["tipo_braco"]}</span></div>'
                '</div>'
                '</div>'
            )
            st.markdown(dossie_html, unsafe_allow_html=True)

            if p_completo.get("observacoes"):
                st.markdown(
                    '<div class="panel-card" style="padding: 14px 18px;">'
                    '<div style="font-size: 0.74rem; color: #94A3B8; font-weight: 600; margin-bottom: 4px;">Observações de Campo</div>'
                    f'<div style="font-size: 0.86rem; color: #F8FAFC;">{p_completo["observacoes"]}</div>'
                    '</div>',
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
            goals_html = (
                '<div class="v14-goals-grid">'
                '<div class="v14-goal-card">'
                '<div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Modernização LED</div>'
                f'<div class="v14-ring" style="background: conic-gradient(#10B981 {taxa_led * 3.6}deg, rgba(255,255,255,0.07) 0deg);"><div class="v14-ring-inner">{taxa_led}%</div></div>'
                f'<div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{total_led} de {total_postes}</div>'
                '<div style="font-size: 0.7rem; color: #64748B;">Luminárias eficientes</div>'
                '</div>'
                '<div class="v14-goal-card">'
                '<div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Rede Operacional</div>'
                f'<div class="v14-ring" style="background: conic-gradient(#0EA5E9 {taxa_disponibilidade * 3.6}deg, rgba(255,255,255,0.07) 0deg);"><div class="v14-ring-inner">{taxa_disponibilidade}%</div></div>'
                f'<div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{operacionais} ativos</div>'
                '<div style="font-size: 0.7rem; color: #64748B;">Sem falha aberta</div>'
                '</div>'
                '<div class="v14-goal-card">'
                '<div style="font-size: 0.76rem; color: #94A3B8; font-weight: 500;">Resolução O.S.</div>'
                f'<div class="v14-ring" style="background: conic-gradient(#34D399 {taxa_os * 3.6}deg, rgba(255,255,255,0.07) 0deg);"><div class="v14-ring-inner">{taxa_os}%</div></div>'
                f'<div style="font-size: 0.8rem; font-weight: 600; color: #F8FAFC;">{os_concluidas} concluídas</div>'
                '<div style="font-size: 0.7rem; color: #64748B;">Atendimento de rua</div>'
                '</div>'
                '</div>'
            )
            st.markdown(goals_html, unsafe_allow_html=True)

            postes_prioritarios = sorted(
                postes,
                key=lambda x: 0 if x["status"] in ("urgente", "defeito_urgente") else (1 if x["status"] == "chamado_aberto" else 2),
            )[:5]

            if postes_prioritarios:
                linhas_atividades = ""
                for item in postes_prioritarios:
                    pill = status_pill_html(item["status"])
                    st_item = item["status"]
                    if st_item in ("urgente", "defeito_urgente"):
                        av_bg, av_col, av_border = "rgba(244, 63, 94, 0.14)", "#FB7185", "rgba(244, 63, 94, 0.3)"
                    elif st_item == "chamado_aberto":
                        av_bg, av_col, av_border = "rgba(245, 158, 11, 0.14)", "#FBBF24", "rgba(245, 158, 11, 0.3)"
                    else:
                        av_bg, av_col, av_border = "rgba(16, 185, 129, 0.12)", "#34D399", "rgba(16, 185, 129, 0.25)"

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

                ativ_card_html = (
                    '<div class="panel-card">'
                    '<div class="panel-header">'
                    '<span class="panel-title">Atividades &amp; Monitoramento Recente</span>'
                    f'<span class="panel-meta">{len(postes)} ativos</span>'
                    '</div>'
                    f'<div>{linhas_atividades}</div>'
                    '</div>'
                )
                st.markdown(ativ_card_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="panel-card" style="border-style: dashed; border-color: rgba(16, 185, 129, 0.35); text-align: center; padding: 24px 20px;">'
                    '<div style="font-family: \'Outfit\', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Comece a Alimentar a Base Municipal</div>'
                    '<div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 4px;">Cadastre um poste individualmente ou envie sua planilha com a relação que já possui anotada.</div>'
                    '</div>',
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
