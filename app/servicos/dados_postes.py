"""
Serviço de Dados dos Postes (Supabase Cloud + Fallback SQLite)
Responsável por consultas, buscas e cadastro de postes da rede de energia.
"""

from typing import List, Dict, Any, Optional
import datetime
from app.database.conexao import obter_conexao, obter_supabase


def obter_resumo_indicadores() -> Dict[str, Any]:
    """Retorna os principais indicadores para os cards no topo."""
    sb = obter_supabase()
    if sb:
        try:
            res_postes = sb.table("postes").select("tipo_luminaria, status").execute()
            postes = res_postes.data or []
            total_postes = len(postes)
            total_led = sum(1 for p in postes if p.get("tipo_luminaria") == "LED")
            total_chamados = sum(
                1 for p in postes if p.get("status") in ("chamado_aberto", "urgente", "defeito_urgente")
            )

            res_os = sb.table("ordens_servico").select("status").execute()
            ordens = res_os.data or []
            os_abertas = sum(1 for o in ordens if o.get("status") == "aberta")
            os_concluidas = sum(1 for o in ordens if o.get("status") == "concluida")

            taxa_led = round((total_led / total_postes * 100), 1) if total_postes > 0 else 0
            return {
                "total_postes": total_postes,
                "total_led": total_led,
                "taxa_led": taxa_led,
                "total_chamados": total_chamados,
                "os_abertas": os_abertas,
                "os_concluidas": os_concluidas,
            }
        except Exception as e:
            print(f"Aviso ao consultar indicadores no Supabase: {e}")

    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM postes;")
    total_postes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM postes WHERE tipo_luminaria = 'LED';")
    total_led = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM postes WHERE status IN ('chamado_aberto', 'urgente', 'defeito_urgente');")
    total_chamados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = 'aberta';")
    os_abertas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = 'concluida';")
    os_concluidas = cursor.fetchone()[0]

    conn.close()

    taxa_led = round((total_led / total_postes * 100), 1) if total_postes > 0 else 0

    return {
        "total_postes": total_postes,
        "total_led": total_led,
        "taxa_led": taxa_led,
        "total_chamados": total_chamados,
        "os_abertas": os_abertas,
        "os_concluidas": os_concluidas,
    }


def listar_postes(filtro_status: Optional[str] = None, termo_busca: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna a lista de postes filtrados."""
    sb = obter_supabase()
    if sb:
        try:
            query = sb.table("postes").select("*").order("id", desc=True)
            if filtro_status and filtro_status != "Todos":
                query = query.eq("status", filtro_status)
            if termo_busca and termo_busca.strip():
                t = termo_busca.strip()
                query = query.or_(f"codigo.ilike.%{t}%,logradouro.ilike.%{t}%,bairro.ilike.%{t}%")
            res = query.execute()
            return res.data or []
        except Exception as e:
            print(f"Aviso ao listar postes no Supabase: {e}")

    conn = obter_conexao()
    cursor = conn.cursor()

    query = "SELECT * FROM postes WHERE 1=1"
    params = []

    if filtro_status and filtro_status != "Todos":
        query += " AND status = ?"
        params.append(filtro_status)

    if termo_busca and termo_busca.strip():
        termo = f"%{termo_busca.strip()}%"
        query += " AND (codigo LIKE ? OR logradouro LIKE ? OR bairro LIKE ?)"
        params.extend([termo, termo, termo])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def obter_poste_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Busca um poste pelo código da plaqueta COSERN."""
    if not codigo:
        return None

    sb = obter_supabase()
    if sb:
        try:
            res = sb.table("postes").select("*").ilike("codigo", codigo.strip()).limit(1).execute()
            if not res.data:
                return None
            poste = res.data[0]
            res_os = (
                sb.table("ordens_servico")
                .select("*")
                .eq("codigo_poste", poste["codigo"])
                .order("id", desc=True)
                .limit(10)
                .execute()
            )
            poste["historico_os"] = res_os.data or []
            return poste
        except Exception as e:
            print(f"Aviso ao buscar poste por código no Supabase: {e}")

    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM postes WHERE codigo = ? COLLATE NOCASE;", (codigo.strip(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    poste = dict(row)

    cursor.execute("""
        SELECT * FROM ordens_servico 
        WHERE codigo_poste = ? 
        ORDER BY id DESC LIMIT 10;
    """, (poste["codigo"],))
    poste["historico_os"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return poste


def cadastrar_poste(dados: Dict[str, Any]) -> bool:
    """Cadastra um novo poste no banco Supabase (e sincroniza localmente)."""
    novo_poste = {
        "codigo": dados["codigo"].strip(),
        "latitude": float(dados["latitude"]),
        "longitude": float(dados["longitude"]),
        "logradouro": dados.get("logradouro") or "Não informado",
        "bairro": dados.get("bairro") or "Centro",
        "referencia": dados.get("referencia") or "",
        "tipo_luminaria": dados.get("tipo_luminaria") or "LED",
        "potencia": int(dados.get("potencia", 100)),
        "tipo_poste": dados.get("tipo_poste") or "Concreto Duplo T",
        "tipo_braco": dados.get("tipo_braco") or "Braço Médio 2m",
        "status": dados.get("status") or "normal",
        "observacoes": dados.get("observacoes") or "",
    }

    sb = obter_supabase()
    if sb:
        sb.table("postes").insert(novo_poste).execute()
        return True

    conn = obter_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO postes (
                codigo, latitude, longitude, logradouro, bairro, referencia,
                tipo_luminaria, potencia, tipo_poste, tipo_braco, status, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            novo_poste["codigo"], novo_poste["latitude"], novo_poste["longitude"],
            novo_poste["logradouro"], novo_poste["bairro"], novo_poste["referencia"],
            novo_poste["tipo_luminaria"], novo_poste["potencia"], novo_poste["tipo_poste"],
            novo_poste["tipo_braco"], novo_poste["status"], novo_poste["observacoes"]
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e


def atualizar_status_poste(codigo: str, status: str):
    """Atualiza o status de operação do poste."""
    sb = obter_supabase()
    if sb:
        try:
            sb.table("postes").update({
                "status": status,
                "data_atualizacao": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).eq("codigo", codigo).execute()
            return
        except Exception as e:
            print(f"Aviso ao atualizar status no Supabase: {e}")

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", (status, codigo))
    conn.commit()
    conn.close()
