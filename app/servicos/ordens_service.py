"""Ordens de serviço: abertura, conclusão e mensagem de despacho no WhatsApp."""
import datetime
import json
import urllib.parse
import uuid
from typing import Any, Dict, Iterable, List, Optional

from app.cache import cache_ttl, limpar_cache
from app.constantes import (
    NOME_MUNICIPIO,
    OS_ABERTA,
    OS_CONCLUIDA,
    PRIORIDADE_URGENTE,
    STATUS_CHAMADO,
    STATUS_NORMAL,
    STATUS_URGENTE,
    UF_MUNICIPIO,
)
from app.database.conexao import modo_local, obter_conexao, obter_supabase
from app.database.paginacao import buscar_todas_paginas
from app.fuso import agora_local
from app.servicos.dados_postes import atualizar_status_poste, localizacao_pendente, obter_poste_por_codigo


def _materiais_como_lista(valor) -> List[Dict[str, Any]]:
    if not valor:
        return []
    if isinstance(valor, list):
        return valor
    try:
        dados = json.loads(valor)
        return dados if isinstance(dados, list) else []
    except (TypeError, ValueError):
        return []


def listar_ordens(filtro_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista ordens, paginando o Supabase até esgotar o resultado."""
    return _listar_ordens_cache(filtro_status or "Todos")


@cache_ttl()
def _listar_ordens_cache(filtro_status: str) -> List[Dict[str, Any]]:
    if not modo_local():
        sb = obter_supabase()

        def criar_consulta():
            consulta = sb.table("ordens_servico").select(
                "*, postes(logradouro, bairro, latitude, longitude, tipo_luminaria, potencia)"
            ).order("id", desc=True)
            if filtro_status and filtro_status != "Todos":
                consulta = consulta.eq("status", filtro_status)
            return consulta

        resultado = []
        for r in buscar_todas_paginas(criar_consulta):
            item = dict(r)
            poste_rel = item.pop("postes", None) or {}
            item["logradouro"] = poste_rel.get("logradouro") or ""
            item["bairro"] = poste_rel.get("bairro") or ""
            item["latitude"] = poste_rel.get("latitude")
            item["longitude"] = poste_rel.get("longitude")
            item["tipo_luminaria"] = poste_rel.get("tipo_luminaria") or "LED"
            item["potencia"] = poste_rel.get("potencia") or 100
            item["materiais_lista"] = _materiais_como_lista(item.get("materiais"))
            resultado.append(item)
        return resultado

    conn = obter_conexao()
    query = """
        SELECT os.*, p.logradouro, p.bairro, p.latitude, p.longitude, p.tipo_luminaria, p.potencia
        FROM ordens_servico os
        LEFT JOIN postes p ON os.codigo_poste = p.codigo
    """
    params: list = []
    if filtro_status and filtro_status != "Todos":
        query += " WHERE os.status = ?"
        params.append(filtro_status)
    query += " ORDER BY os.id DESC;"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    resultado = []
    for r in rows:
        item = dict(r)
        item["materiais_lista"] = _materiais_como_lista(item.get("materiais"))
        resultado.append(item)
    return resultado


def status_pelas_ordens_abertas(prioridades_abertas: Iterable[str]) -> str:
    """Status que o poste deve ter, dadas as prioridades das O.S. ainda abertas.

    Sem O.S. aberta → normal. Alguma urgente → urgente. Senão → chamado aberto.
    """
    prioridades = list(prioridades_abertas)
    if not prioridades:
        return STATUS_NORMAL
    if PRIORIDADE_URGENTE in prioridades:
        return STATUS_URGENTE
    return STATUS_CHAMADO


def _recalcular_status_poste(codigo_poste: str) -> None:
    """Recalcula o status do poste a partir de TODAS as O.S. abertas dele.

    Antes, concluir uma O.S. sempre voltava o poste para "normal", mesmo que ele
    tivesse outra O.S. aberta.
    """
    if not modo_local():
        res = (
            obter_supabase()
            .table("ordens_servico")
            .select("prioridade")
            .eq("codigo_poste", codigo_poste)
            .eq("status", OS_ABERTA)
            .execute()
        )
        prioridades = [r.get("prioridade") for r in (res.data or [])]
    else:
        conn = obter_conexao()
        rows = conn.execute(
            "SELECT prioridade FROM ordens_servico WHERE codigo_poste = ? AND status = ?;",
            (codigo_poste, OS_ABERTA),
        ).fetchall()
        conn.close()
        prioridades = [r["prioridade"] for r in rows]

    atualizar_status_poste(codigo_poste, status_pelas_ordens_abertas(prioridades))


def formatar_protocolo(ano: int, numero: int) -> str:
    return f"OS-{ano}-{numero:04d}"


def criar_ordem_servico(
    codigo_poste: str,
    defeito: str,
    prioridade: str = "Normal",
    materiais: Optional[List[Dict[str, Any]]] = None,
    solicitante: str = "Secretaria de Infraestrutura",
    observacoes: str = "",
) -> str:
    """Abre uma O.S. e devolve o protocolo.

    O número do protocolo vem do ``id`` gerado pelo banco (único por definição),
    não mais de ``COUNT(*) + 1``, que repetia números quando duas O.S. eram
    abertas ao mesmo tempo ou quando alguma era apagada. O ano é o atual.
    """
    # Usa a grafia que está no banco ("p-01" digitado → "P-01"): a FK diferencia caixa.
    poste = obter_poste_por_codigo(codigo_poste)
    if poste:
        codigo_poste = poste["codigo"]

    registro = {
        "codigo_poste": codigo_poste,
        "defeito": defeito,
        "prioridade": prioridade,
        "materiais": json.dumps(materiais or [], ensure_ascii=False),
        "solicitante": solicitante,
        "status": OS_ABERTA,
        "observacoes": observacoes,
    }

    if not modo_local():
        # O protocolo é preenchido pelo gatilho do banco (migração 002).
        res = obter_supabase().table("ordens_servico").insert(registro).execute()
        protocolo = (res.data or [{}])[0].get("protocolo")
        if not protocolo:
            raise RuntimeError(
                "O banco não gerou o protocolo. Aplique supabase/migrations/002_login.sql."
            )
    else:
        conn = obter_conexao()
        try:
            colunas = ", ".join(["protocolo", *registro])
            marcadores = ", ".join("?" for _ in range(len(registro) + 1))
            temporario = f"TMP-{uuid.uuid4()}"
            cursor = conn.execute(
                f"INSERT INTO ordens_servico ({colunas}) VALUES ({marcadores})",
                (temporario, *registro.values()),
            )
            protocolo = formatar_protocolo(agora_local().year, cursor.lastrowid)
            conn.execute("UPDATE ordens_servico SET protocolo = ? WHERE id = ?;", (protocolo, cursor.lastrowid))
            conn.commit()
        finally:
            conn.close()

    _recalcular_status_poste(codigo_poste)
    limpar_cache()
    return protocolo


def concluir_ordem_servico(protocolo: str) -> None:
    if not modo_local():
        sb = obter_supabase()
        res = sb.table("ordens_servico").select("codigo_poste").eq("protocolo", protocolo).limit(1).execute()
        if not res.data:
            return
        codigo_poste = res.data[0]["codigo_poste"]
        sb.table("ordens_servico").update({
            "status": OS_CONCLUIDA,
            "data_conclusao": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }).eq("protocolo", protocolo).execute()
    else:
        conn = obter_conexao()
        row = conn.execute("SELECT codigo_poste FROM ordens_servico WHERE protocolo = ?;", (protocolo,)).fetchone()
        if not row:
            conn.close()
            return
        codigo_poste = row["codigo_poste"]
        conn.execute(
            "UPDATE ordens_servico SET status = ?, data_conclusao = CURRENT_TIMESTAMP WHERE protocolo = ?;",
            (OS_CONCLUIDA, protocolo),
        )
        conn.commit()
        conn.close()

    _recalcular_status_poste(codigo_poste)
    limpar_cache()


def link_rota(latitude, longitude, logradouro: str = "", bairro: str = "") -> str:
    """Link do Google Maps: pelas coordenadas, ou pelo endereço se não houver."""
    if not localizacao_pendente({"latitude": latitude, "longitude": longitude}):
        return f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
    destino = urllib.parse.quote(f"{logradouro}, {bairro}, {NOME_MUNICIPIO} - {UF_MUNICIPIO}")
    return f"https://www.google.com/maps/dir/?api=1&destination={destino}"


def gerar_mensagem_whatsapp(
    protocolo: str,
    codigo_poste: str,
    logradouro: str,
    bairro: str,
    defeito: str,
    prioridade: str,
    luminaria: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    materiais: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if materiais:
        materiais_str = "\n".join(f"  • {m.get('quantidade', 1)}x {m.get('item', '')}" for m in materiais)
    else:
        materiais_str = "  • Conforme vistoria no local"

    texto = (
        f"🚨 *ORDEM DE SERVIÇO DE ILUMINAÇÃO PÚBLICA*\n"
        f"*Prefeitura de {NOME_MUNICIPIO} / {UF_MUNICIPIO}*\n\n"
        f"📄 *Protocolo:* {protocolo}\n"
        f"📍 *Poste:* {codigo_poste}\n"
        f"🛣️ *Endereço:* {logradouro} - {bairro}\n"
        f"⚠️ *Defeito:* {defeito} (Prioridade: {prioridade})\n"
        f"💡 *Luminária Atual:* {luminaria}\n\n"
        f"🧰 *MATERIAIS NECESSÁRIOS PARA A VIATURA:*\n"
        f"{materiais_str}\n\n"
        f"🧭 *ROTA GPS DO POSTE:*\n"
        f"{link_rota(latitude, longitude, logradouro, bairro)}"
    )

    return f"https://wa.me/?text={urllib.parse.quote(texto)}"
