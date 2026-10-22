import streamlit as st
from app.servicos.dados_postes import cadastrar_poste, listar_postes


def renderizar_tela_cadastrar():
    todos_postes = listar_postes()
    total_atual = len(todos_postes)

    sidebar_reduzida = st.session_state.get("sidebar_reduzida", False)
    sb_target = st.session_state.get("sb_card")

    if not sidebar_reduzida and sb_target is not None:
        with sb_target:
            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; margin-bottom: 8px;">Padrão de Campo</div>',
                unsafe_allow_html=True,
            )
            bairro_padrao = st.text_input("Bairro padrão", value="Centro", key="cad_bairro_padrao")
            potencia_padrao = st.selectbox("Potência padrão (W)", [50, 70, 100, 150, 200], index=2, key="cad_pot_padrao")

            if todos_postes:
                ultimos_html = "".join(
                    [
                        f'<div style="display:flex; justify-content:space-between; font-size:0.74rem; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><span class="mono" style="color:#34D399; font-weight:700;">{p["codigo"]}</span><span style="color:#94A3B8; max-width:110px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{p["bairro"]}</span></div>'
                        for p in todos_postes[-4:]
                    ]
                )
                st.markdown(
                    '<div style="background:#0A101A; border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:10px 12px; margin-top:8px;">'
                    '<div style="font-size:0.7rem; color:#F8FAFC; font-weight:600; margin-bottom:6px;">Últimos Cadastrados</div>'
                    f'{ultimos_html}'
                    '</div>',
                    unsafe_allow_html=True,
                )
    else:
        bairro_padrao = "Centro"
        potencia_padrao = 100

    st.markdown(
        f"""
        <div class="command-hero">
            <div>
                <div class="hero-badge">
                    <span class="hero-dot"></span>
                    Inventário Municipal · Base Própria
                </div>
                <h1 class="hero-title">Cadastrar Poste em Campo</h1>
                <p class="hero-subtitle">Registro rápido de ativo de iluminação pública sem necessidade de coordenadas GPS.</p>
            </div>
            <div class="hero-right">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">Base Sincronizada</div>
                <div class="mono" style="font-size: 1.05rem; font-weight: 700; color: #10B981; margin-top: 2px;">{total_atual} Postes</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Supabase · public.postes</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_cadastrar_poste"):
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="status-pill positive">Localização</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Identificação e Endereço</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            codigo = st.text_input("Código / Identificação do poste", placeholder="Ex: P-01, Posto-02, RuaA-05...")
            logradouro = st.text_input("Logradouro / Rua", placeholder="Ex: Rua Manoel Cirilo")

        with c2:
            bairro = st.text_input("Bairro ou comunidade rural", value=bairro_padrao)
            referencia = st.text_input("Ponto de referência", placeholder="Ex: Em frente à UBS / Próximo à praça")

        st.markdown(
            """
            <div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 18px 0;"></div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="status-pill neutral">Especificação</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Luminária e Estrutura Física</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c3, c4 = st.columns(2)
        with c3:
            luminaria = st.selectbox(
                "Tecnologia da luminária",
                ["LED", "Vapor de Sódio", "Vapor de Mercúrio", "Sem Luminária"],
            )
            tipo_poste = st.selectbox(
                "Tipo de estrutura",
                ["Concreto Duplo T", "Concreto Circular", "Madeira Tratada", "Metálico"],
            )
        with c4:
            potencia = st.number_input("Potência nominal (Watts)", value=int(potencia_padrao), step=10)
            tipo_braco = st.selectbox(
                "Tipo de braço",
                ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m", "Pétala Dupla", "Topo de Poste"],
            )

        observacoes = st.text_area(
            "Observações técnicas",
            placeholder="Condição do relé fotoelétrico, presença de transformador, estado da fiação...",
        )

        salvar = st.form_submit_button("Registrar Poste na Base", type="primary", use_container_width=True)

    if salvar:
        if not codigo or not codigo.strip():
            st.error("Informe o código de identificação para registrar o poste.")
            return

        try:
            cadastrar_poste({
                "codigo": codigo,
                "logradouro": logradouro,
                "bairro": bairro,
                "referencia": referencia,
                "tipo_luminaria": luminaria,
                "potencia": potencia,
                "tipo_poste": tipo_poste,
                "tipo_braco": tipo_braco,
                "observacoes": observacoes,
            })
            st.markdown(
                f"""
                <div class="panel-card" style="border-color: #10B981; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <span class="status-pill positive">Ativo Registrado</span>
                        <span style="font-size: 0.9rem; color: #FFFFFF; margin-left: 10px;">
                            Poste <span class="mono" style="font-weight: 700; color: #34D399;">{codigo.strip()}</span> gravado com sucesso no banco de dados.
                        </span>
                    </div>
                    <span style="font-size: 0.82rem; color: #94A3B8;">{logradouro or 'Não informado'} · {bairro}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Erro ao cadastrar poste: {str(e)}")
