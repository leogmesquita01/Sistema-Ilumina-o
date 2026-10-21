import streamlit as st
from app.servicos.ordens_service import listar_ordens, concluir_ordem_servico, gerar_mensagem_whatsapp


def renderizar_tela_ordens_servico():
    todas_ordens = listar_ordens(filtro_status="Todos")
    abertas = [o for o in todas_ordens if o.get("status") == "aberta"]
    urgentes = [o for o in abertas if o.get("prioridade") == "Urgente"]
    concluidas = [o for o in todas_ordens if o.get("status") == "concluida"]

    finding = (
        f"{len(abertas)} ordens aguardam execução ({len(urgentes)} de prioridade urgente)."
        if abertas
        else "Nenhuma ordem de serviço pendente na fila."
    )

    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1 class="page-title">Ordens de serviço e fila de campo</h1>
                <p class="page-subtitle">{finding}</p>
            </div>
            <div class="page-meta">
                <span>Total histórico: <span class="mono" style="color: #ffffff;">{len(todas_ordens)}</span></span>
                <span>Secretaria de Infraestrutura</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI Strip de 3 colunas para a fila de O.S.
    cor_urgente = "color: #e5566f;" if len(urgentes) > 0 else ""
    st.markdown(
        f"""
        <div class="kpi-strip" style="grid-template-columns: repeat(3, 1fr);">
            <div class="kpi-cell">
                <div class="kpi-label">Ordens em aberto</div>
                <div class="kpi-value-row">
                    <span class="kpi-value lead">{len(abertas)}</span>
                    <span class="kpi-unit">na fila</span>
                </div>
                <div class="kpi-sub">Aguardando baixa da equipe</div>
            </div>
            <div class="kpi-cell">
                <div class="kpi-label">Prioridade urgente</div>
                <div class="kpi-value-row">
                    <span class="kpi-value" style="{cor_urgente}">{len(urgentes)}</span>
                    <span class="kpi-unit">chamados</span>
                </div>
                <div class="kpi-sub">Unidades de saúde, centro ou risco</div>
            </div>
            <div class="kpi-cell">
                <div class="kpi-label">Reparos concluídos</div>
                <div class="kpi-value-row">
                    <span class="kpi-value">{len(concluidas)}</span>
                    <span class="kpi-unit">finalizados</span>
                </div>
                <div class="kpi-sub">Postes normalizados na rede</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_filtro, c_busca = st.columns([1.2, 2.8])
    with c_filtro:
        mapa_filtro = {
            "Todas as ordens": "Todos",
            "Em aberto": "aberta",
            "Concluídas": "concluida",
        }
        escolha = st.selectbox("Status da ordem", list(mapa_filtro.keys()))
        filtro_status = mapa_filtro[escolha]

    with c_busca:
        termo = st.text_input(
            "Filtrar por protocolo, plaqueta ou endereço",
            placeholder="Ex: OS-2026-0001, CSR-1002, Rua Severino Ramos...",
        )

    ordens = listar_ordens(filtro_status=filtro_status)
    if termo and termo.strip():
        t = termo.strip().lower()
        ordens = [
            o
            for o in ordens
            if t in o.get("protocolo", "").lower()
            or t in o.get("codigo_poste", "").lower()
            or t in o.get("logradouro", "").lower()
            or t in o.get("defeito", "").lower()
        ]

    if not ordens:
        st.markdown(
            '<div class="panel-card" style="border-style: dashed; color: #8a8c92;">Nenhuma ordem de serviço encontrada para os critérios selecionados.</div>',
            unsafe_allow_html=True,
        )
        return

    for os_item in ordens:
        is_aberta = os_item["status"] == "aberta"
        prioridade_item = os_item.get("prioridade", "Normal")

        if not is_aberta:
            pill_status = '<span class="status-pill positive">Concluída</span>'
        elif prioridade_item == "Urgente":
            pill_status = '<span class="status-pill negative">Aberta · Urgente</span>'
        else:
            pill_status = f'<span class="status-pill warning">Aberta · {prioridade_item}</span>'

        materiais_lista = os_item.get("materiais_lista", [])
        materiais_str = (
            " · ".join([f"{m.get('quantidade', 1)}x {m.get('item', '')}" for m in materiais_lista])
            if materiais_lista
            else "Vistoria no local"
        )
        data_abertura = str(os_item.get("data_abertura", ""))[:10] or "—"

        st.markdown(
            f"""
            <div class="panel-card" style="margin-bottom: 10px; padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="mono" style="font-size: 15px; font-weight: 600; color: #ffffff;">{os_item['protocolo']}</span>
                            <span class="mono" style="font-size: 13px; color: #4a8ad6;">{os_item['codigo_poste']}</span>
                            <span style="font-size: 13px; color: #8a8c92;">{os_item.get('logradouro', '')} · {os_item.get('bairro', '')}</span>
                        </div>
                        <div style="font-size: 13.5px; color: #ffffff; margin-top: 8px; font-weight: 500;">
                            {os_item['defeito']}
                        </div>
                        <div style="font-size: 12.5px; color: #8a8c92; margin-top: 4px;">
                            Kit de materiais: <span style="color: #bdbdc0;">{materiais_str}</span>
                        </div>
                    </div>
                    <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                        {pill_status}
                        <span class="mono" style="font-size: 11.5px; color: #8a8c92;">Abertura: {data_abertura}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_aberta:
            zap_url = gerar_mensagem_whatsapp(
                protocolo=os_item["protocolo"],
                codigo_poste=os_item["codigo_poste"],
                logradouro=os_item.get("logradouro", ""),
                bairro=os_item.get("bairro", ""),
                defeito=os_item["defeito"],
                prioridade=prioridade_item,
                luminaria=f"{os_item.get('tipo_luminaria', 'LED')} {os_item.get('potencia', 100)}W",
                latitude=os_item.get("latitude", -6.1611),
                longitude=os_item.get("longitude", -35.6025),
                materiais=materiais_lista,
            )
            c_acao1, c_acao2, _ = st.columns([1.2, 1.2, 3.6])
            with c_acao1:
                if st.button(
                    f"Dar baixa ({os_item['protocolo']})",
                    key=f"btn_concluir_{os_item['protocolo']}",
                    type="primary",
                    use_container_width=True,
                ):
                    concluir_ordem_servico(os_item["protocolo"])
                    st.rerun()
            with c_acao2:
                st.link_button("Despachar via WhatsApp", zap_url, use_container_width=True)
