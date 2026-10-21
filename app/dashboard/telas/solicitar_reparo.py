import streamlit as st
from app.servicos.dados_postes import listar_postes, obter_poste_por_codigo
from app.servicos.ordens_service import criar_ordem_servico, gerar_mensagem_whatsapp


def renderizar_tela_solicitar_reparo():
    todos_postes = listar_postes()

    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1 class="page-title">Solicitar reparo e kit de viatura</h1>
                <p class="page-subtitle">Emissão de ordem de serviço com relação de peças e despacho por rota GPS.</p>
            </div>
            <div class="page-meta">
                <span>Ativos disponíveis: <span class="mono" style="color: #ffffff;">{len(todos_postes)}</span></span>
                <span>Secretaria de Infraestrutura</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not todos_postes:
        st.markdown(
            '<div class="panel-card" style="border-style: dashed; color: #8a8c92;">Nenhum poste cadastrado na base para abrir chamado.</div>',
            unsafe_allow_html=True,
        )
        return

    opcoes_postes = {
        f"{p['codigo']} · {p['logradouro']} ({p['bairro']})": p["codigo"] for p in todos_postes
    }

    codigo_pre_selecionado = st.session_state.get("poste_selecionado_os")
    indice_padrao = 0
    if codigo_pre_selecionado:
        for idx, (_, cod) in enumerate(opcoes_postes.items()):
            if cod == codigo_pre_selecionado:
                indice_padrao = idx
                break

    escolha_poste = st.selectbox(
        "Selecione o poste pelo código COSERN ou endereço",
        options=list(opcoes_postes.keys()),
        index=indice_padrao,
    )

    codigo_poste = opcoes_postes[escolha_poste]
    poste = obter_poste_por_codigo(codigo_poste)

    if not poste:
        st.error("Poste não encontrado.")
        return

    status_atual = poste.get("status", "normal")
    if status_atual in ("urgente", "defeito_urgente"):
        pill_status = '<span class="status-pill negative">Defeito urgente</span>'
    elif status_atual == "chamado_aberto":
        pill_status = '<span class="status-pill warning">Chamado aberto</span>'
    else:
        pill_status = '<span class="status-pill positive">Operacional</span>'

    # Object Header Card conforme especificação detail da direção data-terminal
    st.markdown(
        f"""
        <div class="panel-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; padding: 16px 20px; margin-bottom: 20px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="mono" style="font-size: 18px; font-weight: 600; color: #ffffff;">{poste['codigo']}</span>
                    {pill_status}
                </div>
                <div style="font-size: 13px; color: #8a8c92; margin-top: 4px;">
                    {poste['logradouro']} · {poste['bairro']}{f" · {poste['referencia']}" if poste.get('referencia') else ""}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #8a8c92;">Conjunto instalado</div>
                <div style="font-size: 13.5px; font-weight: 500; color: #ffffff; margin-top: 2px;">
                    {poste['tipo_luminaria']} <span class="mono">{poste['potencia']}W</span> · {poste['tipo_braco']}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_ordem_servico"):
        st.markdown(
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">Diagnóstico da ocorrência</div>',
            unsafe_allow_html=True,
        )
        col_def, col_prio = st.columns([2, 1])

        with col_def:
            defeito = st.selectbox(
                "Defeito constatado",
                [
                    "Lâmpada apagada durante a noite",
                    "Lâmpada acesa 24 horas (Relé colado)",
                    "Lâmpada piscando / instável",
                    "Luminária quebrada / vandalismo",
                    "Braço de iluminação torto ou caído",
                    "Fiação rompida / curto-circuito",
                    "Poste sem luminária (Nova instalação)",
                    "Outro defeito",
                ],
            )

        with col_prio:
            prioridade = st.selectbox(
                "Prioridade de atendimento",
                ["Normal", "Alta", "Urgente (Posto de Saúde / Centro / Risco)"],
            )

        st.markdown(
            '<div style="height: 1px; background: #1b1a1f; margin: 16px 0;"></div>'
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 4px;">Kit de peças para a viatura</div>'
            '<div style="font-size: 12.5px; color: #8a8c92; margin-bottom: 14px;">Marque os insumos que o eletricista deve embarcar antes da saída.</div>',
            unsafe_allow_html=True,
        )

        label_lampada = (
            f"Lâmpada LED {poste['potencia']}W"
            if poste["tipo_luminaria"] == "LED"
            else f"Lâmpada LED {poste['potencia']}W (substitui {poste['tipo_luminaria']})"
        )

        c_mat1, c_mat2 = st.columns(2)
        with c_mat1:
            usar_lampada = st.checkbox(label_lampada, value=True)
            qtd_lampada = st.number_input(
                "Quantidade de lâmpadas", min_value=1, max_value=10, value=1, disabled=not usar_lampada
            )

            usar_rele = st.checkbox("Relé fotoelétrico 100–240V", value=True)
            qtd_rele = st.number_input(
                "Quantidade de relés", min_value=1, max_value=5, value=1, disabled=not usar_rele
            )

            usar_conector = st.checkbox("Conector perfurante dentado", value=True)
            qtd_conector = st.number_input(
                "Quantidade de conectores", min_value=1, max_value=10, value=2, disabled=not usar_conector
            )

        with c_mat2:
            usar_braco = st.checkbox("Braço de iluminação pública 2m", value=False)
            qtd_braco = st.number_input(
                "Quantidade de braços", min_value=1, max_value=5, value=1, disabled=not usar_braco
            )

            usar_base = st.checkbox("Base / soquete para relé", value=False)
            qtd_base = st.number_input(
                "Quantidade de bases", min_value=1, max_value=5, value=1, disabled=not usar_base
            )

            usar_fita = st.checkbox("Fita isolante de alta fusão", value=True)
            qtd_fita = st.number_input(
                "Quantidade de rolos", min_value=1, max_value=5, value=1, disabled=not usar_fita
            )

        st.markdown(
            '<div style="height: 1px; background: #1b1a1f; margin: 16px 0;"></div>',
            unsafe_allow_html=True,
        )

        c_orig, c_obs = st.columns([1, 1.5])
        with c_orig:
            solicitante = st.text_input(
                "Origem da solicitação", value="Secretaria de Infraestrutura"
            )
        with c_obs:
            observacoes = st.text_input(
                "Instruções para a equipe de campo",
                placeholder="Ex: Levar escada extensível, poste próximo à esquina...",
            )

        submeter = st.form_submit_button(
            "Emitir ordem de serviço", type="primary", use_container_width=True
        )

    if submeter:
        materiais = []
        if usar_lampada:
            materiais.append({"item": f"Lâmpada LED {poste['potencia']}W", "quantidade": qtd_lampada})
        if usar_rele:
            materiais.append({"item": "Relé fotoelétrico 100-240V", "quantidade": qtd_rele})
        if usar_conector:
            materiais.append({"item": "Conector perfurante dentado", "quantidade": qtd_conector})
        if usar_braco:
            materiais.append({"item": "Braço de iluminação 2m", "quantidade": qtd_braco})
        if usar_base:
            materiais.append({"item": "Base / soquete para relé", "quantidade": qtd_base})
        if usar_fita:
            materiais.append({"item": "Fita isolante alta fusão", "quantidade": qtd_fita})

        protocolo = criar_ordem_servico(
            codigo_poste=poste["codigo"],
            defeito=defeito,
            prioridade=prioridade.split()[0],
            materiais=materiais,
            solicitante=solicitante,
            observacoes=observacoes,
        )

        zap_url = gerar_mensagem_whatsapp(
            protocolo=protocolo,
            codigo_poste=poste["codigo"],
            logradouro=poste["logradouro"],
            bairro=poste["bairro"],
            defeito=defeito,
            prioridade=prioridade,
            luminaria=f"{poste['tipo_luminaria']} {poste['potencia']}W",
            latitude=poste["latitude"],
            longitude=poste["longitude"],
            materiais=materiais,
        )

        st.markdown(
            f"""
            <div class="panel-card" style="border-color: #44a282; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="status-pill positive">O.S. registrada</span>
                        <span class="mono" style="font-size: 15px; font-weight: 600; color: #ffffff;">{protocolo}</span>
                    </div>
                    <div style="font-size: 13px; color: #8a8c92; margin-top: 6px;">
                        Poste <span class="mono" style="color: #ffffff;">{poste['codigo']}</span> atualizado na base. Despache a ficha técnica para o eletricista.
                    </div>
                </div>
                <a href="{zap_url}" target="_blank" style="background: #ffffff; color: #111111; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px; display: inline-flex; align-items: center;">
                    Enviar despacho via WhatsApp
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
