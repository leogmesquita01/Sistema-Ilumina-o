import folium
import streamlit as st
from streamlit_folium import st_folium

from app.constantes import BRACOS, CENTRO_MUNICIPIO, ESTRUTURAS, LUMINARIAS, URL_SATELITE
from app.dashboard.html_seguro import esc
from app.database.conexao import modo_local
from app.erros import mensagem_para_usuario
from app.dashboard.ui import html, painel, painel_topo, tela, topo
from app.servicos.dados_postes import cadastrar_poste, codigo_duplicado, listar_postes, localizacao_pendente

_ZOOM_CADASTRO = 15


def _mapa_escolha_localizacao():
    """Mapa clicável do cadastro. Devolve o ponto escolhido ou ``None``.

    A marcação é opcional: quem não quiser (ou não souber) clicar segue com o
    cadastro normal, e o poste entra na fila de "Localização pendente".
    """
    ponto = st.session_state.get("cad_ponto")
    centro = [ponto["lat"], ponto["lng"]] if ponto else list(CENTRO_MUNICIPIO)

    mapa = folium.Map(location=centro, zoom_start=_ZOOM_CADASTRO, tiles=None, control_scale=True)
    folium.TileLayer(tiles=URL_SATELITE, attr="Esri World Imagery", name="Satélite", show=True).add_to(mapa)
    folium.TileLayer(tiles="OpenStreetMap", name="Ruas", show=False).add_to(mapa)
    folium.LayerControl(position="topright", collapsed=True).add_to(mapa)

    if ponto:
        folium.Marker(
            [ponto["lat"], ponto["lng"]],
            tooltip="Poste marcado",
            icon=folium.Icon(color="orange", icon="ok-sign", prefix="fa"),
        ).add_to(mapa)

    resultado = st_folium(
        mapa,
        key="mapa_cadastro",
        height=400,
        use_container_width=True,
        returned_objects=["last_clicked"],
    )

    clique = (resultado or {}).get("last_clicked") if isinstance(resultado, dict) else None
    if clique:
        marca = (round(float(clique["lat"]), 7), round(float(clique["lng"]), 7))
        if st.session_state.get("cad_ultimo_clique") != marca:
            st.session_state["cad_ultimo_clique"] = marca
            st.session_state["cad_ponto"] = {"lat": marca[0], "lng": marca[1]}
            st.rerun()

    return st.session_state.get("cad_ponto")


def _rodape_localizacao(ponto) -> None:
    if not ponto:
        html(
            '<div class="il-painel-rodape"><span class="il-status pendente">Sem marcação</span>'
            "<span>O poste será salvo como localização pendente e não aparece no mapa até ser localizado.</span></div>"
        )
        return
    html(
        '<div class="il-painel-rodape"><span class="il-status normal">Ponto marcado</span>'
        f'<span class="mono">{ponto["lat"]:.6f}, {ponto["lng"]:.6f}</span></div>'
    )
    if st.button("Remover marcação", key="cad_limpar_ponto", type="tertiary"):
        st.session_state.pop("cad_ponto", None)
        st.session_state.pop("cad_ultimo_clique", None)
        st.rerun()


def _ultimos(todos_postes: list) -> None:
    painel_topo("Últimos cadastrados", f"{len(todos_postes)} no total")
    if not todos_postes:
        html('<div class="il-nota">Nenhum poste cadastrado ainda.</div>')
        return
    linhas = "".join(
        "<tr>"
        f'<td class="mono">{esc(p["codigo"])}</td>'
        f'<td>{esc(p.get("logradouro"))} · {esc(p.get("bairro"))}</td>'
        + ('<td><span class="il-status pendente">Sem localização</span></td>' if localizacao_pendente(p)
           else '<td><span class="il-status normal">Localizado</span></td>') +
        "</tr>"
        for p in todos_postes[:5]  # a lista vem do mais novo para o mais antigo
    )
    html(f'<div class="il-sem-margem il-tabela-box"><table class="il-tabela"><tbody>{linhas}</tbody></table></div>')


def renderizar_tela_cadastrar():
    with tela("cadastro"):
        todos_postes = listar_postes()
        topo(
            "Inventário",
            "Cadastrar poste",
            "Preencha a ficha e, se puder, marque o ponto no mapa de satélite. Sem marcação, o poste fica como localização pendente.",
            meta=f"{len(todos_postes)} postes na base",
        )

        aviso = st.session_state.pop("cad_aviso", None)
        if aviso:
            situacao = "com localização" if aviso["tem_localizacao"] else "com localização pendente"
            st.success(f"Poste {aviso['codigo']} gravado {situacao} — {aviso['logradouro']}, {aviso['bairro']}.")

        col_form, col_mapa = st.columns([1.15, 1], gap="medium")

        with col_form:
            with painel("cadastro-form"):
                painel_topo("Ficha do poste")
                with st.form("form_cadastrar_poste", border=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        codigo = st.text_input("Código da plaqueta", placeholder="Exatamente como na plaqueta")
                        logradouro = st.text_input("Rua / logradouro", placeholder="Ex.: Rua Manoel Cirilo")
                    with c2:
                        bairro = st.text_input("Bairro ou comunidade", value="Centro")
                        referencia = st.text_input("Ponto de referência", placeholder="Ex.: em frente à UBS")

                    html('<div class="il-subsecao">Luminária e estrutura</div>')
                    c3, c4 = st.columns(2)
                    with c3:
                        luminaria = st.selectbox("Tipo de luminária", LUMINARIAS)
                        tipo_poste = st.selectbox("Tipo de estrutura", ESTRUTURAS)
                    with c4:
                        potencia = st.number_input("Potência (W)", value=100, step=10, min_value=1)
                        tipo_braco = st.selectbox("Tipo de braço", BRACOS)

                    observacoes = st.text_area(
                        "Observações técnicas",
                        placeholder="Condição do relé, transformador próximo, estado da fiação…",
                    )
                    salvar = st.form_submit_button("Registrar poste", type="primary", use_container_width=True)

        with col_mapa:
            with painel("cadastro-mapa"):
                painel_topo("Onde está o poste?", "clique no satélite")
                ponto = _mapa_escolha_localizacao()
                _rodape_localizacao(ponto)
            with painel("cadastro-ultimos"):
                _ultimos(todos_postes)

        if not salvar:
            return
        if not codigo or not codigo.strip():
            st.error("Informe o código da plaqueta para registrar o poste.")
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
                "latitude": ponto["lat"] if ponto else None,
                "longitude": ponto["lng"] if ponto else None,
            })
        except Exception as e:
            if codigo_duplicado(e):
                existente = getattr(e, "codigo_existente", codigo.strip())
                st.error(f"Já existe um poste com o código {existente}.")
            else:
                st.error(mensagem_para_usuario(e, modo_local=modo_local()).texto)
            return

        st.session_state["cad_aviso"] = {
            "codigo": codigo.strip(),
            "tem_localizacao": bool(ponto),
            "logradouro": logradouro or "Não informado",
            "bairro": bairro or "Centro",
        }
        st.session_state.pop("cad_ponto", None)
        st.session_state.pop("cad_ultimo_clique", None)
        st.rerun()
