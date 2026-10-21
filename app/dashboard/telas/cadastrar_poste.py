import streamlit as st
from app.servicos.dados_postes import cadastrar_poste


def renderizar_tela_cadastrar():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-title">Cadastrar poste em campo</h1>
                <p class="page-subtitle">Registro individual de ativo de iluminação pública georreferenciado na malha de Boa Saúde / RN.</p>
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
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">Identificação e coordenadas</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            codigo = st.text_input("Código da plaqueta COSERN", placeholder="Ex: CSR-1099")
            logradouro = st.text_input("Logradouro / Rua", placeholder="Ex: Rua Manoel Cirilo")
            bairro = st.text_input("Bairro ou comunidade rural", value="Centro")
            referencia = st.text_input("Ponto de referência", placeholder="Ex: Em frente à UBS")

        with c2:
            lat = st.number_input("Latitude (graus decimais)", value=-6.161100, format="%.6f")
            lng = st.number_input("Longitude (graus decimais)", value=-35.602500, format="%.6f")
            luminaria = st.selectbox(
                "Tecnologia da luminária",
                ["LED", "Vapor de Sódio", "Vapor de Mercúrio", "Sem Luminária"],
            )
            potencia = st.number_input("Potência nominal (Watts)", value=100, step=10)

        st.markdown(
            '<div style="height: 1px; background: #1b1a1f; margin: 16px 0;"></div>'
            '<div style="font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">Estrutura física</div>',
            unsafe_allow_html=True,
        )

        c3, c4 = st.columns(2)
        with c3:
            tipo_poste = st.selectbox(
                "Tipo de estrutura",
                ["Concreto Duplo T", "Concreto Circular", "Madeira Tratada", "Metálico"],
            )
        with c4:
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
            st.error("Informe o código da plaqueta COSERN para registrar o poste.")
            return

        try:
            cadastrar_poste({
                "codigo": codigo,
                "latitude": lat,
                "longitude": lng,
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
                    <span class="mono" style="font-size: 12px; color: #8a8c92;">{lat:.5f}, {lng:.5f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Erro ao cadastrar poste: {str(e)}")
