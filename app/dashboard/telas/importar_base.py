import io

import pandas as pd
import streamlit as st

from app.dashboard.html_seguro import esc
from app.dashboard.ui import html, kpis, painel, painel_topo, tela, topo
from app.importer import import_poles_file

COLUNAS_ACEITAS = [
    ("Código *", "CODIGO, PLAQUETA, POSTE, BARRAMENTO"),
    ("Coordenadas", "LATITUDE, LONGITUDE ou a coluna de GPS do Kobo"),
    ("Endereço", "LOGRADOURO, RUA, BAIRRO, REFERÊNCIA"),
    ("Luminária", "TIPO_LUMINARIA, POTÊNCIA"),
    ("Estrutura", "TIPO_POSTE, TIPO_BRACO"),
    ("Observações", "OBSERVAÇÕES, OBS"),
]


def _planilha_modelo() -> bytes:
    exemplo = pd.DataFrame({
        "CODIGO_POSTE": ["P-001", "P-002", "P-003"],
        "LOGRADOURO": ["Rua Manoel Cirilo", "Travessa São Pedro", "Av. Rio Branco"],
        "BAIRRO": ["Centro", "Centro", "Bela Vista"],
        "REFERENCIA": ["Ao lado do colégio", "Próximo à praça", "Em frente ao posto"],
        "TIPO_LUMINARIA": ["LED", "Vapor de Sódio", "LED"],
        "POTENCIA_WATTS": [100, 70, 150],
        "TIPO_POSTE": ["Concreto Duplo T", "Concreto Circular", "Concreto Duplo T"],
        "TIPO_BRACO": ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m"],
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        exemplo.to_excel(writer, index=False, sheet_name="Postes")
    return buffer.getvalue()


def _resultado(resultado: dict) -> None:
    html(kpis([
        ("Linhas lidas", resultado["total_linhas"], "", ""),
        ("Salvos / atualizados", resultado["importados"], "", ""),
        ("Ignorados", resultado["erros"], "", "sem código"),
    ]))
    colunas = resultado.get("colunas_identificadas", {})
    st.caption("Colunas usadas: " + ", ".join(f"{campo} ← “{coluna}”" for campo, coluna in colunas.items()))
    if resultado.get("duplicados"):
        st.warning(f"{resultado['duplicados']} código(s) repetido(s) na planilha — valeu a última linha de cada um.")
    if resultado.get("codigos_ajustados"):
        st.info(
            f"{resultado['codigos_ajustados']} código(s) da planilha só mudavam nas maiúsculas/minúsculas "
            "e foram ligados ao poste que já existia (ex.: p-01 → P-01)."
        )
    for aviso in resultado.get("detalhes_erros", []):
        st.caption(f"⚠ {aviso}")
    st.info(
        "Postes que já existiam mantiveram a situação (chamados abertos continuam abertos) e a localização, "
        "a menos que a planilha trouxesse uma coordenada válida."
    )


def renderizar_tela_importar():
    with tela("importar"):
        topo(
            "Importação em lote",
            "Importar planilha",
            "Envie a planilha da equipe ou a exportação do Kobo (Excel ou CSV). Códigos que já existem são atualizados, sem duplicar.",
            meta="upsert por código",
        )

        col_envio, col_ajuda = st.columns([1.6, 1.2], gap="medium")
        with col_envio:
            with painel("importar-envio"):
                painel_topo("Arquivo", ".xlsx · .csv")
                arquivo = st.file_uploader("Selecione a planilha de postes", type=["xlsx", "csv"])
                if arquivo is not None:
                    html(
                        f'<div class="il-nota"><span class="mono">{esc(arquivo.name)}</span> · {arquivo.size / 1024:.1f} KB</div>'
                    )
                    if st.button("Processar e salvar postes", type="primary", use_container_width=True):
                        with st.spinner("Gravando os postes no banco…"):
                            try:
                                resultado = import_poles_file(arquivo.read(), arquivo.name)
                            except Exception as e:
                                st.error(f"Falha ao processar o arquivo: {e}")
                            else:
                                _resultado(resultado)

        with col_ajuda:
            with painel("importar-colunas"):
                painel_topo("Colunas reconhecidas", "automático")
                linhas = "".join(
                    f"<tr><td><strong>{esc(campo)}</strong></td><td class=\"mono\">{esc(aceitas)}</td></tr>"
                    for campo, aceitas in COLUNAS_ACEITAS
                )
                html(f'<div class="il-sem-margem il-tabela-box"><table class="il-tabela"><tbody>{linhas}</tbody></table></div>')
                st.download_button(
                    "Baixar planilha modelo (.xlsx)",
                    data=_planilha_modelo(),
                    file_name="modelo_postes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
