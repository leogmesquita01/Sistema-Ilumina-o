from typing import List, Dict, Any, Optional
import datetime
from app.cache import cache_ttl, limpar_cache
from app.database.conexao import obter_conexao, obter_supabase, obter_supabase_admin
from app.database.paginacao import buscar_todas_paginas


@cache_ttl()
def obter_resumo_indicadores() -> Dict[str, Any]:
    """Indicadores do painel.

    Usa ``count=exact`` do PostgREST em vez de baixar as tabelas inteiras: com
    milhares de postes, contar no cliente estourava o limite de 1.000 linhas por
    requisição e os números saíam errados (para menos), sem aviso.
    """
    sb = obter_supabase()
    if sb:
        try:
            def contar(tabela: str, coluna: Optional[str] = None,
                       valor: Optional[str] = None,
                       valores: Optional[List[str]] = None) -> int:
                consulta = sb.table(tabela).select("id", count="exact").limit(1)
                if coluna and valor is not None:
                    consulta = consulta.eq(coluna, valor)
                if coluna and valores is not None:
                    consulta = consulta.in_(coluna, valores)
                return consulta.execute().count or 0

            total_postes = contar("postes")
            total_led = contar("postes", "tipo_luminaria", "LED")
            total_chamados = contar(
                "postes", "status", valores=["chamado_aberto", "urgente", "defeito_urgente"]
            )
            os_abertas = contar("ordens_servico", "status", "aberta")
            os_concluidas = contar("ordens_servico", "status", "concluida")

            taxa_led = round((total_led / total_postes * 100), 1) if total_postes > 0 else 0

            return {
                "total_postes": total_postes,
                "total_led": total_led,
                "taxa_led": taxa_led,
                "total_chamados": total_chamados,
                "os_abertas": os_abertas,
                "os_concluidas": os_concluidas,
            }
        except Exception:
            pass

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
    """Lista postes, paginando o Supabase até esgotar o resultado.

    A normalização dos argumentos acontece antes do cache para que "sem filtro"
    e "Todos" caiam na mesma entrada.
    """
    return _listar_postes_cache(filtro_status or "Todos", (termo_busca or "").strip())


@cache_ttl()
def _listar_postes_cache(filtro_status: str, termo_busca: str) -> List[Dict[str, Any]]:
    sb = obter_supabase()
    if sb:
        try:
            def criar_consulta():
                consulta = sb.table("postes").select("*").order("id", desc=True)
                if filtro_status and filtro_status != "Todos":
                    consulta = consulta.eq("status", filtro_status)
                if termo_busca:
                    # vírgula e parênteses quebrariam a sintaxe de filtro do PostgREST
                    t = termo_busca.replace(",", " ").replace("(", " ").replace(")", " ")
                    consulta = consulta.or_(
                        f"codigo.ilike.%{t}%,logradouro.ilike.%{t}%,bairro.ilike.%{t}%"
                    )
                return consulta

            return buscar_todas_paginas(criar_consulta)
        except Exception:
            pass

    conn = obter_conexao()
    cursor = conn.cursor()

    query = "SELECT * FROM postes WHERE 1=1"
    params = []

    if filtro_status and filtro_status != "Todos":
        query += " AND status = ?"
        params.append(filtro_status)

    if termo_busca:
        termo = f"%{termo_busca}%"
        query += " AND (codigo LIKE ? OR logradouro LIKE ? OR bairro LIKE ?)"
        params.extend([termo, termo, termo])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


@cache_ttl()
def obter_poste_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
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
        except Exception:
            pass

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
    lat_val = dados.get("latitude")
    lng_val = dados.get("longitude")
    novo_poste = {
        "codigo": dados["codigo"].strip(),
        "latitude": float(lat_val) if lat_val is not None else -6.1611,
        "longitude": float(lng_val) if lng_val is not None else -35.6025,
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

    sb = obter_supabase_admin()
    if sb:
        sb.table("postes").insert(novo_poste).execute()
        limpar_cache()
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
        limpar_cache()
        return True
    except Exception as e:
        conn.close()
        raise e


def atualizar_status_poste(codigo: str, status: str):
    sb = obter_supabase_admin()
    if sb:
        try:
            sb.table("postes").update({
                "status": status,
                "data_atualizacao": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).eq("codigo", codigo).execute()
            limpar_cache()
            return
        except Exception:
            pass

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", (status, codigo))
    conn.commit()
    conn.close()
    limpar_cache()
