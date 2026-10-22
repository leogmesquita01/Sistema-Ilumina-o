import pandas as pd
import io
from typing import Dict, Any, List
from app.database.conexao import obter_conexao, obter_supabase_admin

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
    if pd.isna(val):
        raise ValueError("Coordenada vazia")
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", ".")
    return float(s)


def identify_columns(df_columns: List[str]) -> Dict[str, str]:
    mapping = {}
    normalized_cols = {str(col).strip().lower(): col for col in df_columns}

    for standard_name, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
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
    filename_lower = filename.lower()

    if filename_lower.endswith(".csv"):
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

    col_map = identify_columns(list(df.columns))

    if "codigo" not in col_map:
        raise ValueError(
            f"Não foi possível identificar a coluna obrigatória de Código/Plaqueta. Colunas encontradas: {list(df.columns)}"
        )

    total_linhas = len(df)
    importados = 0
    erros = 0
    detalhes_erros = []
    lote_postes = []

    for idx, row in df.iterrows():
        try:
            raw_code = row[col_map["codigo"]]
            if pd.isna(raw_code):
                continue
            codigo = str(raw_code).strip()

            lat = -6.1611
            lng = -35.6025
            if "latitude" in col_map and not pd.isna(row[col_map["latitude"]]):
                try:
                    lat = clean_coordinate(row[col_map["latitude"]])
                except Exception:
                    lat = -6.1611
            if "longitude" in col_map and not pd.isna(row[col_map["longitude"]]):
                try:
                    lng = clean_coordinate(row[col_map["longitude"]])
                except Exception:
                    lng = -35.6025

            logradouro = str(row[col_map["logradouro"]]).strip() if "logradouro" in col_map and not pd.isna(row[col_map["logradouro"]]) else "Não informado"
            bairro = str(row[col_map["bairro"]]).strip() if "bairro" in col_map and not pd.isna(row[col_map["bairro"]]) else "Centro"
            referencia = str(row[col_map["referencia"]]).strip() if "referencia" in col_map and not pd.isna(row[col_map["referencia"]]) else ""
            tipo_luminaria = str(row[col_map["tipo_luminaria"]]).strip() if "tipo_luminaria" in col_map and not pd.isna(row[col_map["tipo_luminaria"]]) else "LED"

            potencia = 100
            if "potencia" in col_map and not pd.isna(row[col_map["potencia"]]):
                try:
                    potencia = int(float(str(row[col_map["potencia"]]).replace("W", "").strip()))
                except ValueError:
                    potencia = 100

            tipo_poste = str(row[col_map["tipo_poste"]]).strip() if "tipo_poste" in col_map and not pd.isna(row[col_map["tipo_poste"]]) else "Concreto Duplo T"
            tipo_braco = str(row[col_map["tipo_braco"]]).strip() if "tipo_braco" in col_map and not pd.isna(row[col_map["tipo_braco"]]) else "Braço Médio 2m"

            lote_postes.append({
                "codigo": codigo,
                "latitude": lat,
                "longitude": lng,
                "logradouro": logradouro,
                "bairro": bairro,
                "referencia": referencia,
                "tipo_luminaria": tipo_luminaria,
                "potencia": potencia,
                "tipo_poste": tipo_poste,
                "tipo_braco": tipo_braco,
                "status": "normal",
            })
            importados += 1
        except Exception as e:
            erros += 1
            if len(detalhes_erros) < 5:
                detalhes_erros.append(f"Linha {idx + 2}: {str(e)}")

    sb = obter_supabase_admin()
    if sb and lote_postes:
        tamanho_lote = 500
        for i in range(0, len(lote_postes), tamanho_lote):
            chunk = lote_postes[i:i + tamanho_lote]
            sb.table("postes").upsert(chunk, on_conflict="codigo").execute()
        return {
            "sucesso": True,
            "total_linhas": total_linhas,
            "importados": importados,
            "erros": erros,
            "detalhes_erros": detalhes_erros,
            "colunas_identificadas": col_map,
        }

    conn = obter_conexao()
    cursor = conn.cursor()

    for p in lote_postes:
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
        """, (
            p["codigo"], p["latitude"], p["longitude"], p["logradouro"],
            p["bairro"], p["referencia"], p["tipo_luminaria"], p["potencia"],
            p["tipo_poste"], p["tipo_braco"]
        ))

    conn.commit()
    conn.close()

    return {
        "sucesso": True,
        "total_linhas": total_linhas,
        "importados": importados,
        "erros": erros,
        "detalhes_erros": detalhes_erros,
        "colunas_identificadas": col_map,
    }
