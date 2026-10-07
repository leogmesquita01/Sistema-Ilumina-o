"""
Servidor Principal FastAPI
Web App de Gestão e Mapa da Rede de Postes de Energia (COSERN / Boa Saúde - RN)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import json
import io
import pandas as pd
from typing import Optional, List

from app.database import init_db, get_connection
from app.models import PosteCreate, OrdemServicoCreate
from app.importer import import_poles_file
from app.seed_data import seed_database

# Inicializa o app FastAPI com metadados claros
app = FastAPI(
    title="Sistema de Mapeamento de Iluminação Pública - Boa Saúde/RN",
    description="API de busca rápida de postes COSERN, georreferenciamento e despacho de ordens de serviço de manutenção.",
    version="1.0.0"
)

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados na subida
@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

# ==========================================
# ROTAS DE POSTES
# ==========================================

@app.get("/api/postes", summary="Listar todos os postes cadastrados")
def listar_postes(
    status: Optional[str] = None,
    bairro: Optional[str] = None,
    tipo_luminaria: Optional[str] = None,
    limite: int = 5000
):
    """Retorna a lista de postes com coordenadas para plotar no mapa."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM postes WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if bairro:
        query += " AND bairro LIKE ?"
        params.append(f"%{bairro}%")
    if tipo_luminaria:
        query += " AND tipo_luminaria = ?"
        params.append(tipo_luminaria)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limite)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@app.get("/api/postes/buscar", summary="Busca rápida por código ou rua")
