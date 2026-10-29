"""Leitura de planilhas de postes (Excel/CSV) e gravação em lote.

Regras de atualização (upsert por código):
* Poste **novo**: entra com os dados da planilha; colunas ausentes ficam com o
  padrão do banco; status "normal".
* Poste **existente**: só as colunas presentes na planilha são atualizadas.
  O **status nunca é tocado** (reimportar não fecha chamados) e as
  **coordenadas só mudam se a planilha trouxer uma coordenada válida** (não
  apaga a localização marcada no escritório).
"""
import io
import math
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from app.cache import limpar_cache
from app.constantes import BRACOS, ESTRUTURAS, LUMINARIAS
from app.database.conexao import modo_local, obter_conexao, obter_supabase
from app.database.paginacao import buscar_todas_paginas

# Ordem importa: campos mais específicos primeiro. Assim "tipo_poste" é
# reconhecido antes de "codigo" tentar usar o sinônimo "poste".
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "tipo_luminaria": ["tipo_luminaria", "luminaria", "lampada", "tipo_lampada", "modelo_lampada"],
    "tipo_poste": ["tipo_poste", "estrutura", "tipo_estrutura", "material_poste"],
    "tipo_braco": ["tipo_braco", "braco", "suporte", "tam_braco"],
    "referencia": ["referencia", "ponto_referencia", "ref", "compl", "complemento"],
    "potencia": ["potencia", "potencia_w", "potencia_watts", "watts", "pot", "w"],
    "latitude": ["latitude", "lat", "lat_y", "coord_y", "y"],
    "longitude": ["longitude", "long", "lng", "lon", "coord_x", "x"],
    # Sem "end": o Kobo exporta uma coluna "end" (hora de fim do formulário).
    "logradouro": ["logradouro", "rua", "endereco", "nome_rua", "logr", "via"],
    "bairro": ["bairro", "comunidade", "localidade", "distrito", "zona", "setor"],
    "observacoes": ["observacoes", "observacao", "obs"],
    "codigo": ["codigo", "codigo_poste", "plaqueta", "barramento", "id_poste", "num_poste",
               "etiqueta", "ponnot", "poste", "cod", "ponto"],
}

# Sinônimos curtos demais para busca parcial ("x" casaria com qualquer coisa).
_TAMANHO_MINIMO_PARCIAL = 4

# Valores usados só para postes NOVOS quando a célula está vazia.
_PADROES_TEXTO = {
    "logradouro": "Não informado",
    "bairro": "Centro",
    "referencia": "",
    "tipo_luminaria": "LED",
    "tipo_poste": "Concreto Duplo T",
    "tipo_braco": "Braço Médio 2m",
    "observacoes": "",
}
_POTENCIA_PADRAO = 100
_CAMPOS_TEXTO = list(_PADROES_TEXTO)


def normalizar_nome_coluna(nome: Any) -> str:
    """'Código do Poste ' -> 'codigo_do_poste'."""
    texto = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    texto = texto.strip().lower()
    for separador in (" ", "-", ".", "/"):
        texto = texto.replace(separador, "_")
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto.strip("_")


def identify_columns(df_columns: List[Any]) -> Dict[str, Any]:
    """Mapeia campo do sistema -> coluna original da planilha.

    1ª passada: nome exato (normalizado). 2ª passada: o sinônimo aparece dentro do
    nome da coluna — só para sinônimos com 4+ letras. Uma coluna nunca é usada
    para dois campos.
    """
    normalizadas = [(normalizar_nome_coluna(c), c) for c in df_columns]
    mapping: Dict[str, Any] = {}
    usadas: set = set()

    def procurar(campo: str, parcial: bool) -> None:
        if campo in mapping:
            return
        for sinonimo in COLUMN_SYNONYMS[campo]:
            if parcial and len(sinonimo) < _TAMANHO_MINIMO_PARCIAL:
                continue
            for norm, original in normalizadas:
                if original in usadas:
                    continue
                if norm == sinonimo or (parcial and sinonimo in norm):
                    mapping[campo] = original
                    usadas.add(original)
                    return

    for campo in COLUMN_SYNONYMS:
        procurar(campo, parcial=False)
    for campo in COLUMN_SYNONYMS:
        procurar(campo, parcial=True)

    return mapping


def _chave_opcao(texto: str) -> str:
    """'Vapor de Sódio' e 'vapor_de_sodio' viram a mesma chave."""
    return normalizar_nome_coluna(texto).replace("_", "")


# Campos de lista: o valor da planilha é trocado pela opção oficial do sistema
# quando bate (ex.: o Kobo exportando "vapor_de_sodio" vira "Vapor de Sódio").
_OPCOES_OFICIAIS = {
    "tipo_luminaria": {_chave_opcao(o): o for o in LUMINARIAS},
    "tipo_poste": {_chave_opcao(o): o for o in ESTRUTURAS},
    "tipo_braco": {_chave_opcao(o): o for o in BRACOS},
}


