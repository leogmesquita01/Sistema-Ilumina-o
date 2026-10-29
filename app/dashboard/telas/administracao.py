"""Tela "Administração": só aparece para quem tem papel admin.

A tela é a porta; a fechadura é o banco (migração 005). Mesmo assim ela confere o
papel de novo aqui, para ninguém cair nela mexendo no ``session_state``.
"""
import pandas as pd
import streamlit as st

from app.constantes import OS_ABERTA
from app.dashboard.sessao import usuario_atual
from app.dashboard.ui import html, painel, painel_topo, tela, topo, vazio
from app.database.conexao import modo_local
from app.erros import NadaGravado, mensagem_para_usuario
from app.fuso import agora_local, para_local
from app.servicos import admin_service as adm
from app.servicos.dados_postes import PosteDuplicado
from app.servicos.ordens_service import listar_ordens

_AVISO = "admin_aviso"


def eh_admin(usuario) -> bool:
    return bool(usuario) and usuario.get("papel") == "admin"


def _executar(acao, sucesso: str) -> None:
    """Roda a ação; em caso de sucesso guarda o aviso e recarrega a tela."""
    try:
        acao()
    except (adm.AcaoRecusada, PosteDuplicado, NadaGravado) as erro:
        st.warning(str(erro))
        return
    except Exception as erro:  # erro do banco (permissão, gatilho, rede)
        st.error(mensagem_para_usuario(erro, modo_local()).texto)
        return
    st.session_state[_AVISO] = sucesso
    st.rerun()


def _data(valor) -> str:
    dt = para_local(valor)
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"


# ---- Equipe ------------------------------------------------------------------

def _aba_equipe() -> None:
    if modo_local():
        html(vazio("Equipe só com o Supabase", "No modo local não há login: todo mundo entra como administrador."))
        return

    membros = adm.listar_equipe()
    pendentes = [m for m in membros if not m.get("liberado")]
    liberados = [m for m in membros if m.get("liberado")]

    with painel("admin-equipe"):
        painel_topo("Quem tem acesso", f"{len(liberados)} conta(s)")
        if liberados:
            st.dataframe(
                pd.DataFrame([{
                    "Nome": m.get("nome") or "—",
                    "E-mail": m.get("email"),
                    "Papel": adm.PAPEIS.get(m.get("papel"), m.get("papel")),
                    "Ativo": "Sim" if m.get("ativo") else "Não",
                    "Último acesso": _data(m.get("ultimo_acesso")),
                } for m in liberados]),
                hide_index=True, use_container_width=True,
            )

            por_id = {m["id"]: m for m in liberados}
            # Fora do formulário: trocar a pessoa recarrega os campos com os dados dela.
            escolhido = st.selectbox(
                "Editar", list(por_id),
                format_func=lambda i: f"{por_id[i].get('nome') or '—'} · {por_id[i].get('email')}",
            )
            m = por_id[escolhido]
            with st.form(f"form_editar_membro_{escolhido}", border=False):
                c1, c2, c3 = st.columns([2, 1.3, 1], vertical_alignment="bottom")
                nome = c1.text_input("Nome", value=m.get("nome") or "")
                papel = c2.selectbox("Papel", list(adm.PAPEIS), format_func=adm.PAPEIS.get,
                                     index=list(adm.PAPEIS).index(m.get("papel") or "operador"))
                ativo = c3.checkbox("Ativo", value=bool(m.get("ativo")))
                if st.form_submit_button("Salvar alterações", type="primary"):
                    _executar(lambda: adm.atualizar_membro(escolhido, nome, papel, ativo),
                              f"Usuário {nome or m.get('email')} atualizado.")
            st.caption("O papel novo vale no próximo login da pessoa; o banco já aplica na hora. "
                       "Desativar corta o acesso sem apagar o histórico dela.")

    with painel("admin-pendentes"):
        painel_topo("Contas aguardando liberação", f"{len(pendentes)}")
        if not pendentes:
            html(vazio("Nenhuma conta esperando",
                       "Para chamar alguém: Supabase → Authentication → Add user. A conta aparece aqui para liberar."))
        else:
            por_id = {m["id"]: m for m in pendentes}
            with st.form("form_liberar", border=False):
                escolhido = st.selectbox("Conta", list(por_id), format_func=lambda i: por_id[i].get("email"))
                c1, c2 = st.columns([2, 1.3], vertical_alignment="bottom")
                nome = c1.text_input("Nome de quem vai usar")
                papel = c2.selectbox("Papel", list(adm.PAPEIS), format_func=adm.PAPEIS.get, key="papel_liberar")
                if st.form_submit_button("Liberar acesso", type="primary"):
                    _executar(lambda: adm.liberar_usuario(escolhido, nome, papel),
                              f"Acesso liberado para {por_id[escolhido].get('email')}.")


# ---- Ações sensíveis ---------------------------------------------------------

