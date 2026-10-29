"""Área do administrador: equipe, ações sensíveis, histórico e backup.

No Supabase, quem garante que só o admin faz isto é o banco (migração 005):
policies, gatilhos e as funções ``listar_equipe``/``liberar_usuario``. A tela
apenas não aparece para o operador.

No modo local não há login nem histórico: equipe e histórico ficam vazios, e as
ações sensíveis valem direto no SQLite.
"""
import io
from typing import Any, Dict, List, Optional

import pandas as pd

from app.cache import limpar_cache
from app.constantes import OS_ABERTA, OS_CANCELADA
from app.database.conexao import modo_local, obter_conexao, obter_supabase
from app.erros import NadaGravado
from app.fuso import para_local
from app.servicos.dados_postes import PosteDuplicado, listar_postes, obter_poste_por_codigo
from app.servicos.ordens_service import _recalcular_status_poste, listar_ordens

PAPEIS = {"operador": "Operador", "admin": "Administrador"}


class AcaoRecusada(ValueError):
    """A ação não pode ser feita como pedida (a mensagem explica por quê)."""


# ---- Equipe ------------------------------------------------------------------

def listar_equipe() -> List[Dict[str, Any]]:
    """Contas do Supabase Auth com o perfil de cada uma (``liberado`` = tem perfil)."""
    if modo_local():
        return []
    return list(obter_supabase().rpc("listar_equipe").execute().data or [])


def atualizar_membro(usuario_id: str, nome: str, papel: str, ativo: bool) -> None:
    if papel not in PAPEIS:
        raise AcaoRecusada(f"Papel inválido: {papel}")
    if modo_local():
        raise AcaoRecusada("No modo local não há equipe: o acesso é feito pelo Supabase.")
    res = (
        obter_supabase()
        .table("perfis")
        .update({"nome": (nome or "").strip(), "papel": papel, "ativo": bool(ativo)})
        .eq("id", usuario_id)
        .execute()
    )
    if not res.data:
        raise NadaGravado("Nada foi alterado: o usuário não foi encontrado ou você não é administrador.")


def liberar_usuario(usuario_id: str, nome: str, papel: str = "operador") -> None:
    """Dá acesso a uma conta criada no Supabase Auth (cria o perfil dela)."""
    if papel not in PAPEIS:
        raise AcaoRecusada(f"Papel inválido: {papel}")
    if modo_local():
        raise AcaoRecusada("No modo local não há equipe: o acesso é feito pelo Supabase.")
    obter_supabase().rpc(
        "liberar_usuario", {"p_id": usuario_id, "p_nome": (nome or "").strip(), "p_papel": papel}
    ).execute()


# ---- Ações sensíveis ---------------------------------------------------------

def _ordem_por_protocolo(protocolo: str) -> Optional[Dict[str, Any]]:
    protocolo = (protocolo or "").strip()
    if not protocolo:
        return None
    if not modo_local():
        res = obter_supabase().table("ordens_servico").select("*").eq("protocolo", protocolo).limit(1).execute()
        return (res.data or [None])[0]
    conn = obter_conexao()
    row = conn.execute("SELECT * FROM ordens_servico WHERE protocolo = ?;", (protocolo,)).fetchone()
    conn.close()
    return dict(row) if row else None


def renomear_poste(codigo_atual: str, codigo_novo: str) -> str:
    """Troca o código do poste. As O.S. dele acompanham (FK com ON UPDATE CASCADE)."""
    poste = obter_poste_por_codigo(codigo_atual)
    if not poste:
        raise AcaoRecusada(f"Poste {codigo_atual} não encontrado.")
    codigo_novo = (codigo_novo or "").strip()
    if not codigo_novo:
        raise AcaoRecusada("Informe o novo código.")
    atual = poste["codigo"]
    if codigo_novo == atual:
        raise AcaoRecusada("O novo código é igual ao atual.")
    outro = obter_poste_por_codigo(codigo_novo)
    if outro and outro["codigo"] != atual:  # "p-01" → "P-01" é só ajuste de caixa
        raise PosteDuplicado(outro["codigo"])

    if not modo_local():
        res = obter_supabase().table("postes").update({"codigo": codigo_novo}).eq("codigo", atual).execute()
        alteradas = len(res.data or [])
    else:
        conn = obter_conexao()
        try:
            alteradas = conn.execute("UPDATE postes SET codigo = ? WHERE codigo = ?;", (codigo_novo, atual)).rowcount
            conn.commit()
        finally:
            conn.close()
    limpar_cache()
    if not alteradas:
        raise NadaGravado(f"Nada foi alterado no poste {atual}.")
    return codigo_novo


