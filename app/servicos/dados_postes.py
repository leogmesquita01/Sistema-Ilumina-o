"""
Serviço de Dados dos Postes (SQLite)
Responsável por consultas, buscas e cadastro de postes da rede de energia.
"""

from typing import List, Dict, Any, Optional
from app.database.conexao import obter_conexao

def obter_resumo_indicadores() -> Dict[str, Any]:
    """Retorna os principais indicadores para os cards no topo."""
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
        "os_concluidas": os_concluidas
    }

def listar_postes(filtro_status: Optional[str] = None, termo_busca: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna a lista de postes filtrados."""
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
    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM postes WHERE codigo = ? COLLATE NOCASE;", (codigo.strip(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    poste = dict(row)

    # Busca histórico de ordens de serviço deste poste
    cursor.execute("""
        SELECT * FROM ordens_servico 
        WHERE codigo_poste = ? 
        ORDER BY id DESC LIMIT 10;
    """, (poste["codigo"],))
    poste["historico_os"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return poste

def cadastrar_poste(dados: Dict[str, Any]) -> bool:
    """Cadastra um novo poste no banco."""
    conn = obter_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO postes (
                codigo, latitude, longitude, logradouro, bairro, referencia,
                tipo_luminaria, potencia, tipo_poste, tipo_braco, status, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["codigo"].strip(), dados["latitude"], dados["longitude"],
            dados.get("logradouro", "Não informado"), dados.get("bairro", "Centro"),
            dados.get("referencia", ""), dados.get("tipo_luminaria", "LED"),
            dados.get("potencia", 100), dados.get("tipo_poste", "Concreto Duplo T"),
            dados.get("tipo_braco", "Braço Médio 2m"), dados.get("status", "normal"),
            dados.get("observacoes", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

def atualizar_status_poste(codigo: str, status: str):
    """Atualiza o status de operação do poste."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", (status, codigo))
    conn.commit()
    conn.close()
