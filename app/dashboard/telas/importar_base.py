import streamlit as st
import pandas as pd
import io
from app.importer import import_poles_file


def renderizar_tela_importar():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-title">Importar base cadastral COSERN</h1>
                <p class="page-subtitle">Sincronização em lote de ativos de iluminação pública a partir de planilhas Excel ou CSV.</p>
            </div>
            <div class="page-meta">
                <span>Modo: <span class="mono" style="color: #ffffff;">Upsert por plaqueta</span></span>
                <span>Tabelas: Supabase + Local</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.7, 1.3], gap="medium")

    with c1:
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <span class="panel-title">Arquivo da concessionária ou ANEEL</span>
                    <span class="panel-meta">.xlsx · .xls · .csv</span>
                </div>
                <div style="font-size: 13px; color: #8a8c92; margin-bottom: 8px;">
                    O importador reconhece cabeçalhos variados e atualiza automaticamente postes já existentes pelo código da plaqueta.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        arquivo = st.file_uploader(
            "Selecione a planilha de ativos",
            type=["xlsx", "xls", "csv"],
        )

        if arquivo is not None:
            st.markdown(
                f"""
                <div class="panel-card" style="padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; color: #ffffff;">Arquivo carregado: <span class="mono">{arquivo.name}</span></span>
                    <span class="mono" style="font-size: 12px; color: #8a8c92;">{arquivo.size / 1024:.1f} KB</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Processar e sincronizar ativos", type="primary", use_container_width=True):
                with st.spinner("Sincronizando registros com o banco de dados..."):
                    try:
                        conteudo = arquivo.read()
                        resultado = import_poles_file(conteudo, arquivo.name)

                        st.markdown(
                            f"""
                            <div class="panel-card" style="border-color: #44a282; margin-top: 12px;">
                                <div class="panel-header">
                                    <span class="panel-title">Resultado da importação</span>
                                    <span class="status-pill positive">Concluído</span>
                                </div>
                                <div class="kv-list">
                                    <div class="kv-row">
                                        <span class="kv-key">Linhas lidas na planilha</span>
                                        <span class="kv-val mono">{resultado['total_linhas']}</span>
                                    </div>
                                    <div class="kv-row">
                                        <span class="kv-key">Postes inseridos ou atualizados</span>
                                        <span class="kv-val mono">{resultado['importados']}</span>
                                    </div>
                                    <div class="kv-row">
                                        <span class="kv-key">Linhas ignoradas / com erro</span>
                                        <span class="kv-val mono">{resultado['erros']}</span>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.error(f"Falha ao processar arquivo: {str(e)}")

    with c2:
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
            "TIPO_BRACO": ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m"],
        }
        df_exemplo = pd.DataFrame(dados_exemplo)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exemplo.to_excel(writer, index=False, sheet_name="Postes")
        buffer.seek(0)

        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <span class="panel-title">Esquema de colunas aceito</span>
                    <span class="panel-meta">Mapeamento automático</span>
                </div>
                <table class="clean-table">
                    <thead>
                        <tr>
                            <th>Campo</th>
                            <th>Cabeçalhos reconhecidos</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Plaqueta <span style="color: #e5566f;">*</span></td>
                            <td class="mono" style="font-size: 11.5px; color: #8a8c92;">CODIGO, PLAQUETA, PONNOT</td>
                        </tr>
                        <tr>
                            <td>Coordenadas <span style="color: #e5566f;">*</span></td>
                            <td class="mono" style="font-size: 11.5px; color: #8a8c92;">LATITUDE, LONGITUDE, X, Y</td>
                        </tr>
                        <tr>
                            <td>Localização</td>
                            <td class="mono" style="font-size: 11.5px; color: #8a8c92;">LOGRADOURO, RUA, BAIRRO</td>
                        </tr>
                        <tr>
                            <td>Equipamento</td>
                            <td class="mono" style="font-size: 11.5px; color: #8a8c92;">TIPO_LUMINARIA, POTENCIA</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            label="Baixar planilha modelo (.xlsx)",
            data=buffer,
            file_name="modelo_postes_cosern.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