def excluir_poste(codigo: str) -> None:
    """Exclui um poste sem O.S. Com histórico de O.S., o banco recusa (ON DELETE RESTRICT)."""
    poste = obter_poste_por_codigo(codigo)
    if not poste:
        raise AcaoRecusada(f"Poste {codigo} não encontrado.")
    if poste.get("historico_os"):
        raise AcaoRecusada(
            f"O poste {poste['codigo']} tem ordens de serviço. Exclua ou mantenha as O.S. antes: "
            "o histórico de manutenção não é apagado junto."
        )
    if not modo_local():
        res = obter_supabase().table("postes").delete().eq("codigo", poste["codigo"]).execute()
        alteradas = len(res.data or [])
    else:
        conn = obter_conexao()
        try:
            alteradas = conn.execute("DELETE FROM postes WHERE codigo = ?;", (poste["codigo"],)).rowcount
            conn.commit()
        finally:
            conn.close()
    limpar_cache()
    if not alteradas:
        raise NadaGravado(f"O poste {poste['codigo']} não foi excluído (sem permissão?).")


def cancelar_ordem(protocolo: str, motivo: str) -> None:
    """Cancela uma O.S. aberta e recalcula a situação do poste."""
    ordem = _ordem_por_protocolo(protocolo)
    if not ordem:
        raise AcaoRecusada(f"O.S. {protocolo} não encontrada.")
    if ordem.get("status") != OS_ABERTA:
        raise AcaoRecusada(f"A O.S. {ordem['protocolo']} não está aberta (situação: {ordem.get('status')}).")
    motivo = (motivo or "").strip()
    if not motivo:
        raise AcaoRecusada("Informe o motivo do cancelamento.")
    obs = ((ordem.get("observacoes") or "").strip() + f"\nCancelada: {motivo}").strip()

    if not modo_local():
        res = (
            obter_supabase().table("ordens_servico")
            .update({"status": OS_CANCELADA, "observacoes": obs})
            .eq("protocolo", ordem["protocolo"]).eq("status", OS_ABERTA)
            .execute()
        )
        alteradas = len(res.data or [])
    else:
        conn = obter_conexao()
        try:
            alteradas = conn.execute(
                "UPDATE ordens_servico SET status = ?, observacoes = ? WHERE protocolo = ? AND status = ?;",
                (OS_CANCELADA, obs, ordem["protocolo"], OS_ABERTA),
            ).rowcount
            conn.commit()
        finally:
            conn.close()
    if not alteradas:
        limpar_cache()
        raise NadaGravado(f"A O.S. {ordem['protocolo']} não foi cancelada (sem permissão ou já baixada).")
    _recalcular_status_poste(ordem["codigo_poste"])
    limpar_cache()


def corrigir_protocolo(protocolo_atual: str, protocolo_novo: str) -> None:
    ordem = _ordem_por_protocolo(protocolo_atual)
    if not ordem:
        raise AcaoRecusada(f"O.S. {protocolo_atual} não encontrada.")
    protocolo_novo = (protocolo_novo or "").strip()
    if not protocolo_novo or protocolo_novo == ordem["protocolo"]:
        raise AcaoRecusada("Informe um protocolo novo, diferente do atual.")
    if _ordem_por_protocolo(protocolo_novo):
        raise AcaoRecusada(f"Já existe uma O.S. com o protocolo {protocolo_novo}.")

    if not modo_local():
        res = (
            obter_supabase().table("ordens_servico")
            .update({"protocolo": protocolo_novo}).eq("protocolo", ordem["protocolo"]).execute()
        )
        alteradas = len(res.data or [])
    else:
        conn = obter_conexao()
        try:
            alteradas = conn.execute(
                "UPDATE ordens_servico SET protocolo = ? WHERE protocolo = ?;", (protocolo_novo, ordem["protocolo"])
            ).rowcount
            conn.commit()
        finally:
            conn.close()
    limpar_cache()
    if not alteradas:
        raise NadaGravado(f"O protocolo {ordem['protocolo']} não foi alterado (sem permissão?).")


