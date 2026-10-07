"""
Tela: Importar Base da COSERN / ANEEL
Permite carregar planilhas de postes em Excel ou CSV e alimentar o banco de dados.
"""

import streamlit as st
import pandas as pd
import io
from app.importer import import_poles_file

def renderizar_tela_importar():
    st.markdown('<h1 class="montserrat-title">📥 Importar Base da COSERN</h1>', unsafe_allow_html=True)
    st.caption("Alimente o banco com a relação de postes enviada pela concessionária ou baixada da ANEEL.")

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("1. Carregar Arquivo de Planilha")
        arquivo = st.file_uploader(
            "Arraste a planilha ou clique para selecionar:",
            type=["xlsx", "xls", "csv"],
            help="O sistema aceita planilhas com colunas de código, latitude, longitude, endereço e tipo de luminária."
        )

        if arquivo is not None:
            st.info(f"Arquivo selecionado: **{arquivo.name}** ({arquivo.size / 1024:.1f} KB)")
            
            if st.button("🚀 Processar e Salvar Postes no Banco", type="primary", use_container_width=True):
                with st.spinner("Lendo arquivo e atualizando banco de dados com Python..."):
                    try:
                        conteudo = arquivo.read()
                        resultado = import_poles_file(conteudo, arquivo.name)
                        
                        st.success(f"🎉 Importação concluída com sucesso!")
                        st.write(f"- Total de linhas lidas: **{resultado['total_linhas']}**")
                        st.write(f"- Postes cadastrados / atualizados: **{resultado['importados']}**")
                        if resultado["erros"] > 0:
                            st.warning(f"Avisos em {resultado['erros']} linhas.")
                    except Exception as e:
                        st.error(f"Erro ao processar arquivo: {str(e)}")

    with c2:
        st.subheader("2. Modelo Padrão")
        st.write("Se ainda não tiver a planilha da COSERN formatada, você pode baixar nosso modelo pronto:")

        # Gera modelo Excel em memória
        dados_exemplo = {
            "CODIGO_POSTE": ["CSR-2001", "CSR-2002", "CSR-2003"],
            "LATITUDE": [-6.1615, -6.1620, -6.1628],
            "LONGITUDE": [-35.6022, -35.6031, -35.6040],
            "LOGRADOURO": ["Rua Principal", "Travessa São Pedro", "Av. Brasil"],
            "BAIRRO": ["Centro", "Centro", "Bela Vista"],
            "REFERENCIA": ["Ao lado do colégio", "Próximo à praça", "Em frente ao posto"],
            "TIPO_LUMINARIA": ["LED", "Vapor de Sódio", "LED"],
            "POTENCIA_WATTS": [100, 70, 150],
            "TIPO_POSTE": ["Concreto Duplo T", "Concreto Circular", "Concreto Duplo T"],
            "TIPO_BRACO": ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m"]
        }
        df_exemplo = pd.DataFrame(dados_exemplo)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exemplo.to_excel(writer, index=False, sheet_name="Postes")
        buffer.seek(0)

        st.download_button(
            label="📄 Baixar Planilha Modelo (.xlsx)",
            data=buffer,
            file_name="modelo_postes_cosern.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown(
            """
            **Colunas reconhecidas automaticamente:**
            - **Código:** `CODIGO`, `PLAQUETA`, `BARRAMENTO`
            - **Coordenadas:** `LATITUDE` e `LONGITUDE`
            - **Endereço:** `LOGRADOURO`, `RUA`, `BAIRRO`
            - **Luminária:** `TIPO_LUMINARIA`, `POTENCIA`
            """
        )
