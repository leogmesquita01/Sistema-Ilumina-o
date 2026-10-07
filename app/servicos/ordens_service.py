"""
Serviço de Ordens de Serviço e Solicitação de Materiais
"""

from typing import List, Dict, Any, Optional
import json
import urllib.parse
from app.database.conexao import obter_conexao
from app.servicos.dados_postes import atualizar_status_poste

def listar_ordens(filtro_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna todas as ordens de serviço cadastradas."""
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
    """Cria uma nova ordem de serviço e atualiza o status do poste."""
    conn = obter_conexao()
    cursor = conn.cursor()

    # Gera número de protocolo anual sequencial
    cursor.execute("SELECT COUNT(*) FROM ordens_servico;")
    total = cursor.fetchone()[0] + 1
    protocolo = f"OS-{2026}-{total:04d}"

    materiais_json = json.dumps(materiais if materiais else [])
    novo_status = "urgente" if prioridade == "Urgente" else "chamado_aberto"

    cursor.execute("""
        INSERT INTO ordens_servico (
            protocolo, codigo_poste, defeito, prioridade, materiais, solicitante, status, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, 'aberta', ?)
    """, (
        protocolo, codigo_poste, defeito, prioridade,
        materiais_json, solicitante, observacoes
    ))

    # Atualiza status do poste
    cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;",
                   (novo_status, codigo_poste))

    conn.commit()
    conn.close()
    return protocolo

def concluir_ordem_servico(protocolo: str):
    """Marca uma ordem como concluída e restaura o status do poste para 'normal'."""
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

    # Restaura o poste para operação normal
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
    latitude: float,
    longitude: float,
    materiais: List[Dict[str, Any]]
) -> str:
    """Monta a mensagem pronta e link formatado para envio no WhatsApp da viatura/eletricista."""
    materiais_str = "\n".join([f"  • {m.get('quantidade', 1)}x {m.get('item', '')}" for m in materiais]) if materiais else "  • Conforme vistoria no local"
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"

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