def canonizar_opcao(campo: str, valor: Optional[str]) -> Optional[str]:
    if valor is None or campo not in _OPCOES_OFICIAIS:
        return valor
    return _OPCOES_OFICIAIS[campo].get(_chave_opcao(valor), valor)


def _vazio(valor: Any) -> bool:
    if valor is None:
        return True
    try:
        return bool(pd.isna(valor))
    except (TypeError, ValueError):
        return False


def limpar_codigo(valor: Any) -> Optional[str]:
    """Código como texto. Excel transforma 1001 em 1001.0 — isso é desfeito."""
    if _vazio(valor):
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    texto = str(valor).strip()
    return texto or None


def clean_coordinate(val: Any) -> float:
    if _vazio(val):
        raise ValueError("Coordenada vazia")
    if isinstance(val, (int, float)):
        numero = float(val)
    else:
        numero = float(str(val).strip().replace(",", "."))
    if math.isnan(numero) or math.isinf(numero):
        raise ValueError("Coordenada inválida")
    return numero


def ler_coordenadas(lat_bruta: Any, lng_bruta: Any) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Devolve (lat, lng, aviso). Coordenada ausente ou inválida -> (None, None)."""
    if _vazio(lat_bruta) and _vazio(lng_bruta):
        return None, None, None
    try:
        lat = clean_coordinate(lat_bruta)
        lng = clean_coordinate(lng_bruta)
    except (TypeError, ValueError):
        return None, None, "coordenada ilegível, ignorada"
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None, "coordenada fora da faixa válida, ignorada"
    if lat == 0 and lng == 0:
        return None, None, "coordenada 0,0 ignorada"
    return lat, lng, None


def ler_potencia(valor: Any) -> Optional[int]:
    if _vazio(valor):
        return None
    texto = str(valor).upper().replace("W", "").replace(",", ".").strip()
    try:
        return int(float(texto))
    except ValueError:
        return None


def _detectar_separador(texto: str) -> str:
    """Separador pela 1ª linha. O detector automático do pandas erra em CSV de
    uma coluna só (chegou a usar a letra "o" de "codigo" como separador)."""
    cabecalho = texto.splitlines()[0] if texto else ""
    contagens = {sep: cabecalho.count(sep) for sep in (";", ",", "\t", "|")}
    melhor = max(contagens, key=contagens.get)
    return melhor if contagens[melhor] > 0 else ","


def _ler_planilha(file_bytes: bytes, filename: str) -> pd.DataFrame:
    nome = filename.lower()
    if nome.endswith(".csv"):
        try:
            texto = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = file_bytes.decode("latin-1")
        return pd.read_csv(io.StringIO(texto), sep=_detectar_separador(texto), dtype=str)
    if nome.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    raise ValueError("Formato não suportado. Envie um arquivo Excel (.xlsx, .xls) ou CSV.")


def preparar_registros(df: pd.DataFrame, col_map: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma a planilha em registros prontos para gravar (sem tocar no banco)."""
    campos_texto = [c for c in _CAMPOS_TEXTO if c in col_map]
    tem_potencia = "potencia" in col_map
    tem_coordenadas = "latitude" in col_map and "longitude" in col_map

    por_codigo: Dict[str, Dict[str, Any]] = {}
    avisos: List[str] = []
    ignoradas = 0
    duplicados = 0

    for posicao, (_, row) in enumerate(df.iterrows()):
        linha = posicao + 2  # cabeçalho é a linha 1
        codigo = limpar_codigo(row[col_map["codigo"]])
        if not codigo:
            ignoradas += 1
            continue

        registro: Dict[str, Any] = {"codigo": codigo}
        for campo in campos_texto:
            valor = row[col_map[campo]]
            registro[campo] = None if _vazio(valor) else canonizar_opcao(campo, str(valor).strip())
        if tem_potencia:
            registro["potencia"] = ler_potencia(row[col_map["potencia"]])

        registro["latitude"] = registro["longitude"] = None
        if tem_coordenadas:
            lat, lng, aviso = ler_coordenadas(row[col_map["latitude"]], row[col_map["longitude"]])
            registro["latitude"], registro["longitude"] = lat, lng
            if aviso and len(avisos) < 8:
                avisos.append(f"Linha {linha} ({codigo}): {aviso}")

        chave = codigo.casefold()  # "P-01" e "p-01" são o mesmo poste
        if chave in por_codigo:
            duplicados += 1
            if len(avisos) < 8:
                avisos.append(f"Linha {linha}: código {codigo} repetido — vale a última ocorrência")
        por_codigo[chave] = registro

    return {
        "registros": list(por_codigo.values()),
        "campos_texto": campos_texto,
        "tem_potencia": tem_potencia,
        "ignoradas": ignoradas,
        "duplicados": duplicados,
        "avisos": avisos,
    }


