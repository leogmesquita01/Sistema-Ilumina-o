import streamlit as st
from app.servicos.dados_postes import listar_postes, obter_poste_por_codigo, cadastrar_poste
from app.servicos.ordens_service import criar_ordem_servico, gerar_mensagem_whatsapp


def renderizar_tela_solicitar_reparo():
    todos_postes = listar_postes()

    st.markdown(
        f"""
        <div class="command-hero">
            <div>
                <div class="hero-badge">
                    <span class="hero-dot"></span>
                    Despacho Operacional · Equipe de Campo
                </div>
                <h1 class="hero-title">Solicitar Reparo e Kit de Viatura</h1>
                <p class="hero-subtitle">Emissão de Ordem de Serviço com checklist de peças para embarque na viatura e envio imediato via WhatsApp.</p>
            </div>
            <div class="hero-right">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">Ativos na Base</div>
                <div class="mono" style="font-size: 1.05rem; font-weight: 700; color: #10B981; margin-top: 2px;">{len(todos_postes)} Postes</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Secretaria de Infraestrutura</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    modo_novo_poste = False
    poste = None

    with st.sidebar:
        st.markdown(
            '<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; margin-bottom: 8px;">Seleção do Ativo</div>',
            unsafe_allow_html=True,
        )
        if todos_postes:
            opcoes_postes = {
                f"{p['codigo']} · {p['logradouro']} ({p['bairro']})": p["codigo"] for p in todos_postes
            }
            opcoes_lista = list(opcoes_postes.keys()) + ["+ Novo poste não listado"]

            codigo_pre_selecionado = st.session_state.get("poste_selecionado_os")
            indice_padrao = 0
            if codigo_pre_selecionado:
                for idx, (_, cod) in enumerate(opcoes_postes.items()):
                    if cod == codigo_pre_selecionado:
                        indice_padrao = idx
                        break

            escolha_poste = st.selectbox(
                "Poste para reparo",
                options=opcoes_lista,
                index=indice_padrao,
                key="reparo_poste_sidebar",
            )

            if escolha_poste == "+ Novo poste não listado":
                modo_novo_poste = True
            else:
                codigo_poste = opcoes_postes[escolha_poste]
                poste = obter_poste_por_codigo(codigo_poste)
        else:
            modo_novo_poste = True
            st.caption("Nenhum poste cadastrado. Preencha os dados ao lado.")

        if poste and not modo_novo_poste:
            st.markdown(
                '<div style="background: #0A101A; border: 1px solid rgba(16,185,129,0.25); border-radius: 14px; padding: 10px 12px; margin-top: 6px;">'
                f'<div class="mono" style="font-size: 0.9rem; font-weight: 800; color: #FFFFFF;">{poste["codigo"]}</div>'
                f'<div style="font-size: 0.74rem; color: #94A3B8; margin-top: 2px;">{poste["logradouro"]} · {poste["bairro"]}</div>'
                f'<div class="mono" style="font-size: 0.72rem; color: #34D399; margin-top: 4px;">{poste["tipo_luminaria"]} {poste["potencia"]}W</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    if poste and not modo_novo_poste:
        status_atual = poste.get("status", "normal")
        if status_atual in ("urgente", "defeito_urgente"):
            pill_status = '<span class="status-pill negative">Defeito Urgente</span>'
        elif status_atual == "chamado_aberto":
            pill_status = '<span class="status-pill warning">O.S. em Aberto</span>'
        else:
            pill_status = '<span class="status-pill positive">Operacional</span>'

        ref_txt = f" · {poste['referencia']}" if poste.get("referencia") else ""
        card_poste_html = (
            '<div class="panel-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; border-color: rgba(16, 185, 129, 0.28);">'
            '<div>'
            '<div style="display: flex; align-items: center; gap: 10px;">'
            f'<span class="mono" style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF;">{poste["codigo"]}</span>'
            f'{pill_status}'
            '</div>'
            '<div style="font-size: 0.88rem; color: #94A3B8; margin-top: 4px;">'
            f'{poste["logradouro"]} · <strong style="color: #E2E8F0;">{poste["bairro"]}</strong>{ref_txt}'
            '</div>'
            '</div>'
            '<div style="display: flex; gap: 12px;">'
            '<div class="spec-tile" style="padding: 8px 14px;">'
            '<div class="spec-tile-label">Luminária</div>'
            f'<div class="spec-tile-val">{poste["tipo_luminaria"]} <span class="mono" style="color: #34D399;">{poste["potencia"]}W</span></div>'
            '</div>'
            '<div class="spec-tile" style="padding: 8px 14px;">'
            '<div class="spec-tile-label">Braço / Suporte</div>'
            f'<div class="spec-tile-val">{poste["tipo_braco"]}</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(card_poste_html, unsafe_allow_html=True)

    with st.form("form_ordem_servico"):
        if modo_novo_poste:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span class="status-pill positive">1</span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Identificação do Poste</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cp1, cp2, cp3 = st.columns([1, 1.6, 1])
            with cp1:
                novo_codigo = st.text_input("Código / Identificação do poste", placeholder="Ex: P-01, Posto-04...")
            with cp2:
                novo_logradouro = st.text_input("Logradouro / Rua", placeholder="Ex: Rua Manoel Cirilo")
            with cp3:
                novo_bairro = st.text_input("Bairro / Comunidade", value="Centro")
            st.markdown(
                '<div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 18px 0;"></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="status-pill warning">Diagnóstico</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Ocorrência Constatada em Campo</span>
            </div>
            """,
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
            """
            <div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 18px 0;"></div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="status-pill positive">Kit Viatura</span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Relação de Peças e Materiais</span>
                </div>
                <span style="font-size: 0.78rem; color: #94A3B8;">Insumos que o eletricista deve embarcar</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        potencia_ref = poste["potencia"] if poste else 100
        label_lampada = f"Lâmpada LED {potencia_ref}W"

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
            '<div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 18px 0;"></div>',
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
            "Emitir Ordem de Serviço", type="primary", use_container_width=True
        )

    if submeter:
        if modo_novo_poste:
            if not novo_codigo or not novo_codigo.strip():
                st.error("Informe o código ou identificação do poste.")
                return
            cod_alvo = novo_codigo.strip()
            log_alvo = novo_logradouro.strip() if novo_logradouro else "Não informado"
            bairro_alvo = novo_bairro.strip() if novo_bairro else "Centro"
            lum_alvo = "LED 100W"

            existente = obter_poste_por_codigo(cod_alvo)
            if not existente:
                cadastrar_poste({
                    "codigo": cod_alvo,
                    "logradouro": log_alvo,
                    "bairro": bairro_alvo,
                })
        else:
            cod_alvo = poste["codigo"]
            log_alvo = poste["logradouro"]
            bairro_alvo = poste["bairro"]
            lum_alvo = f"{poste['tipo_luminaria']} {poste['potencia']}W"

        materiais = []
        if usar_lampada:
            materiais.append({"item": f"Lâmpada LED {potencia_ref}W", "quantidade": qtd_lampada})
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
            codigo_poste=cod_alvo,
            defeito=defeito,
            prioridade=prioridade.split()[0],
            materiais=materiais,
            solicitante=solicitante,
            observacoes=observacoes,
        )

        zap_url = gerar_mensagem_whatsapp(
            protocolo=protocolo,
            codigo_poste=cod_alvo,
            logradouro=log_alvo,
            bairro=bairro_alvo,
            defeito=defeito,
            prioridade=prioridade,
            luminaria=lum_alvo,
            materiais=materiais,
        )

        st.markdown(
            f"""
            <div class="panel-card" style="border-color: #10B981; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="status-pill positive">O.S. Emitida</span>
                        <span class="mono" style="font-size: 1.1rem; font-weight: 800; color: #FFFFFF;">{protocolo}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 6px;">
                        Poste <span class="mono" style="color: #F8FAFC; font-weight: 700;">{cod_alvo}</span> atualizado na base. Envie o despacho para o eletricista:
                    </div>
                </div>
                <a href="{zap_url}" target="_blank" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: #FFFFFF; padding: 10px 18px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 0.86rem; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);">
                    Enviar Despacho via WhatsApp
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
