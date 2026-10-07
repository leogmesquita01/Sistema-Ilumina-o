"""
Módulo de Importação de Arquivos da COSERN / ANEEL
Capaz de ler planilhas Excel (.xlsx, .xls) e arquivos CSV, identificar colunas automaticamente
mesmo com nomes variados e salvar os postes no banco SQLite.
"""

import pandas as pd
import io
import json
from typing import Dict, Any, List, Tuple
from app.database.conexao import obter_conexao as get_connection

# Sinônimos comuns de cabeçalhos nas planilhas de concessionárias
COLUMN_SYNONYMS = {
    "codigo": ["codigo", "cod", "plaqueta", "barramento", "id_poste", "poste", "etiqueta", "ponto", "ponnot", "num_poste"],
    "latitude": ["latitude", "lat", "lat_y", "coord_y", "y"],
    "longitude": ["longitude", "long", "lng", "lon", "coord_x", "x"],
    "logradouro": ["logradouro", "rua", "endereco", "end", "nome_rua", "logr", "via"],
    "bairro": ["bairro", "comunidade", "localidade", "distrito", "zona", "setor"],
    "referencia": ["referencia", "ponto_referencia", "ref", "compl", "complemento"],
    "tipo_luminaria": ["tipo_luminaria", "luminaria", "lampada", "tipo_lampada", "modelo_lampada"],
    "potencia": ["potencia", "pot", "watts", "w", "potencia_w"],
    "tipo_poste": ["tipo_poste", "estrutura", "tipo_estrutura", "material_poste"],
    "tipo_braco": ["tipo_braco", "braco", "suporte", "tam_braco"],
}

def clean_coordinate(val: Any) -> float:
    """Limpa e converte strings de coordenadas, tratando vírgulas brasileiras (-6,160 -> -6.160)."""
    if pd.isna(val):
        raise ValueError("Coordenada vazia")
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", ".")
    return float(s)

def identify_columns(df_columns: List[str]) -> Dict[str, str]:
    """Identifica as melhores colunas do dataframe correspondentes ao nosso modelo."""
    mapping = {}
    normalized_cols = {str(col).strip().lower(): col for col in df_columns}
    
    for standard_name, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            # Busca exata ou que contenha a palavra
            matched = None
            for norm_name, original_name in normalized_cols.items():
                if syn == norm_name or syn in norm_name:
                    matched = original_name
                    break
            if matched:
                mapping[standard_name] = matched
                break
                
    return mapping

def import_poles_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Lê o arquivo de planilha (Excel ou CSV) e insere ou atualiza os postes no banco de dados.
    """
    filename_lower = filename.lower()
    
    # 1. Carrega o arquivo com Pandas
    if filename_lower.endswith(".csv"):
        # Tenta detectar separador vírgula ou ponto-e-vírgula
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine="python", encoding="latin-1")
    elif filename_lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError("Formato não suportado. Envie um arquivo Excel (.xlsx, .xls) ou CSV.")

    if df.empty:
        raise ValueError("O arquivo enviado está vazio.")

    # 2. Identifica colunas
    col_map = identify_columns(list(df.columns))

    if "codigo" not in col_map or "latitude" not in col_map or "longitude" not in col_map:
        missing = []
        if "codigo" not in col_map: missing.append("Código/Plaqueta")
        if "latitude" not in col_map: missing.append("Latitude")
        if "longitude" not in col_map: missing.append("Longitude")
        raise ValueError(f"Não foi possível identificar as colunas obrigatórias: {', '.join(missing)}. Colunas encontradas: {list(df.columns)}")

    # 3. Processa e insere registros no SQLite
    conn = get_connection()
    cursor = conn.cursor()
    
    total_linhas = len(df)
    importados = 0
    atualizados = 0
    erros = 0
    detalhes_erros = []

    for idx, row in df.iterrows():
        try:
            raw_code = row[col_map["codigo"]]
            if pd.isna(raw_code):
                continue
            codigo = str(raw_code).strip()

            lat = clean_coordinate(row[col_map["latitude"]])
            lng = clean_coordinate(row[col_map["longitude"]])

            logradouro = str(row[col_map["logradouro"]]).strip() if "logradouro" in col_map and not pd.isna(row[col_map["logradouro"]]) else "Não informado"
            bairro = str(row[col_map["bairro"]]).strip() if "bairro" in col_map and not pd.isna(row[col_map["bairro"]]) else "Centro"
            referencia = str(row[col_map["referencia"]]).strip() if "referencia" in col_map and not pd.isna(row[col_map["referencia"]]) else ""
            
            tipo_luminaria = str(row[col_map["tipo_luminaria"]]).strip() if "tipo_luminaria" in col_map and not pd.isna(row[col_map["tipo_luminaria"]]) else "LED"
            
            # Tratamento de potência numérica
            potencia = 100
            if "potencia" in col_map and not pd.isna(row[col_map["potencia"]]):
                try:
                    potencia = int(float(str(row[col_map["potencia"]]).replace("W", "").strip()))
                except ValueError:
                    potencia = 100

            tipo_poste = str(row[col_map["tipo_poste"]]).strip() if "tipo_poste" in col_map and not pd.isna(row[col_map["tipo_poste"]]) else "Concreto Duplo T"
            tipo_braco = str(row[col_map["tipo_braco"]]).strip() if "tipo_braco" in col_map and not pd.isna(row[col_map["tipo_braco"]]) else "Braço Médio 2m"

            # INSERT OR REPLACE (Atualiza se já existir)
            cursor.execute("""
                INSERT INTO postes (
                    codigo, latitude, longitude, logradouro, bairro, referencia,
                    tipo_luminaria, potencia, tipo_poste, tipo_braco, status, data_atualizacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'normal', CURRENT_TIMESTAMP)
                ON CONFLICT(codigo) DO UPDATE SET
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    logradouro = excluded.logradouro,
                    bairro = excluded.bairro,
                    referencia = excluded.referencia,
                    tipo_luminaria = excluded.tipo_luminaria,
                    potencia = excluded.potencia,
                    tipo_poste = excluded.tipo_poste,
                    tipo_braco = excluded.tipo_braco,
                    data_atualizacao = CURRENT_TIMESTAMP;
            """, (codigo, lat, lng, logradouro, bairro, referencia, tipo_luminaria, potencia, tipo_poste, tipo_braco))

            importados += 1
        except Exception as e:
            erros += 1
            if len(detalhes_erros) < 5:
                detalhes_erros.append(f"Linha {idx + 2}: {str(e)}")

    conn.commit()
    conn.close()

    return {
        "sucesso": True,
        "total_linhas": total_linhas,
        "importados": importados,
        "erros": erros,
        "detalhes_erros": detalhes_erros,
        "colunas_identificadas": col_map
    }
