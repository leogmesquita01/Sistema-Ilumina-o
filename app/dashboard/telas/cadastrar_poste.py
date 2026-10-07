"""
Tela: Cadastrar Poste Manualmente (Modo Campo)
"""

import streamlit as st
from app.servicos.dados_postes import cadastrar_poste

def renderizar_tela_cadastrar():
    st.markdown('<h1 class="montserrat-title">➕ Cadastrar Novo Poste</h1>', unsafe_allow_html=True)
    st.caption("Cadastre postes avulsos identificados em campo pela equipe da Secretaria de Infraestrutura.")

    with st.form("form_cadastrar_poste"):
        c1, c2 = st.columns(2)
        with c1:
            codigo = st.text_input("Código da Plaqueta COSERN:", placeholder="Ex: CSR-1099")
            logradouro = st.text_input("Logradouro / Rua:", placeholder="Ex: Rua Nova")
            bairro = st.text_input("Bairro ou Comunidade:", value="Centro")
            referencia = st.text_input("Ponto de Referência:", placeholder="Ex: Próximo à padaria")

        with c2:
            lat = st.number_input("Latitude:", value=-6.1611, format="%.6f")
            lng = st.number_input("Longitude:", value=-35.6025, format="%.6f")
            luminaria = st.selectbox("Tipo de Luminária:", ["LED", "Vapor de Sódio", "Vapor de Mercúrio", "Sem Luminária"])
            potencia = st.number_input("Potência (Watts):", value=100, step=10)

        observacoes = st.text_area("Observações Técnicas:", placeholder="Estrutura, estado de conservação, etc.")

        salvar = st.form_submit_button("💾 Salvar Poste no Banco", type="primary", use_container_width=True)

    if salvar:
        if not codigo:
            st.error("Informe o código da plaqueta do poste.")
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
                "observacoes": observacoes
            })
            st.success(f"Poste **{codigo}** cadastrado com sucesso no banco de dados!")
        except Exception as e:
            st.error(f"Erro ao cadastrar poste: {str(e)}")
