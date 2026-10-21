import streamlit as st
from app.servicos.dados_postes import cadastrar_poste, listar_postes


def renderizar_tela_cadastrar():
    total_atual = len(listar_postes())

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
            bairro = st.text_input("Bairro ou comunidade rural", value="Centro")
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
            potencia = st.number_input("Potência nominal (Watts)", value=100, step=10)
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
