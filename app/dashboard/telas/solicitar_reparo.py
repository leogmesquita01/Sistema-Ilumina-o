import streamlit as st

from app.dashboard.html_seguro import esc
from app.dashboard.ui import html, kv, painel, painel_topo, status_html, tela, topo, vazio
from app.servicos.dados_postes import cadastrar_poste, listar_postes, obter_poste_por_codigo
from app.servicos.ordens_service import criar_ordem_servico, gerar_mensagem_whatsapp

NOVO_POSTE = "+ Novo poste não listado"
ESCOLHA = "— Escolha o poste —"

DEFEITOS = [
    "Lâmpada apagada durante a noite",
    "Lâmpada acesa 24 horas (Relé colado)",
    "Lâmpada piscando / instável",
    "Luminária quebrada / vandalismo",
    "Braço de iluminação torto ou caído",
    "Fiação rompida / curto-circuito",
    "Poste sem luminária (Nova instalação)",
    "Outro defeito",
]

PRIORIDADES = ["Normal", "Alta", "Urgente (Posto de Saúde / Centro / Risco)"]


def _escolher_poste(todos_postes: list):
    """Coluna da esquerda: seleção do poste. Devolve (poste, modo_novo_poste)."""
    painel_topo("Poste")
    if not todos_postes:
        html(vazio("Nenhum poste cadastrado", "Preencha a identificação do poste no formulário."))
        return None, True

    opcoes = {f"{p['codigo']} · {p.get('logradouro') or '—'} ({p.get('bairro') or '—'})": p["codigo"] for p in todos_postes}
    lista = [ESCOLHA] + list(opcoes) + [NOVO_POSTE]
    # Poste vindo da ficha do mapa: usado uma vez só (antes ficava preso na sessão).
    pre = st.session_state.pop("poste_selecionado_os", None)
    if pre:
        st.session_state["reparo_poste"] = next((r for r, cod in opcoes.items() if cod == pre), ESCOLHA)
    if st.session_state.get("reparo_poste") not in lista:
        st.session_state["reparo_poste"] = ESCOLHA
    escolha = st.selectbox("Poste para reparo", lista, key="reparo_poste")
    if escolha == ESCOLHA:
        html('<div class="il-nota">Escolha o poste na lista ou cadastre um novo.</div>')
        return None, False
    if escolha == NOVO_POSTE:
        html('<div class="il-nota">O poste será cadastrado junto com a O.S., como localização pendente.</div>')
        return None, True

    poste = obter_poste_por_codigo(opcoes[escolha])
    if poste:
        html(
            '<div class="il-ficha">'
            f'<div class="il-ficha-linha"><span class="il-codigo">{esc(poste["codigo"])}</span>{status_html(poste.get("status"))}</div>'
            "</div>"
        )
        html('<div class="il-sem-margem">' + kv([
            ("Endereço", f"{poste.get('logradouro') or '—'}, {poste.get('bairro') or '—'}"),
            ("Referência", poste.get("referencia") or "—"),
            ("Luminária", f"{poste.get('tipo_luminaria') or '—'} · {poste.get('potencia') or 100} W"),
            ("Braço", poste.get("tipo_braco") or "—"),
        ]) + "</div>")
    return poste, False


