import streamlit as st
import pandas as pd
import io
from app.importer import import_poles_file


def renderizar_tela_importar():
    st.markdown(
        """
        <div class="command-hero">
            <div>
                <div class="hero-badge">
                    <span class="hero-dot"></span>
                    Importação em Lote · Planilhas de Campo
                </div>
                <h1 class="hero-title">Importar Planilha de Postes</h1>
                <p class="hero-subtitle">Carregue a relação de postes já anotados pela equipe em Excel ou CSV para alimentar o banco do município.</p>
            </div>
            <div class="hero-right">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;">Sincronização</div>
                <div class="mono" style="font-size: 1.02rem; font-weight: 700; color: #10B981; margin-top: 2px;">Upsert por Código</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Sem exigir coordenadas</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.65, 1.35], gap="medium")

    with c1:
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <span class="panel-title">Upload da Planilha da Equipe</span>
                    <span class="panel-meta">.XLSX · .XLS · .CSV</span>
                </div>
                <div style="font-size: 0.86rem; color: #94A3B8; line-height: 1.5;">
                    Envie sua planilha com os postes anotados em campo. O sistema reconhece automaticamente as colunas de código, rua, bairro, referência e potência, atualizando o Supabase sem exigir latitude ou longitude.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        arquivo = st.file_uploader(
            "Selecione a planilha de postes (.xlsx, .xls ou .csv)",
            type=["xlsx", "xls", "csv"],
        )

        if arquivo is not None:
            st.markdown(
                f"""
                <div class="panel-card" style="padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; border-color: rgba(16, 185, 129, 0.35);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="status-pill positive">Pronto</span>
                        <span style="font-size: 0.88rem; color: #FFFFFF; font-weight: 600;">{arquivo.name}</span>
                    </div>
                    <span class="mono" style="font-size: 0.78rem; color: #94A3B8;">{arquivo.size / 1024:.1f} KB</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Processar e Salvar Postes na Base", type="primary", use_container_width=True):
                with st.spinner("Sincronizando registros com o banco de dados..."):
                    try:
                        conteudo = arquivo.read()
                        resultado = import_poles_file(conteudo, arquivo.name)

                        st.markdown(
                            f"""
                            <div class="panel-card" style="border-color: #10B981; margin-top: 14px;">
                                <div class="panel-header">
                                    <span class="panel-title">Resumo da Importação</span>
                                    <span class="status-pill positive">Concluído</span>
                                </div>
                                <div class="spec-grid" style="grid-template-columns: repeat(3, 1fr);">
                                    <div class="spec-tile">
                                        <div class="spec-tile-label">Linhas Lidas</div>
                                        <div class="spec-tile-val mono">{resultado['total_linhas']}</div>
                                    </div>
                                    <div class="spec-tile">
                                        <div class="spec-tile-label">Salvos / Atualizados</div>
                                        <div class="spec-tile-val mono" style="color: #34D399;">{resultado['importados']}</div>
                                    </div>
                                    <div class="spec-tile">
                                        <div class="spec-tile-label">Ignorados</div>
                                        <div class="spec-tile-val mono">{resultado['erros']}</div>
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
            "CODIGO_POSTE": ["P-001", "P-002", "P-003"],
            "LOGRADOURO": ["Rua Manoel Cirilo", "Travessa São Pedro", "Av. Rio Branco"],
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
                    <span class="panel-title">Colunas Reconhecidas</span>
                    <span class="panel-meta">Auto-Detect</span>
                </div>
                <table class="clean-table">
                    <thead>
                        <tr>
                            <th>Campo</th>
                            <th>Cabeçalhos Aceitos</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Código</strong> <span style="color: #FB7185;">*</span></td>
                            <td class="mono" style="font-size: 0.76rem; color: #94A3B8;">CODIGO, POSTE, PLAQUETA, ID</td>
                        </tr>
                        <tr>
                            <td><strong>Localização</strong></td>
                            <td class="mono" style="font-size: 0.76rem; color: #94A3B8;">LOGRADOURO, RUA, BAIRRO, REF</td>
                        </tr>
                        <tr>
                            <td><strong>Luminária</strong></td>
                            <td class="mono" style="font-size: 0.76rem; color: #94A3B8;">TIPO_LUMINARIA, POTENCIA</td>
                        </tr>
                        <tr>
                            <td><strong>Estrutura</strong></td>
                            <td class="mono" style="font-size: 0.76rem; color: #94A3B8;">TIPO_POSTE, TIPO_BRACO</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            label="Baixar Planilha Modelo (.xlsx)",
            data=buffer,
            file_name="modelo_postes_boasaude.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