def _aba_acoes() -> None:
    col_poste, col_os = st.columns(2, gap="medium")

    with col_poste:
        with painel("admin-renomear"):
            painel_topo("Renomear código do poste", "O.S. acompanham")
            with st.form("form_renomear", border=False, clear_on_submit=True):
                atual = st.text_input("Código atual", placeholder="P-001")
                novo = st.text_input("Novo código", placeholder="P-0001")
                if st.form_submit_button("Renomear", type="primary"):
                    _executar(lambda: adm.renomear_poste(atual, novo), f"Poste {atual.strip()} agora é {novo.strip()}.")

        with painel("admin-excluir-poste"):
            painel_topo("Excluir poste", "só sem O.S.")
            with st.form("form_excluir_poste", border=False, clear_on_submit=True):
                codigo = st.text_input("Código do poste")
                certeza = st.checkbox("Confirmo: o poste sai da base de vez")
                if st.form_submit_button("Excluir poste"):
                    if not certeza:
                        st.warning("Marque a confirmação para excluir.")
                    else:
                        _executar(lambda: adm.excluir_poste(codigo), f"Poste {codigo.strip()} excluído.")

    with col_os:
        with painel("admin-os"):
            painel_topo("Ordem de serviço", "cancelar · corrigir · excluir")
            ordens = listar_ordens("Todos")
            if not ordens:
                html(vazio("Nenhuma O.S.", "Ainda não há ordens de serviço."))
                return
            por_protocolo = {o["protocolo"]: o for o in ordens}
            protocolo = st.selectbox(
                "O.S.", list(por_protocolo),
                format_func=lambda p: f"{p} · poste {por_protocolo[p]['codigo_poste']} · {por_protocolo[p].get('status')}",
            )
            acao = st.radio("O que fazer", ["Cancelar", "Corrigir protocolo", "Excluir"], horizontal=True)

            with st.form("form_os", border=False, clear_on_submit=True):
                if acao == "Cancelar":
                    if por_protocolo[protocolo].get("status") != OS_ABERTA:
                        st.caption("Só O.S. aberta pode ser cancelada.")
                    motivo = st.text_input("Motivo", placeholder="Aberta em duplicidade, poste errado…")
                    if st.form_submit_button("Cancelar O.S.", type="primary"):
                        _executar(lambda: adm.cancelar_ordem(protocolo, motivo), f"O.S. {protocolo} cancelada.")
                elif acao == "Corrigir protocolo":
                    novo = st.text_input("Protocolo correto", placeholder="OS-2026-0001")
                    if st.form_submit_button("Corrigir", type="primary"):
                        _executar(lambda: adm.corrigir_protocolo(protocolo, novo), f"Protocolo corrigido para {novo.strip()}.")
                else:
                    st.caption("Excluir apaga a O.S. de vez (lançamento errado). Para desistência, use Cancelar.")
                    certeza = st.checkbox("Confirmo a exclusão definitiva")
                    if st.form_submit_button("Excluir O.S."):
                        if not certeza:
                            st.warning("Marque a confirmação para excluir.")
                        else:
                            _executar(lambda: adm.excluir_ordem(protocolo), f"O.S. {protocolo} excluída.")


# ---- Histórico ---------------------------------------------------------------

def _aba_historico() -> None:
    if modo_local():
        html(vazio("Histórico só com o Supabase", "Os registros são gravados pelo banco (migração 005)."))
        return
    with painel("admin-historico"):
        filtros = {"Tudo": None, **{v: k for k, v in adm.TABELAS_HISTORICO.items()}}
        c1, c2 = st.columns([2, 1])
        escolha = c1.segmented_control("Mostrar", list(filtros), default="Tudo", key="hist_filtro")
        limite = c2.selectbox("Quantos", [50, 200, 1000], index=1)
        linhas = adm.listar_historico(limite=limite, tabela=filtros.get(escolha or "Tudo"))
        painel_topo("Últimas ações", f"{len(linhas)} registro(s)")
        if not linhas:
            html(vazio("Nada registrado ainda", "As ações aparecem aqui depois de aplicar a migração 005."))
        else:
            st.dataframe(pd.DataFrame(linhas), hide_index=True, use_container_width=True)


# ---- Backup ------------------------------------------------------------------

def _aba_backup() -> None:
    with painel("admin-backup"):
        painel_topo("Backup em planilha", "postes + O.S.")
        st.caption("Gera um Excel com todos os postes e todas as ordens de serviço, uma aba cada. "
                   "Guarde fora do computador (pendrive, Drive).")
        if st.button("Gerar planilha", type="primary"):
            try:
                st.session_state["admin_backup"] = adm.gerar_backup_xlsx()
            except Exception as erro:
                st.error(mensagem_para_usuario(erro, modo_local()).texto)
        dados = st.session_state.get("admin_backup")
        if dados:
            st.download_button(
                "Baixar backup (.xlsx)", data=dados,
                file_name=f"ilumina-backup-{agora_local():%Y-%m-%d-%H%M}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


def _aba_protegida(desenhar) -> None:
    """Erro numa aba (ex.: migração 005 ainda não aplicada) não derruba as outras."""
    try:
        desenhar()
    except Exception as erro:
        if "PGRST202" in str(erro) or "42P01" in str(erro) or "PGRST205" in str(erro):
            st.warning("Esta parte precisa da migração supabase/migrations/005_area_admin.sql aplicada no banco.")
            return
        mensagem = mensagem_para_usuario(erro, modo_local())
        if mensagem.sessao_expirada:
            raise
        st.error(mensagem.texto)


def renderizar_tela_administracao():
    with tela("admin"):
        if not eh_admin(usuario_atual()):
            st.error("Esta área é só do administrador.")
            return

        topo("Só para o administrador", "Administração",
             "Equipe, correções que o operador não pode fazer, histórico de quem fez o quê e backup.",
             meta="acesso restrito")

        aviso = st.session_state.pop(_AVISO, None)
        if aviso:
            st.success(aviso)

        equipe, acoes, historico, backup = st.tabs(["Equipe", "Ações sensíveis", "Histórico", "Backup"])
        for aba, desenhar in ((equipe, _aba_equipe), (acoes, _aba_acoes),
                              (historico, _aba_historico), (backup, _aba_backup)):
            with aba:
                _aba_protegida(desenhar)
