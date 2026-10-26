import streamlit as st
from app.constantes import NOME_MUNICIPIO, UF_MUNICIPIO, PRIORIDADE_URGENTE
from app.dashboard.html_seguro import esc
from app.servicos.ordens_service import listar_ordens, concluir_ordem_servico, gerar_mensagem_whatsapp
from app.fuso import para_local


def renderizar_tela_ordens_servico():
    todas_ordens = listar_ordens(filtro_status="Todos")
    total_os = len(todas_ordens)
    abertas = [o for o in todas_ordens if o.get("status") == "aberta"]
    urgentes = [o for o in abertas if o.get("prioridade") == PRIORIDADE_URGENTE]
    concluidas = [o for o in todas_ordens if o.get("status") == "concluida"]

    taxa_conclusao = round((len(concluidas) / total_os) * 100, 1) if total_os > 0 else 100.0
    pct_abertas = round((len(abertas) / total_os) * 100, 1) if total_os > 0 else 0.0
    pct_urgentes = round((len(urgentes) / len(abertas)) * 100, 1) if abertas else 0.0

    header_os_html = (
        '<div class="command-hero">'
        '<div>'
        '<div class="hero-badge"><span class="hero-dot"></span>Controle de Manutenção · Equipes de Rua</div>'
        '<h1 class="hero-title">Ordens de Serviço e Fila de Campo</h1>'
        '<p class="hero-subtitle">Acompanhamento de chamados abertos, kits de peças embarcados e baixa de serviços concluídos.</p>'
        '</div>'
        '<div class="hero-right">'
        '<div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">Total Histórico</div>'
        f'<div class="mono" style="font-size: 1.05rem; font-weight: 700; color: #10B981; margin-top: 2px;">{total_os} Ordens</div>'
        f'<div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">{NOME_MUNICIPIO} · {UF_MUNICIPIO}</div>'
        '</div>'
        '</div>'
        '<div class="bento-kpi-grid" style="grid-template-columns: repeat(3, 1fr);">'
        '<div class="bento-kpi-card">'
        '<div class="bento-kpi-top">'
        '<span class="bento-kpi-label">Ordens em Aberto</span>'
        '<div class="bento-kpi-icon amber">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
        '</div>'
        '</div>'
        f'<div class="bento-kpi-value">{len(abertas)}</div>'
        '<div class="bento-kpi-bar">'
        f'<div class="bento-kpi-bar-fill" style="width: {min(100, max(5, pct_abertas))}%; background: #F59E0B;"></div>'
        '</div>'
        '<div class="bento-kpi-sub">'
        '<span>Aguardando execução</span>'
        '<span class="mono" style="color: #FBBF24;">Fila ativa</span>'
        '</div>'
        '</div>'
        '<div class="bento-kpi-card">'
        '<div class="bento-kpi-top">'
        '<span class="bento-kpi-label">Prioridade Urgente</span>'
        '<div class="bento-kpi-icon rose">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
        '</div>'
        '</div>'
        f'<div class="bento-kpi-value" style="{"color: #FB7185;" if urgentes else ""}">{len(urgentes)}</div>'
        '<div class="bento-kpi-bar">'
        f'<div class="bento-kpi-bar-fill" style="width: {min(100, max(4, pct_urgentes))}%; background: #F43F5E;"></div>'
        '</div>'
        '<div class="bento-kpi-sub">'
        '<span>Saúde, escolas ou risco</span>'
        '<span class="mono" style="color: #FB7185;">Crítico</span>'
        '</div>'
        '</div>'
        '<div class="bento-kpi-card">'
        '<div class="bento-kpi-top">'
        '<span class="bento-kpi-label">Reparos Concluídos</span>'
        '<div class="bento-kpi-icon emerald">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
        '</div>'
        '</div>'
        f'<div class="bento-kpi-value">{len(concluidas)}</div>'
        '<div class="bento-kpi-bar">'
        f'<div class="bento-kpi-bar-fill" style="width: {taxa_conclusao}%; background: linear-gradient(90deg, #10B981, #34D399);"></div>'
        '</div>'
        '<div class="bento-kpi-sub">'
        '<span>Taxa de resolução</span>'
        f'<span class="mono" style="color: #34D399;">{taxa_conclusao}%</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header_os_html, unsafe_allow_html=True)

    mapa_filtro = {
        "Todas as ordens": "Todos",
        "Em aberto": "aberta",
        "Concluídas": "concluida",
    }
    sidebar_reduzida = st.session_state.get("sidebar_reduzida", False)
    sb_target = st.session_state.get("sb_card")

    if not sidebar_reduzida and sb_target is not None:
        with sb_target:
            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; margin-bottom: 8px;">Filtros da Fila</div>',
                unsafe_allow_html=True,
            )
            escolha = st.selectbox("Status da ordem", list(mapa_filtro.keys()), key="os_status_sidebar")
            filtro_status = mapa_filtro[escolha]

            termo = st.text_input(
                "Buscar O.S. ou poste",
                placeholder="OS-2026, P-01, rua...",
                key="os_termo_sidebar",
            )
    else:
        filtro_status = "Todos"
        termo = ""

    ordens = listar_ordens(filtro_status=filtro_status)
    if termo and termo.strip():
        t = termo.strip().lower()
        ordens = [
            o
            for o in ordens
            if t in (o.get("protocolo") or "").lower()
            or t in (o.get("codigo_poste") or "").lower()
            or t in (o.get("logradouro") or "").lower()
            or t in (o.get("defeito") or "").lower()
        ]

    if not ordens:
        st.markdown(
            """
            <div class="panel-card" style="text-align: center; padding: 36px 24px; border-style: dashed;">
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.08rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">
                    Nenhuma Ordem de Serviço encontrada
                </div>
                <div style="font-size: 0.85rem; color: #94A3B8;">
                    Não há registros para o filtro selecionado. Você pode abrir uma nova solicitação na aba Solicitar Reparo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for os_item in ordens:
        is_aberta = os_item["status"] == "aberta"
        prioridade_item = os_item.get("prioridade") or "Normal"

        if not is_aberta:
            pill_status = '<span class="status-pill positive">Concluída</span>'
        elif prioridade_item == PRIORIDADE_URGENTE:
            pill_status = '<span class="status-pill negative">Aberta · Urgente</span>'
        else:
            pill_status = f'<span class="status-pill warning">Aberta · {esc(prioridade_item)}</span>'

        materiais_lista = os_item.get("materiais_lista", [])
        if materiais_lista:
            chips_html = "".join(
                [
                    f'<span class="mat-chip">{esc(m.get("quantidade", 1))}x {esc(m.get("item"), "")}</span>'
                    for m in materiais_lista
                ]
            )
        else:
            chips_html = '<span class="mat-chip">Vistoria técnica no local</span>'

        dt_abertura = para_local(os_item.get("data_abertura"))
        data_abertura = dt_abertura.strftime("%d/%m/%Y") if dt_abertura else (str(os_item.get("data_abertura") or "")[:10] or "—")

        card_os_html = (
            '<div class="panel-card" style="margin-bottom: 12px; padding: 18px 22px;">'
            '<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; flex-wrap: wrap;">'
            '<div>'
            '<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
            f'<span class="mono" style="font-size: 1rem; font-weight: 800; color: #FFFFFF;">{esc(os_item["protocolo"])}</span>'
            f'<span class="mono" style="font-size: 0.85rem; font-weight: 700; color: #34D399; background: rgba(16, 185, 129, 0.12); padding: 2px 9px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">Poste {esc(os_item["codigo_poste"])}</span>'
            f'<span style="font-size: 0.85rem; color: #94A3B8;">{esc(os_item.get("logradouro"))} · {esc(os_item.get("bairro"))}</span>'
            '</div>'
            f'<div style="font-size: 0.95rem; color: #F8FAFC; margin-top: 10px; font-weight: 600;">{esc(os_item["defeito"])}</div>'
            f'<div class="chip-group">{chips_html}</div>'
            '</div>'
            '<div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">'
            f'{pill_status}'
            f'<span class="mono" style="font-size: 0.75rem; color: #64748B;">Abertura: {data_abertura}</span>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(card_os_html, unsafe_allow_html=True)

        if is_aberta:
            zap_url = gerar_mensagem_whatsapp(
                protocolo=os_item["protocolo"],
                codigo_poste=os_item["codigo_poste"],
                logradouro=os_item.get("logradouro") or "",
                bairro=os_item.get("bairro") or "",
                defeito=os_item["defeito"],
                prioridade=prioridade_item,
                luminaria=f"{os_item.get('tipo_luminaria') or 'LED'} {os_item.get('potencia') or 100}W",
                latitude=os_item.get("latitude"),
                longitude=os_item.get("longitude"),
                materiais=materiais_lista,
            )
            c_acao1, c_acao2, _ = st.columns([1.3, 1.3, 3.4])
            with c_acao1:
                if st.button(
                    f"Concluir O.S. ({os_item['protocolo']})",
                    key=f"btn_concluir_{os_item['protocolo']}",
                    type="primary",
                    use_container_width=True,
                ):
                    concluir_ordem_servico(os_item["protocolo"])
                    st.rerun()
            with c_acao2:
                st.link_button("Despachar via WhatsApp", zap_url, use_container_width=True)