def renderizar_tela_solicitar_reparo():
    with tela("reparo"):
        todos_postes = listar_postes()
        topo(
            "Despacho de campo",
            "Solicitar reparo",
            "Emita a ordem de serviço com o kit de peças da viatura e envie para o eletricista pelo WhatsApp.",
            meta=f"{len(todos_postes)} postes na base",
        )

        col_poste, col_form = st.columns([1, 1.7], gap="medium")
        with col_poste:
            with painel("reparo-poste"):
                poste, modo_novo_poste = _escolher_poste(todos_postes)

        with col_form:
            with painel("reparo-form"):
                painel_topo("Ordem de serviço")
                with st.form("form_ordem_servico", border=False):
                    if modo_novo_poste:
                        cp1, cp2, cp3 = st.columns([1, 1.6, 1])
                        with cp1:
                            novo_codigo = st.text_input("Código do poste", placeholder="Ex.: plaqueta")
                        with cp2:
                            novo_logradouro = st.text_input("Rua / logradouro")
                        with cp3:
                            novo_bairro = st.text_input("Bairro / comunidade", value="Centro")

                    col_def, col_prio = st.columns([2, 1])
                    with col_def:
                        defeito = st.selectbox("Defeito constatado", DEFEITOS)
                    with col_prio:
                        prioridade = st.selectbox("Prioridade", PRIORIDADES)

                    html('<div class="il-subsecao">Kit da viatura</div>')
                    potencia_ref = (poste.get("potencia") or 100) if poste else 100
                    c_mat1, c_mat2 = st.columns(2)
                    with c_mat1:
                        usar_lampada = st.checkbox(f"Lâmpada LED {potencia_ref}W", value=True)
                        qtd_lampada = st.number_input("Lâmpadas", min_value=1, max_value=10, value=1)
                        usar_rele = st.checkbox("Relé fotoelétrico 100–240V", value=True)
                        qtd_rele = st.number_input("Relés", min_value=1, max_value=5, value=1)
                        usar_conector = st.checkbox("Conector perfurante dentado", value=True)
                        qtd_conector = st.number_input("Conectores", min_value=1, max_value=10, value=2)
                    with c_mat2:
                        usar_braco = st.checkbox("Braço de iluminação pública 2m", value=False)
                        qtd_braco = st.number_input("Braços", min_value=1, max_value=5, value=1)
                        usar_base = st.checkbox("Base / soquete para relé", value=False)
                        qtd_base = st.number_input("Bases", min_value=1, max_value=5, value=1)
                        usar_fita = st.checkbox("Fita isolante de alta fusão", value=True)
                        qtd_fita = st.number_input("Rolos de fita", min_value=1, max_value=5, value=1)

                    c_orig, c_obs = st.columns([1, 1.5])
                    with c_orig:
                        solicitante = st.text_input("Origem da solicitação", value="Secretaria de Infraestrutura")
                    with c_obs:
                        observacoes = st.text_input(
                            "Instruções para a equipe",
                            placeholder="Ex.: levar escada extensível, poste próximo à esquina…",
                        )

                    submeter = st.form_submit_button("Emitir ordem de serviço", type="primary", use_container_width=True)

        if not submeter:
            return

        if not modo_novo_poste and not poste:
            st.error("Escolha o poste do reparo antes de emitir a ordem de serviço.")
            return

        if modo_novo_poste:
            if not novo_codigo or not novo_codigo.strip():
                st.error("Informe o código ou identificação do poste.")
                return
            existente = obter_poste_por_codigo(novo_codigo.strip())
            if existente:
                # "p-01" digitado quando já existe "P-01": a O.S. vai para o poste que
                # existe, com os dados dele (antes gravava "p-01" e quebrava a FK).
                st.info(f"O poste {existente['codigo']} já estava cadastrado; a O.S. foi aberta nele.")
                poste = existente
            else:
                cod_alvo = novo_codigo.strip()
                log_alvo = novo_logradouro.strip() if novo_logradouro else "Não informado"
                bairro_alvo = novo_bairro.strip() if novo_bairro else "Centro"
                lum_alvo = "LED 100W"
                lat_alvo = lng_alvo = None
                cadastrar_poste({"codigo": cod_alvo, "logradouro": log_alvo, "bairro": bairro_alvo})

        if poste:
            cod_alvo = poste["codigo"]
            log_alvo = poste.get("logradouro") or "Não informado"
            bairro_alvo = poste.get("bairro") or ""
            lum_alvo = f"{poste.get('tipo_luminaria') or 'LED'} {poste.get('potencia') or 100}W"
            lat_alvo, lng_alvo = poste.get("latitude"), poste.get("longitude")

        materiais = []
        for usar, item, qtd in (
            (usar_lampada, f"Lâmpada LED {potencia_ref}W", qtd_lampada),
            (usar_rele, "Relé fotoelétrico 100-240V", qtd_rele),
            (usar_conector, "Conector perfurante dentado", qtd_conector),
            (usar_braco, "Braço de iluminação 2m", qtd_braco),
            (usar_base, "Base / soquete para relé", qtd_base),
            (usar_fita, "Fita isolante alta fusão", qtd_fita),
        ):
            if usar:
                materiais.append({"item": item, "quantidade": qtd})

        protocolo = criar_ordem_servico(
            codigo_poste=cod_alvo,
            defeito=defeito,
            prioridade=prioridade.split()[0],
            materiais=materiais,
            solicitante=solicitante,
            observacoes=observacoes,
        )
        zap_url = gerar_mensagem_whatsapp(
            protocolo=protocolo, codigo_poste=cod_alvo, logradouro=log_alvo, bairro=bairro_alvo,
            defeito=defeito, prioridade=prioridade, luminaria=lum_alvo,
            latitude=lat_alvo, longitude=lng_alvo, materiais=materiais,
        )

        with painel("reparo-ok"):
            html(
                '<div class="il-confirmacao">'
                '<span class="il-kicker">Ordem de serviço emitida</span>'
                f'<span class="il-codigo">{esc(protocolo)}</span>'
                f'<span>Poste <span class="mono">{esc(cod_alvo)}</span> atualizado na base. Envie o despacho para o eletricista:</span>'
                "</div>"
            )
            st.link_button("Enviar despacho no WhatsApp", zap_url, type="primary")