def _completar_novo(registro: Dict[str, Any]) -> Dict[str, Any]:
    """Preenche padrões em células vazias — só para postes que ainda não existem."""
    completo = dict(registro)
    for campo, padrao in _PADROES_TEXTO.items():
        if campo in completo and completo[campo] is None:
            completo[campo] = padrao
    if "potencia" in completo and completo["potencia"] is None:
        completo["potencia"] = _POTENCIA_PADRAO
    return completo


def _mesclar_existente(registro: Dict[str, Any]) -> Dict[str, Any]:
    """Para poste existente: célula vazia não apaga o que já está no banco."""
    return {k: v for k, v in registro.items() if v is not None or k in ("latitude", "longitude")}


def ajustar_para_codigos_existentes(registros: List[Dict[str, Any]], existentes: List[str]) -> int:
    """Troca o código da planilha pela grafia que já está no banco ("p-01" → "P-01").

    O UNIQUE do banco diferencia maiúsculas; sem isso, reimportar com outra caixa
    criava um segundo poste. Devolve quantos códigos foram ajustados.
    """
    canonico = {c.casefold(): c for c in existentes}
    ajustados = 0
    for r in registros:
        oficial = canonico.get(r["codigo"].casefold())
        if oficial is not None and oficial != r["codigo"]:
            r["codigo"] = oficial
            ajustados += 1
    return ajustados


def _codigos_existentes() -> List[str]:
    if modo_local():
        conn = obter_conexao()
        try:
            return [r["codigo"] for r in conn.execute("SELECT codigo FROM postes;")]
        finally:
            conn.close()
    sb = obter_supabase()
    linhas = buscar_todas_paginas(lambda: sb.table("postes").select("codigo").order("id"))
    return [r["codigo"] for r in linhas]


def _gravar_supabase(registros: List[Dict[str, Any]], existentes: set) -> None:
    sb = obter_supabase()

    # O PostgREST grava em lote só as colunas presentes no PRIMEIRO objeto. Por
    # isso os lotes são agrupados por conjunto de colunas.
    grupos: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
    for r in registros:
        if r["codigo"] in existentes:
            dados = _mesclar_existente(r)
            if dados.get("latitude") is None:
                dados.pop("latitude", None)
                dados.pop("longitude", None)
        else:
            dados = _completar_novo(r)
            dados["status"] = "normal"
        grupos.setdefault(tuple(sorted(dados)), []).append(dados)

    for lote in grupos.values():
        for i in range(0, len(lote), 500):
            sb.table("postes").upsert(lote[i:i + 500], on_conflict="codigo").execute()


def _gravar_sqlite(registros: List[Dict[str, Any]], campos_texto: List[str], tem_potencia: bool) -> None:
    conn = obter_conexao()
    try:
        colunas = ["codigo", *campos_texto, *(["potencia"] if tem_potencia else []), "latitude", "longitude"]
        atualizacoes = [f"{c} = COALESCE(excluded.{c}, postes.{c})" for c in colunas if c != "codigo"]
        sql = (
            f"INSERT INTO postes ({', '.join(colunas)}, status) "
            f"VALUES ({', '.join('?' for _ in colunas)}, 'normal') "
            f"ON CONFLICT(codigo) DO UPDATE SET {', '.join(atualizacoes)}, "
            f"data_atualizacao = CURRENT_TIMESTAMP;"
        )
        for r in registros:
            novo = _completar_novo(r)
            # Para quem já existe, o COALESCE ignora o padrão e mantém o valor atual
            # só quando a célula veio vazia. Por isso passamos o valor bruto (None)
            # nas células vazias e deixamos o banco decidir.
            existe = conn.execute("SELECT 1 FROM postes WHERE codigo = ?;", (r["codigo"],)).fetchone()
            valores = r if existe else novo
            conn.execute(sql, tuple(valores.get(c) for c in colunas))
        conn.commit()
    finally:
        conn.close()


def import_poles_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    df = _ler_planilha(file_bytes, filename)
    if df.empty:
        raise ValueError("O arquivo enviado está vazio.")

    col_map = identify_columns(list(df.columns))
    if "codigo" not in col_map:
        raise ValueError(
            "Não foi possível identificar a coluna obrigatória de Código/Plaqueta. "
            f"Colunas encontradas: {list(df.columns)}"
        )

    preparo = preparar_registros(df, col_map)
    registros = preparo["registros"]
    ajustados = 0

    if registros:
        existentes = _codigos_existentes()
        ajustados = ajustar_para_codigos_existentes(registros, existentes)
        if modo_local():
            _gravar_sqlite(registros, preparo["campos_texto"], preparo["tem_potencia"])
        else:
            _gravar_supabase(registros, set(existentes))
        limpar_cache()

    return {
        "sucesso": True,
        "total_linhas": len(df),
        "importados": len(registros),
        "erros": preparo["ignoradas"],
        "duplicados": preparo["duplicados"],
        "codigos_ajustados": ajustados,
        "detalhes_erros": preparo["avisos"],
        "colunas_identificadas": {k: str(v) for k, v in col_map.items()},
    }
