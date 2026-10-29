"""Tela inicial: indicadores, mapa da rede, ficha do poste e fila de manutenção."""
import streamlit as st

from app.constantes import (
    OS_ABERTA,
    PRIORIDADE_URGENTE,
    STATUS_CHAMADO,
    STATUS_NORMAL,
    STATUS_URGENTE,
)
from app.dashboard.html_seguro import esc
from app.dashboard.sessao import usuario_atual
from app.dashboard.telas.componentes_mapa import CAMADAS, renderizar_mapa_folium
from app.dashboard.ui import (
    esqueleto,
    html,
    ir_para,
    kpis,
    kv,
    painel,
    painel_topo,
    status_html,
    tela,
    topo,
    vazio,
)
from app.fuso import agora_local, para_local
from app.servicos.dados_postes import (
    COORDENADA_PADRAO,
    listar_postes,
    localizacao_pendente,
    obter_poste_por_codigo,
    obter_resumo_indicadores,
)
from app.servicos.ordens_service import link_rota, listar_ordens

FILTROS_STATUS = {
    "Todos": "Todos",
    "Operacional": STATUS_NORMAL,
    "Chamado aberto": STATUS_CHAMADO,
    "Urgente": STATUS_URGENTE,
}


def _numero(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def _ha_quanto_tempo(data) -> str:
    inicio = para_local(data)
    if not inicio:
        return "—"
    dias = (agora_local().date() - inicio.date()).days
    return "hoje" if dias <= 0 else f"{dias} d"


def _rotulo_poste(p: dict) -> str:
    return f"{p['codigo']} · {p.get('logradouro') or '—'} ({p.get('bairro') or '—'})"


def _faixa_superior(stats: dict, pendentes: int) -> None:
    col_kpis, col_acoes = st.columns([4.2, 1.6], vertical_alignment="bottom", gap="medium")
    with col_kpis:
        html(kpis([
            ("Postes cadastrados", _numero(stats["total_postes"]), "", ""),
            ("Luminárias LED", f"{int(round(stats['taxa_led']))}%", "", ""),
            ("O.S. abertas", stats["os_abertas"], "", ""),
            ("Em alerta", stats["total_chamados"], "urgente" if stats["total_chamados"] else "", ""),
            ("Sem localização", _numero(pendentes), "", ""),
        ]))
    with col_acoes:
        b1, b2 = st.columns(2, gap="small")
        with b1:
            if st.button("Importar planilha", key="mapa_ir_importar", use_container_width=True):
                ir_para("importar")
        with b2:
            if st.button("Nova O.S.", key="mapa_ir_reparo", type="primary", use_container_width=True):
                ir_para("reparo")


def _ficha(poste: dict | None) -> None:
    if not poste:
        html(vazio("Nenhum poste selecionado", "Escolha um poste na lista acima ou busque pelo código."))
        return

    completo = obter_poste_por_codigo(poste["codigo"]) or poste
    pendente = localizacao_pendente(completo)
    abertas = [o for o in completo.get("historico_os", []) if o.get("status") == OS_ABERTA]
    if abertas:
        os_ = abertas[0]
        linha_os = f"O.S. {esc(os_.get('protocolo'))} aberta há {_ha_quanto_tempo(os_.get('data_abertura'))} · {esc(os_.get('defeito'))}"
    else:
        linha_os = "Nenhuma ordem de serviço aberta"

    html(
        '<div class="il-ficha">'
        f'<div class="il-ficha-linha"><span class="il-codigo">{esc(completo["codigo"])}</span>{status_html(completo.get("status"))}</div>'
        f'<div class="il-ficha-os">{linha_os}</div></div>'
    )
    coordenada = "Localização pendente" if pendente else f"{float(completo['latitude']):.6f}, {float(completo['longitude']):.6f}"
    html('<div class="il-sem-margem">' + kv([
        ("Endereço", f"{completo.get('logradouro') or '—'}, {completo.get('bairro') or '—'}"),
        ("Referência", completo.get("referencia") or "—"),
        ("Luminária", f"{completo.get('tipo_luminaria') or '—'} · {completo.get('potencia') or 100} W"),
        ("Estrutura", f"{completo.get('tipo_poste') or '—'} · {completo.get('tipo_braco') or '—'}"),
        ("Coordenada", coordenada),
    ], mono=("Coordenada",)) + "</div>")
    if completo.get("observacoes"):
        html(f'<div class="il-nota">{esc(completo["observacoes"])}</div>')

    b1, b2 = st.columns(2, gap="small")
    with b1:
        if st.button("Solicitar reparo", key="ficha_reparo", type="primary", use_container_width=True):
            st.session_state["poste_selecionado_os"] = completo["codigo"]
            ir_para("reparo")
    with b2:
        st.link_button(
            "Rota no Maps",
            link_rota(completo.get("latitude"), completo.get("longitude"),
                      completo.get("logradouro") or "", completo.get("bairro") or ""),
            use_container_width=True,
        )


def _fila() -> None:
    abertas = listar_ordens(filtro_status=OS_ABERTA)
    abertas = sorted(abertas, key=lambda o: (o.get("prioridade") != PRIORIDADE_URGENTE, o.get("id") or 0))
    painel_topo("Fila de manutenção", f"{len(abertas)} aberta(s)")
    if not abertas:
        html(vazio("Fila vazia", "Nenhuma ordem de serviço aberta no momento."))
        return

    linhas = []
    for o in abertas[:6]:
        status = STATUS_URGENTE if o.get("prioridade") == PRIORIDADE_URGENTE else STATUS_CHAMADO
        prioridade = o.get("prioridade") or "Normal"
        linhas.append(
            "<tr>"
            f'<td>{status_html(status, texto=prioridade)}</td>'
            f'<td class="mono">{esc(o.get("codigo_poste"))}</td>'
            f'<td>{esc(o.get("logradouro"))} · {esc(o.get("bairro"))}</td>'
            f'<td class="num">{_ha_quanto_tempo(o.get("data_abertura"))}</td>'
            "</tr>"
        )
    html(
        '<div class="il-sem-margem il-tabela-box"><table class="il-tabela">'
        '<thead><tr><th scope="col">Prioridade</th><th scope="col">Poste</th><th scope="col">Local</th>'
        '<th scope="col" class="num">Aberta</th></tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody></table></div>'
    )
    if len(abertas) > 6:
        if st.button(f"Ver as {len(abertas)} ordens", key="fila_ver_todas", type="tertiary"):
            ir_para("ordens")


def renderizar_tela_mapa() -> None:
    with tela("mapa"):
        agora = agora_local()
        saudacao = "Bom dia" if agora.hour < 12 else ("Boa tarde" if agora.hour < 18 else "Boa noite")
        primeiro_nome = (usuario_atual()["nome"] or "").split(" ")[0]

        carregando = st.empty()
        carregando.markdown(esqueleto(linhas=2), unsafe_allow_html=True)
        stats = obter_resumo_indicadores()
        todos = listar_postes()
        pendentes = sum(1 for p in todos if localizacao_pendente(p))
        carregando.empty()

        if stats["total_chamados"]:
            subtitulo = f"{stats['total_chamados']} ponto(s) aguardam manutenção · {stats['os_abertas']} O.S. na fila."
        else:
            subtitulo = "Nenhum ponto aguardando manutenção."
        topo("Painel da rede", f"{saudacao}, {primeiro_nome}", subtitulo, meta=f"Sincronizado às {agora:%H:%M}")

        _faixa_superior(stats, pendentes)

        if pendentes:
            c_aviso, c_botao = st.columns([5, 1.2], vertical_alignment="center", gap="small")
            with c_aviso:
                html(
                    f'<div class="il-aviso"><span class="il-status pendente">Localização pendente</span>'
                    f'<span><strong>{_numero(pendentes)}</strong> poste(s) sem coordenada confiável não aparecem no mapa.</span></div>'
                )
            with c_botao:
                if st.button("Localizar postes", key="mapa_ir_localizar", use_container_width=True):
                    ir_para("localizar")

        col_mapa, col_lado = st.columns([3, 2], gap="medium")

        with col_mapa:
            with painel("mapa"):
                painel_topo("Mapa da rede", f"{_numero(len(todos) - pendentes)} no mapa")
                f1, f2, f3 = st.columns([2.1, 1.3, 1.8], vertical_alignment="bottom", gap="small")
                with f1:
                    busca = st.text_input("Buscar", placeholder="Código, rua ou bairro", key="mapa_busca")
                with f2:
                    filtro = FILTROS_STATUS[st.selectbox("Situação", list(FILTROS_STATUS), key="mapa_status")]
                with f3:
                    camada = st.segmented_control("Camada", list(CAMADAS), default="Ruas", key="mapa_camada") or "Ruas"

                postes = listar_postes(filtro_status=filtro, termo_busca=busca)
                foco = None
                if busca.strip():
                    exatos = [p for p in postes if str(p["codigo"]).lower() == busca.strip().lower()]
                    foco = exatos[0] if exatos else (postes[0] if postes else None)
                st.session_state["mapa_foco"] = foco["codigo"] if foco else st.session_state.get("mapa_foco")

                localizavel = foco is not None and not localizacao_pendente(foco)
                centro = [foco["latitude"], foco["longitude"]] if localizavel else list(COORDENADA_PADRAO)
                renderizar_mapa_folium(postes, centro, 18 if localizavel else 15, camada)
                html(
                    '<div class="il-painel-rodape"><div class="il-legenda">'
                    '<span class="il-status normal">Operacional</span>'
                    '<span class="il-status chamado">Chamado aberto</span>'
                    '<span class="il-status urgente">Urgente</span></div>'
                    f'<span>{len(postes)} poste(s) no filtro atual</span></div>'
                )

        with col_lado:
            with painel("ficha"):
                painel_topo("Poste selecionado")
                opcoes = {_rotulo_poste(p): p for p in postes}
                rotulos = ["—"] + list(opcoes)
                # Com `key`, o Streamlit ignora `index` depois do 1º uso: a seleção
                # precisa ser escrita no estado do widget quando a busca acha outro poste.
                if foco is not None and st.session_state.get("mapa_foco_aplicado") != foco["codigo"]:
                    st.session_state["mapa_foco_aplicado"] = foco["codigo"]
                    st.session_state["mapa_inspecao"] = _rotulo_poste(foco)
                if st.session_state.get("mapa_inspecao") not in rotulos:
                    st.session_state["mapa_inspecao"] = "—"
                escolha = st.selectbox("Inspecionar poste", rotulos, key="mapa_inspecao")
                _ficha(opcoes.get(escolha))

            with painel("fila"):
                _fila()

        if not todos:
            html(vazio("Comece a alimentar a base", "Cadastre um poste ou importe a planilha (inclusive a exportação do Kobo)."))
