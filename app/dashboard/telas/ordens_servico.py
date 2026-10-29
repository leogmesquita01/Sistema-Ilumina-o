import streamlit as st

from app.constantes import OS_ABERTA, OS_CANCELADA, OS_CONCLUIDA, PRIORIDADE_URGENTE, STATUS_CHAMADO, STATUS_URGENTE
from app.dashboard.html_seguro import esc
from app.dashboard.ui import html, kpis, painel, status_html, tela, topo, vazio
from app.fuso import para_local
from app.servicos.ordens_service import concluir_ordem_servico, gerar_mensagem_whatsapp, listar_ordens

FILTROS = {"Abertas": OS_ABERTA, "Concluídas": OS_CONCLUIDA, "Canceladas": OS_CANCELADA, "Todas": "Todos"}


def _status_os(os_item: dict) -> str:
    if os_item.get("status") == OS_CANCELADA:
        return '<span class="il-status concluida">Cancelada</span>'
    if os_item.get("status") != OS_ABERTA:
        return '<span class="il-status concluida">Concluída</span>'
    prioridade = os_item.get("prioridade") or "Normal"
    status = STATUS_URGENTE if prioridade == PRIORIDADE_URGENTE else STATUS_CHAMADO
    return status_html(status, texto=f"Aberta · {prioridade}")


def _cartao(os_item: dict) -> None:
    materiais = os_item.get("materiais_lista") or []
    etiquetas = "".join(
        f'<span class="il-etiqueta">{esc(m.get("quantidade", 1))}× {esc(m.get("item"), "")}</span>' for m in materiais
    ) or '<span class="il-etiqueta">Vistoria técnica no local</span>'
    abertura = para_local(os_item.get("data_abertura"))
    data_txt = abertura.strftime("%d/%m/%Y %H:%M") if abertura else "—"

    html(
        '<div class="il-os">'
        '<div class="il-os-linha">'
        f'<span class="il-codigo pequeno">{esc(os_item["protocolo"])}</span>'
        f'<span class="mono">Poste {esc(os_item["codigo_poste"])}</span>'
        f'<span class="il-os-local">{esc(os_item.get("logradouro"))} · {esc(os_item.get("bairro"))}</span>'
        f'<span class="il-os-status">{_status_os(os_item)}</span>'
        "</div>"
        f'<div class="il-os-defeito">{esc(os_item["defeito"])}</div>'
        f"<div>{etiquetas}</div>"
        f'<div class="il-meta">Aberta em {data_txt} · {esc(os_item.get("solicitante"), "—")}</div>'
        "</div>"
    )


def renderizar_tela_ordens_servico():
    with tela("ordens"):
        todas = listar_ordens(filtro_status="Todos")
        abertas = [o for o in todas if o.get("status") == OS_ABERTA]
        urgentes = [o for o in abertas if o.get("prioridade") == PRIORIDADE_URGENTE]
        concluidas = [o for o in todas if o.get("status") == OS_CONCLUIDA]
        validas = [o for o in todas if o.get("status") != OS_CANCELADA]  # cancelada não conta na taxa
        taxa = round(len(concluidas) / len(validas) * 100) if validas else 0

        topo(
            "Manutenção",
            "Ordens de serviço",
            "Chamados abertos, kits de peças da viatura e baixa dos serviços concluídos.",
            meta=f"{len(todas)} no histórico",
        )
        html(kpis([
            ("Abertas", len(abertas), "", "aguardando execução"),
            ("Urgentes", len(urgentes), "urgente" if urgentes else "", "saúde, escolas ou risco"),
            ("Concluídas", len(concluidas), "", f"{taxa}% de resolução"),
        ]))

        f1, f2 = st.columns([1.3, 2], vertical_alignment="bottom", gap="medium")
        with f1:
            escolha = st.segmented_control("Mostrar", list(FILTROS), default="Abertas", key="os_filtro") or "Abertas"
        with f2:
            termo = st.text_input("Buscar", placeholder="Protocolo, poste, rua ou defeito", key="os_busca")

        ordens = listar_ordens(filtro_status=FILTROS[escolha])
        if termo.strip():
            t = termo.strip().lower()
            ordens = [
                o for o in ordens
                if any(t in (o.get(campo) or "").lower() for campo in ("protocolo", "codigo_poste", "logradouro", "defeito"))
            ]

        if not ordens:
            with painel("os-vazio"):
                html(vazio("Nenhuma ordem de serviço encontrada", "Não há registros para este filtro. Abra uma na tela Solicitar reparo."))
            return

        for os_item in ordens:
            with painel(f"os-{os_item['protocolo']}"):
                _cartao(os_item)
                if os_item.get("status") != OS_ABERTA:
                    continue
                zap_url = gerar_mensagem_whatsapp(
                    protocolo=os_item["protocolo"],
                    codigo_poste=os_item["codigo_poste"],
                    logradouro=os_item.get("logradouro") or "",
                    bairro=os_item.get("bairro") or "",
                    defeito=os_item["defeito"],
                    prioridade=os_item.get("prioridade") or "Normal",
                    luminaria=f"{os_item.get('tipo_luminaria') or 'LED'} {os_item.get('potencia') or 100}W",
                    latitude=os_item.get("latitude"),
                    longitude=os_item.get("longitude"),
                    materiais=os_item.get("materiais_lista") or [],
                )
                b1, b2, _ = st.columns([1.2, 1.3, 3])
                with b1:
                    if st.button("Concluir O.S.", key=f"btn_concluir_{os_item['protocolo']}", type="primary", use_container_width=True):
                        concluir_ordem_servico(os_item["protocolo"])
                        st.rerun()
                with b2:
                    st.link_button("Despachar no WhatsApp", zap_url, use_container_width=True)