def buscar_postes(q: str = Query(..., min_length=1, description="Código da plaqueta COSERN ou nome do logradouro")):
    """Busca em tempo real postes que correspondam ao termo digitado."""
    termo = f"%{q.strip()}%"
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM postes 
        WHERE codigo LIKE ? OR logradouro LIKE ? OR bairro LIKE ?
        ORDER BY 
            CASE WHEN codigo = ? THEN 0
                 WHEN codigo LIKE ? THEN 1
                 ELSE 2 END,
            codigo ASC
        LIMIT 20;
    """, (termo, termo, termo, q.strip(), f"{q.strip()}%"))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/postes/{codigo}", summary="Obter detalhes de um poste específico")
def obter_poste(codigo: str):
    """Busca um poste exatamente pelo seu código de plaqueta da COSERN."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM postes WHERE codigo = ? COLLATE NOCASE;", (codigo.strip(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Poste com código '{codigo}' não encontrado no banco de dados.")

    poste = dict(row)

    # Busca histórico de manutenções desse poste
    cursor.execute("""
        SELECT * FROM ordens_servico 
        WHERE codigo_poste = ? 
        ORDER BY id DESC LIMIT 10;
    """, (poste["codigo"],))
    ordens = [dict(r) for r in cursor.fetchall()]
    poste["historico_os"] = ordens

    conn.close()
    return poste

@app.post("/api/postes", summary="Cadastrar novo poste manualmente (Modo Campo)")
def cadastrar_poste(poste: PosteCreate):
    """Permite cadastrar um poste manualmente direto do celular no local."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO postes (
                codigo, latitude, longitude, logradouro, bairro, referencia,
                tipo_luminaria, potencia, tipo_poste, tipo_braco, status, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            poste.codigo.strip(), poste.latitude, poste.longitude, poste.logradouro,
            poste.bairro, poste.referencia, poste.tipo_luminaria, poste.potencia,
            poste.tipo_poste, poste.tipo_braco, poste.status, poste.observacoes
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar poste: {str(e)}")

    conn.close()
    return {"sucesso": True, "mensagem": f"Poste {poste.codigo} cadastrado com sucesso!"}

# ==========================================
# ROTAS DE ORDENS DE SERVIÇO & REPAROS
# ==========================================

@app.get("/api/ordens-servico", summary="Listar ordens de serviço de manutenção")
def listar_ordens_servico(status: Optional[str] = None):
    """Retorna todas as solicitações de reparo e materiais solicitados."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT os.*, p.logradouro, p.bairro, p.latitude, p.longitude, p.tipo_luminaria, p.potencia
        FROM ordens_servico os
        LEFT JOIN postes p ON os.codigo_poste = p.codigo
    """
    params = []
    if status:
        query += " WHERE os.status = ?"
        params.append(status)

    query += " ORDER BY os.id DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    resultado = []
    for r in rows:
        item = dict(r)
        if item.get("materiais"):
            try:
                item["materiais"] = json.loads(item["materiais"])
            except Exception:
                pass
        resultado.append(item)
    return resultado

@app.post("/api/ordens-servico", summary="Criar nova ordem de serviço com kit de equipamentos")
def criar_ordem_servico(dados: OrdemServicoCreate):
    """Cria uma solicitação de reparo e atualiza o status do poste."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se poste existe
    cursor.execute("SELECT id FROM postes WHERE codigo = ?;", (dados.codigo_poste,))
    poste = cursor.fetchone()
    if not poste:
        conn.close()
        raise HTTPException(status_code=404, detail="Poste não encontrado.")

    # Gera número de protocolo
    cursor.execute("SELECT COUNT(*) FROM ordens_servico;")
    total = cursor.fetchone()[0] + 1
    protocolo = f"OS-{2026}-{total:04d}"

    materiais_json = json.dumps([m.dict() for m in dados.materiais])
    novo_status_poste = "urgente" if dados.prioridade == "Urgente" else "chamado_aberto"

    try:
        cursor.execute("""
            INSERT INTO ordens_servico (
                protocolo, codigo_poste, defeito, prioridade, materiais, solicitante, status, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, 'aberta', ?)
        """, (
            protocolo, dados.codigo_poste, dados.defeito, dados.prioridade,
            materiais_json, dados.solicitante, dados.observacoes
        ))

        # Atualiza status do poste
        cursor.execute("UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", 
                       (novo_status_poste, dados.codigo_poste))

        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao criar O.S.: {str(e)}")

    conn.close()
    return {
        "sucesso": True,
        "protocolo": protocolo,
        "mensagem": f"Ordem de Serviço {protocolo} criada com sucesso para o poste {dados.codigo_poste}."
    }

@app.patch("/api/ordens-servico/{protocolo}/status", summary="Atualizar status da OS (concluir reparo)")
def atualizar_status_os(protocolo: str, status: str = Query(..., regex="^(aberta|em_rota|concluida|cancelada)$")):
    """Atualiza o status da ordem de serviço. Se concluída, reseta o poste para status 'normal'."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT codigo_poste FROM ordens_servico WHERE protocolo = ?;", (protocolo,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada.")

    codigo_poste = row["codigo_poste"]

    cursor.execute("""
        UPDATE ordens_servico 
        SET status = ?, 
            data_conclusao = CASE WHEN ? = 'concluida' THEN CURRENT_TIMESTAMP ELSE data_conclusao END
        WHERE protocolo = ?;
    """, (status, status, protocolo))

    if status == "concluida":
        # Se concluiu, o poste volta a ficar normal
        cursor.execute("UPDATE postes SET status = 'normal', data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;", (codigo_poste,))

    conn.commit()
    conn.close()
    return {"sucesso": True, "protocolo": protocolo, "novo_status": status}

# ==========================================
# IMPORTAÇÃO DA BASE COSERN (EXCEL / CSV)
# ==========================================

@app.post("/api/importar", summary="Importar planilha de postes da COSERN ou ANEEL")
async def importar_planilha(arquivo: UploadFile = File(...)):
    """Recebe arquivo Excel (.xlsx, .xls) ou CSV e importa para o banco SQLite."""
    try:
        conteudo = await arquivo.read()
        resultado = import_poles_file(conteudo, arquivo.filename)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/modelo-planilha", summary="Baixar planilha modelo da COSERN para preenchimento")
def baixar_modelo_planilha():
    """Gera uma planilha Excel modelo pronta para ser preenchida."""
    dados_exemplo = {
        "CODIGO_POSTE": ["CSR-2001", "CSR-2002", "CSR-2003"],
        "LATITUDE": [-6.1615, -6.1620, -6.1628],
        "LONGITUDE": [-35.6022, -35.6031, -35.6040],
        "LOGRADOURO": ["Rua Principal", "Travessa São Pedro", "Av. Brasil"],
        "BAIRRO": ["Centro", "Centro", "Bela Vista"],
        "REFERENCIA": ["Ao lado do colégio", "Próximo à praça", "Em frente ao posto"],
        "TIPO_LUMINARIA": ["LED", "Vapor de Sódio", "LED"],
        "POTENCIA_WATTS": [100, 70, 150],
        "TIPO_POSTE": ["Concreto Duplo T", "Concreto Circular", "Concreto Duplo T"],
        "TIPO_BRACO": ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m"]
    }
    df = pd.DataFrame(dados_exemplo)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Postes COSERN")
    output.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="modelo_postes_cosern.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==========================================
# ESTATÍSTICAS DO MUNICÍPIO
# ==========================================

@app.get("/api/estatisticas", summary="Indicadores gerais para a Secretaria")
def obter_estatisticas():
    """Retorna contadores para os cartões de indicadores do painel."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM postes;")
    total_postes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM postes WHERE tipo_luminaria = 'LED';")
    total_led = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM postes WHERE status IN ('chamado_aberto', 'urgente');")
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

# ==========================================
# ARQUIVOS ESTÁTICOS DO FRONTEND
# ==========================================
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