def excluir_ordem(protocolo: str) -> None:
    """Apaga a O.S. de vez (para lançamento errado). Para desistência, prefira cancelar."""
    ordem = _ordem_por_protocolo(protocolo)
    if not ordem:
        raise AcaoRecusada(f"O.S. {protocolo} não encontrada.")
    if not modo_local():
        res = obter_supabase().table("ordens_servico").delete().eq("protocolo", ordem["protocolo"]).execute()
        alteradas = len(res.data or [])
    else:
        conn = obter_conexao()
        try:
            alteradas = conn.execute("DELETE FROM ordens_servico WHERE protocolo = ?;", (ordem["protocolo"],)).rowcount
            conn.commit()
        finally:
            conn.close()
    if not alteradas:
        limpar_cache()
        raise NadaGravado(f"A O.S. {ordem['protocolo']} não foi excluída (sem permissão?).")
    _recalcular_status_poste(ordem["codigo_poste"])
    limpar_cache()


# ---- Histórico ---------------------------------------------------------------

_IGNORAR_NO_DIFF = {"data_atualizacao", "id"}
TABELAS_HISTORICO = {"postes": "Poste", "ordens_servico": "O.S.", "perfis": "Usuário"}
ACOES = {"INSERT": "Criou", "UPDATE": "Alterou", "DELETE": "Excluiu"}


def resumir_mudanca(antes: Optional[dict], depois: Optional[dict]) -> str:
    """Texto curto com o que mudou: "status: aberta → cancelada; codigo: P-1 → P-01"."""
    if not antes or not depois:
        return ""
    partes = []
    for campo in depois:
        if campo in _IGNORAR_NO_DIFF:
            continue
        if antes.get(campo) != depois.get(campo):
            partes.append(f"{campo}: {antes.get(campo)!s} → {depois.get(campo)!s}")
    return "; ".join(partes)


def listar_historico(limite: int = 200, tabela: Optional[str] = None) -> List[Dict[str, Any]]:
    """Últimas ações registradas pelos gatilhos da migração 005 (só Supabase)."""
    if modo_local():
        return []
    consulta = obter_supabase().table("historico").select("*").order("id", desc=True).limit(limite)
    if tabela:
        consulta = consulta.eq("tabela", tabela)
    linhas = consulta.execute().data or []

    nomes: Dict[str, str] = {}
    try:
        for m in listar_equipe():
            nomes[str(m.get("id"))] = m.get("nome") or m.get("email") or ""
    except Exception:  # sem a lista da equipe, mostra só o id
        pass

    saida = []
    for r in linhas:
        registro = r.get("registro") or ""
        if r.get("tabela") == "perfis":
            registro = nomes.get(registro, registro)
        quando = para_local(r.get("em"))
        saida.append({
            "Quando": quando.strftime("%d/%m/%Y %H:%M") if quando else "",
            "Quem": nomes.get(str(r.get("usuario")), "sistema" if not r.get("usuario") else str(r["usuario"])[:8]),
            "Ação": ACOES.get(r.get("acao"), r.get("acao")),
            "Tipo": TABELAS_HISTORICO.get(r.get("tabela"), r.get("tabela")),
            "Registro": registro,
            "O que mudou": resumir_mudanca(r.get("antes"), r.get("depois")),
        })
    return saida


# ---- Backup ------------------------------------------------------------------

def gerar_backup_xlsx() -> bytes:
    """Planilha com todos os postes e todas as O.S. (uma aba cada)."""
    postes = pd.DataFrame(listar_postes())
    ordens = pd.DataFrame(listar_ordens("Todos"))
    if "materiais_lista" in ordens:
        ordens = ordens.drop(columns=["materiais_lista"])
    for df in (postes, ordens):
        for coluna in df.columns:
            if df[coluna].map(lambda v: isinstance(v, (dict, list))).any():
                df[coluna] = df[coluna].map(str)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        postes.to_excel(writer, index=False, sheet_name="Postes")
        ordens.to_excel(writer, index=False, sheet_name="Ordens de serviço")
    return buffer.getvalue()
