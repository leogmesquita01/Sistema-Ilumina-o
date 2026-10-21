import streamlit as st
from app.servicos.dados_postes import cadastrar_poste


def renderizar_tela_cadastrar():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-title">Cadastrar poste em campo</h1>
                <p class="page-subtitle">Registro individual de ativo de iluminação pública na base própria do município.</p>
            </div>
            <div class="page-meta">
                <span>Destino: <span class="mono" style="color: #ffffff;">Supabase · public.postes</span></span>
                <span>Secretaria de Infraestrutura</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_cadastrar_poste"):
        st.markdown(
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">Identificação e localização</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            codigo = st.text_input("Código / Identificação do poste", placeholder="Ex: P-01, CSR-1099...")
            logradouro = st.text_input("Logradouro / Rua", placeholder="Ex: Rua Manoel Cirilo")

        with c2:
            bairro = st.text_input("Bairro ou comunidade rural", value="Centro")
            referencia = st.text_input("Ponto de referência", placeholder="Ex: Em frente à UBS")

        st.markdown(
            '<div style="height: 1px; background: #1b1a1f; margin: 16px 0;"></div>'
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">Luminária e estrutura física</div>',
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

        salvar = st.form_submit_button("Registrar poste na base", type="primary", use_container_width=True)

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
                <div class="panel-card" style="border-color: #44a282; margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="status-pill positive">Ativo gravado</span>
                        <span style="font-size: 13px; color: #ffffff; margin-left: 10px;">
                            Poste <span class="mono" style="font-weight: 600;">{codigo.strip()}</span> cadastrado com sucesso no Supabase.
                        </span>
                    </div>
                    <span style="font-size: 12px; color: #8a8c92;">{logradouro or 'Não informado'} · {bairro}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Erro ao cadastrar poste: {str(e)}")
