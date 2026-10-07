"""
Tela: Solicitar Reparo & Kit de Equipamentos (O.S.)
Prepara a ordem de serviço para a viatura com peças necessárias e despacho via WhatsApp.
"""

import streamlit as st
from app.servicos.dados_postes import listar_postes, obter_poste_por_codigo
from app.servicos.ordens_service import criar_ordem_servico, gerar_mensagem_whatsapp

def renderizar_tela_solicitar_reparo():
    st.markdown('<h1 class="montserrat-title">🛠️ Solicitar Reparo & Equipamentos</h1>', unsafe_allow_html=True)
    st.caption("Gere ordens de serviço com a relação de peças necessárias para a viatura ir a campo.")

    # 1. Seleção do Poste
    todos_postes = listar_postes()
    opcoes_postes = {f"{p['codigo']} — {p['logradouro']} ({p['bairro']})": p['codigo'] for p in todos_postes}
    
    codigo_pre_selecionado = st.session_state.get("poste_selecionado_os")
    indice_padrao = 0
    if codigo_pre_selecionado:
        for idx, (label, cod) in enumerate(opcoes_postes.items()):
            if cod == codigo_pre_selecionado:
                indice_padrao = idx
                break

    escolha_poste = st.selectbox(
        "Selecione o Poste para Manutenção:",
        options=list(opcoes_postes.keys()),
        index=indice_padrao if opcoes_postes else 0
    )

    if not opcoes_postes:
        st.warning("Nenhum poste cadastrado no banco de dados.")
        return

    codigo_poste = opcoes_postes[escolha_poste]
    poste = obter_poste_por_codigo(codigo_poste)

    if not poste:
        st.error("Poste não encontrado.")
        return

    # 2. Resumo Visual do Poste
    st.markdown(
        f"""
        <div style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.25); border-radius: 12px; padding: 14px; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 11px; text-transform: uppercase; color: #0284C7; font-weight: 700;">Poste Selecionado</span>
                    <h3 style="margin: 0; color: #FFFFFF; font-family: 'JetBrains Mono'; font-size: 20px;">{poste['codigo']}</h3>
                    <p style="margin: 4px 0 0 0; color: #CBD5E1; font-size: 13px;">📍 {poste['logradouro']} &bull; {poste['bairro']}</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 11px; color: #94A3B8;">Luminária Atual</span>
                    <div style="font-weight: 800; color: #38BDF8; font-size: 14px;">{poste['tipo_luminaria']} {poste['potencia']}W</div>
                    <div style="font-size: 11px; color: #94A3B8;">{poste['tipo_braco']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Formulário da O.S.
    with st.form("form_ordem_servico"):
        st.subheader("1. Diagnóstico do Problema")
        col_def, col_prio = st.columns([2, 1])

        with col_def:
            defeito = st.selectbox(
                "Qual é o defeito reportado?",
                [
                    "Lâmpada apagada durante a noite",
                    "Lâmpada acesa 24 horas (Relé colado)",
                    "Lâmpada piscando / instável",
                    "Luminária quebrada / vandalismo",
                    "Braço de iluminação torto ou caído",
                    "Fiação rompida / curto-circuito",
                    "Poste sem luminária (Nova instalação)",
                    "Outro defeito"
                ]
            )

        with col_prio:
            prioridade = st.selectbox(
                "Prioridade do Atendimento:",
                ["Normal", "Alta", "Urgente (Posto de Saúde / Centro / Risco)"]
            )

        st.subheader("2. Kit de Peças & Equipamentos para a Viatura")
        st.caption("Selecione os materiais que a equipe deve carregar no veículo:")

        # Sugestão inteligente de lâmpada compatível
        label_lampada = f"Lâmpada LED {poste['potencia']}W" if poste['tipo_luminaria'] == "LED" else f"Lâmpada LED {poste['potencia']}W (Substituição de {poste['tipo_luminaria']})"

        c_mat1, c_mat2 = st.columns(2)
        with c_mat1:
            usar_lampada = st.checkbox(label_lampada, value=True)
            qtd_lampada = st.number_input("Qtd Lâmpadas:", min_value=1, max_value=10, value=1, disabled=not usar_lampada)

            usar_rele = st.checkbox("Relé Fotoelétrico 100-240V", value=True)
            qtd_rele = st.number_input("Qtd Relés:", min_value=1, max_value=5, value=1, disabled=not usar_rele)

            usar_conector = st.checkbox("Conectores Perfurantes Dentados", value=True)
            qtd_conector = st.number_input("Qtd Conectores:", min_value=1, max_value=10, value=2, disabled=not usar_conector)

        with c_mat2:
            usar_braco = st.checkbox("Braço de Iluminação Pública 2m", value=False)
            qtd_braco = st.number_input("Qtd Braços:", min_value=1, max_value=5, value=1, disabled=not usar_braco)

            usar_base = st.checkbox("Base / Soquete para Relé", value=False)
            qtd_base = st.number_input("Qtd Bases:", min_value=1, max_value=5, value=1, disabled=not usar_base)

            usar_fita = st.checkbox("Fita Isolante de Alta Fusão", value=True)
            qtd_fita = st.number_input("Qtd Rolos:", min_value=1, max_value=5, value=1, disabled=not usar_fita)

        st.subheader("3. Detalhes Adicionais")
        solicitante = st.text_input("Solicitante / Origem do Chamado:", value="Secretaria de Infraestrutura")
        observacoes = st.text_area("Instruções para a equipe de campo:", placeholder="Ex: Poste em ladeira, levar escada longa...")

        submeter = st.form_submit_button("🚀 Gerar Ordem de Serviço", type="primary", use_container_width=True)

    if submeter:
        # Monta lista de materiais
        materiais = []
        if usar_lampada: materiais.append({"item": f"Lâmpada LED {poste['potencia']}W", "quantidade": qtd_lampada})
        if usar_rele: materiais.append({"item": "Relé Fotoelétrico 100-240V", "quantidade": qtd_rele})
        if usar_conector: materiais.append({"item": "Conector Perfurante Dentado", "quantidade": qtd_conector})
        if usar_braco: materiais.append({"item": "Braço de Iluminação 2m", "quantidade": qtd_braco})
        if usar_base: materiais.append({"item": "Base / Soquete para Relé", "quantidade": qtd_base})
        if usar_fita: materiais.append({"item": "Fita Isolante Alta Fusão", "quantidade": qtd_fita})

        protocolo = criar_ordem_servico(
            codigo_poste=poste["codigo"],
            defeito=defeito,
            prioridade=prioridade.split()[0], # Normal, Alta, Urgente
            materiais=materiais,
            solicitante=solicitante,
            observacoes=observacoes
        )

        st.success(f"✅ Ordem de Serviço **{protocolo}** gerada com sucesso para o poste **{poste['codigo']}**!", icon="🎉")

        # Botão de Envio para WhatsApp
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
            materiais=materiais
        )

        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1.5px solid #10B981; border-radius: 12px; padding: 18px; margin-top: 15px; text-align: center;">
                <h3 style="color: #10B981; margin: 0 0 8px 0; font-family: 'Montserrat';">Despacho para a Viatura</h3>
                <p style="color: #CBD5E1; font-size: 13px; margin-bottom: 15px;">A mensagem com protocolo, rota do Google Maps e lista de peças já foi formatada.</p>
                <a href="{zap_url}" target="_blank" style="background: #10B981; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 14px; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);">
                    📱 ENVIAR ORDEM NO WHATSAPP DO ELETRICISTA
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
