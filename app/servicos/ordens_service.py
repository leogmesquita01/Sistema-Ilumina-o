from typing import List, Dict, Any, Optional
import json
import datetime
import urllib.parse
from app.database.conexao import obter_conexao, obter_supabase, obter_supabase_admin
from app.servicos.dados_postes import atualizar_status_poste


def listar_ordens(filtro_status: Optional[str] = None) -> List[Dict[str, Any]]:
    sb = obter_supabase()
    if sb:
        try:
            query = sb.table("ordens_servico").select("*, postes(logradouro, bairro, latitude, longitude, tipo_luminaria, potencia)").order("id", desc=True)
            if filtro_status and filtro_status != "Todos":
                query = query.eq("status", filtro_status)
            res = query.execute()
            rows = res.data or []
            resultado = []
            for r in rows:
                item = dict(r)
                poste_rel = item.pop("postes", None) or {}
                item["logradouro"] = poste_rel.get("logradouro", "")
                item["bairro"] = poste_rel.get("bairro", "")
                item["latitude"] = poste_rel.get("latitude", 0.0)
                item["longitude"] = poste_rel.get("longitude", 0.0)
                item["tipo_luminaria"] = poste_rel.get("tipo_luminaria", "LED")
                item["potencia"] = poste_rel.get("potencia", 100)

                if item.get("materiais"):
                    try:
                        item["materiais_lista"] = json.loads(item["materiais"]) if isinstance(item["materiais"], str) else item["materiais"]
                    except Exception:
                        item["materiais_lista"] = []
                else:
                    item["materiais_lista"] = []
                resultado.append(item)
            return resultado
        except Exception:
            pass

    conn = obter_conexao()
    cursor = conn.cursor()

    query = """
        SELECT os.*, p.logradouro, p.bairro, p.latitude, p.longitude, p.tipo_luminaria, p.potencia
        FROM ordens_servico os
        LEFT JOIN postes p ON os.codigo_poste = p.codigo
    """
    params = []
    if filtro_status and filtro_status != "Todos":
        query += " WHERE os.status = ?"
        params.append(filtro_status)

    query += " ORDER BY os.id DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    resultado = []
    for r in rows:
        item = dict(r)
        if item.get("materiais"):
            try:
                item["materiais_lista"] = json.loads(item["materiais"])
            except Exception:
                item["materiais_lista"] = []
        else:
            item["materiais_lista"] = []
        resultado.append(item)

    return resultado


def criar_ordem_servico(
    codigo_poste: str,
    defeito: str,
    prioridade: str = "Normal",
    materiais: List[Dict[str, Any]] = None,
    solicitante: str = "Secretaria de Infraestrutura",
    observacoes: str = ""
) -> str:
    materiais_json = json.dumps(materiais if materiais else [])
    novo_status = "urgente" if prioridade == "Urgente" else "chamado_aberto"

    sb = obter_supabase_admin()
    if sb:
        res_count = sb.table("ordens_servico").select("id", count="exact").execute()
        total = (res_count.count or len(res_count.data or [])) + 1
        protocolo = f"OS-2026-{total:04d}"

        sb.table("ordens_servico").insert({
            "protocolo": protocolo,
            "codigo_poste": codigo_poste,
            "defeito": defeito,
            "prioridade": prioridade,
            "materiais": materiais_json,
            "solicitante": solicitante,
            "status": "aberta",
            "observacoes": observacoes,
        }).execute()

        atualizar_status_poste(codigo_poste, novo_status)
        return protocolo

    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM ordens_servico;")
    total = cursor.fetchone()[0] + 1
    protocolo = f"OS-2026-{total:04d}"

    cursor.execute("""
        INSERT INTO ordens_servico (
            protocolo, codigo_poste, defeito, prioridade, materiais, solicitante, status, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, 'aberta', ?)
    """, (
        protocolo, codigo_poste, defeito, prioridade,
        materiais_json, solicitante, observacoes
    ))

    cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;",
                   (novo_status, codigo_poste))

    conn.commit()
    conn.close()
    return protocolo


def concluir_ordem_servico(protocolo: str):
    sb = obter_supabase_admin()
    if sb:
        res = sb.table("ordens_servico").select("codigo_poste").eq("protocolo", protocolo).limit(1).execute()
        if not res.data:
            return
        codigo_poste = res.data[0]["codigo_poste"]
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sb.table("ordens_servico").update({
            "status": "concluida",
            "data_conclusao": agora
        }).eq("protocolo", protocolo).execute()
        atualizar_status_poste(codigo_poste, "normal")
        return

    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT codigo_poste FROM ordens_servico WHERE protocolo = ?;", (protocolo,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    codigo_poste = row["codigo_poste"]

    cursor.execute("""
        UPDATE ordens_servico 
        SET status = 'concluida', data_conclusao = CURRENT_TIMESTAMP
        WHERE protocolo = ?;
    """, (protocolo,))

    cursor.execute("UPDATE postes SET status = 'normal', data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", (codigo_poste,))

    conn.commit()
    conn.close()


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
    materiais: List[Dict[str, Any]] = None
) -> str:
    materiais_str = "\n".join([f"  • {m.get('quantidade', 1)}x {m.get('item', '')}" for m in (materiais or [])]) if materiais else "  • Conforme vistoria no local"
    if latitude and longitude and (round(float(latitude), 4) != -6.1611 or round(float(longitude), 4) != -35.6025):
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
    else:
        destino_end = urllib.parse.quote(f"{logradouro}, {bairro}, Boa Saúde - RN")
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={destino_end}"

    texto = (
        f"🚨 *ORDEM DE SERVIÇO DE ILUMINAÇÃO PÚBLICA*\n"
        f"*Prefeitura de Boa Saúde / RN*\n\n"
        f"📄 *Protocolo:* {protocolo}\n"
        f"📍 *Poste:* {codigo_poste}\n"
        f"🛣️ *Endereço:* {logradouro} - {bairro}\n"
        f"⚠️ *Defeito:* {defeito} (Prioridade: {prioridade})\n"
        f"💡 *Luminária Atual:* {luminaria}\n\n"
        f"🧰 *MATERIAIS NECESSÁRIOS PARA A VIATURA:*\n"
        f"{materiais_str}\n\n"
        f"🧭 *ROTA GPS DO POSTE:*\n"
        f"{maps_link}"
    )

    encoded = urllib.parse.quote(texto)
    return f"https://wa.me/?text={encoded}"
