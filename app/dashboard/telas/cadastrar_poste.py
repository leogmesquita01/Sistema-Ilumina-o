import folium
import streamlit as st
from streamlit_folium import st_folium

from app.servicos.dados_postes import COORDENADA_PADRAO, cadastrar_poste, listar_postes

_URL_ESRI = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)
_ZOOM_CADASTRO = 15


def _mapa_escolha_localizacao():
    """Mapa clicável do cadastro. Devolve o ponto escolhido ou ``None``.

    A marcação é opcional: quem não quiser (ou não souber) clicar segue com o
    cadastro normal, e o poste entra na fila de "Localização pendente".
    """
    ponto = st.session_state.get("cad_ponto")
    centro = [ponto["lat"], ponto["lng"]] if ponto else list(COORDENADA_PADRAO)

    mapa = folium.Map(location=centro, zoom_start=_ZOOM_CADASTRO, tiles=None, control_scale=True)
    folium.TileLayer(tiles=_URL_ESRI, attr="Esri World Imagery", name="Satélite (Esri)", show=True).add_to(mapa)
    folium.TileLayer(tiles="OpenStreetMap", name="Mapa de ruas", show=False).add_to(mapa)
    folium.LayerControl(position="topright", collapsed=True).add_to(mapa)

    if ponto:
        folium.Marker(
            [ponto["lat"], ponto["lng"]],
            tooltip="Poste marcado",
            icon=folium.Icon(color="green", icon="ok-sign", prefix="fa"),
        ).add_to(mapa)

    resultado = st_folium(
        mapa,
        key="mapa_cadastro",
        height=390,
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


def _painel_localizacao(ponto) -> None:
    if not ponto:
        st.markdown(
            '<div class="panel-card" style="padding: 12px 16px; margin-top: 10px; border-style: dashed;">'
            '<div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.45;">'
            '<strong style="color: #FBBF24;">Sem marcação</strong> — o poste será salvo como '
            '<strong style="color: #F8FAFC;">localização pendente</strong> e não aparecerá no mapa '
            'até ser localizado na tela "Localizar".'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="panel-card" style="padding: 12px 16px; margin-top: 10px; border-color: rgba(16, 185, 129, 0.4);">'
        '<div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">'
        '<div>'
        '<div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: #34D399; font-weight: 700;">Ponto marcado</div>'
        f'<div class="mono" style="font-size: 0.85rem; color: #FFFFFF; font-weight: 700;">{ponto["lat"]:.6f}, {ponto["lng"]:.6f}</div>'
        '</div>'
        '<span class="status-pill positive">● Será gravado</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("Remover marcação", use_container_width=True, key="cad_limpar_ponto"):
        st.session_state.pop("cad_ponto", None)
        st.session_state.pop("cad_ultimo_clique", None)
        st.rerun()


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
                <p class="hero-subtitle">Preencha a ficha e, se puder, marque o ponto no mapa ao lado. Sem marcação o poste é salvo como localização pendente.</p>
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

    aviso = st.session_state.pop("cad_aviso", None)
    if aviso:
        pill_loc = (
            '<span class="status-pill positive">Localização gravada</span>'
            if aviso["tem_localizacao"]
            else '<span class="status-pill warning">Localização pendente</span>'
        )
        st.markdown(
            '<div class="panel-card" style="border-color: #10B981; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">'
            '<div>'
            '<span class="status-pill positive">Ativo Registrado</span>'
            f'<span style="font-size: 0.9rem; color: #FFFFFF; margin-left: 10px;">Poste '
            f'<span class="mono" style="font-weight: 700; color: #34D399;">{aviso["codigo"]}</span> gravado.</span>'
            '</div>'
            '<div style="display: flex; gap: 8px; align-items: center;">'
            f'{pill_loc}'
            f'<span style="font-size: 0.82rem; color: #94A3B8;">{aviso["logradouro"]} · {aviso["bairro"]}</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    col_form, col_mapa = st.columns([1.15, 1], gap="medium")

    with col_form:
        with st.form("form_cadastrar_poste"):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span class="status-pill positive">Identificação</span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Endereço e Referência</span>
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

    with col_mapa:
        st.markdown(
            '<div style="display: flex; justify-content: space-between; align-items: center; background: #0F1724; border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 11px 16px; margin-bottom: 10px;">'
            '<span style="font-size: 0.82rem; font-weight: 700; color: #F8FAFC;">Onde está o poste?</span>'
            '<span style="font-size: 0.72rem; color: #94A3B8;">Clique no satélite</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        ponto = _mapa_escolha_localizacao()
        _painel_localizacao(ponto)

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
                "latitude": ponto["lat"] if ponto else None,
                "longitude": ponto["lng"] if ponto else None,
            })
        except Exception as e:
            if "duplicate" in str(e).lower():
                st.error(f"Já existe um poste com o código {codigo.strip()}. Use outro código ou edite o existente.")
            else:
                st.error(f"Erro ao cadastrar poste: {str(e)}")
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
