"""Consultas, indicadores e cadastro de postes.

Cada função tem dois caminhos: Supabase (padrão) e SQLite (modo local). Não há
mais ``try/except`` que troca de banco em silêncio: se o Supabase falhar, a
exceção sobe e a tela mostra o erro.
"""
import datetime
from typing import Any, Dict, List, Optional

from app.cache import cache_ttl, limpar_cache
from app.constantes import CENTRO_MUNICIPIO, STATUS_EM_ALERTA, STATUS_NORMAL
from app.database.conexao import modo_local, obter_conexao, obter_supabase
from app.database.paginacao import buscar_todas_paginas
from app.erros import NadaGravado

# Mantido por compatibilidade com as telas: é o centro do município, usado para
# centralizar mapas. Não é mais gravado como coordenada de poste.
COORDENADA_PADRAO = CENTRO_MUNICIPIO


def _agora_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def localizacao_pendente(poste: Dict[str, Any]) -> bool:
    """True quando o poste não tem coordenada confiável.

    Hoje, poste sem localização tem latitude/longitude ``NULL``. A coordenada do
    centro também conta como pendente: versões antigas gravavam esse ponto fixo
    em todo poste novo (a migração 002 converte esses casos para NULL).
    """
    lat, lng = poste.get("latitude"), poste.get("longitude")
    if lat is None or lng is None:
        return True
    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        return True
    # NaN e valores fora da faixa (dado corrompido) não são coordenada confiável.
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return True
    arredondado = (round(lat, 4), round(lng, 4))
    return arredondado == (round(CENTRO_MUNICIPIO[0], 4), round(CENTRO_MUNICIPIO[1], 4))


@cache_ttl()
def obter_resumo_indicadores() -> Dict[str, Any]:
    """Indicadores do painel, contados no banco (``count=exact``)."""
    if not modo_local():
        sb = obter_supabase()

        def contar(tabela: str, aplicar=None) -> int:
            consulta = sb.table(tabela).select("id", count="exact").limit(1)
            if aplicar:
                consulta = aplicar(consulta)
            return consulta.execute().count or 0

        total_postes = contar("postes")
        # "LED", "LED 100W", "led"... todos contam como LED.
        total_led = contar("postes", lambda c: c.ilike("tipo_luminaria", "%LED%"))
        total_chamados = contar("postes", lambda c: c.in_("status", list(STATUS_EM_ALERTA)))
        os_abertas = contar("ordens_servico", lambda c: c.eq("status", "aberta"))
        os_concluidas = contar("ordens_servico", lambda c: c.eq("status", "concluida"))
    else:
        conn = obter_conexao()
        cursor = conn.cursor()

        def um(sql: str, params: tuple = ()) -> int:
            return cursor.execute(sql, params).fetchone()[0]

        marcadores = ",".join("?" for _ in STATUS_EM_ALERTA)
        total_postes = um("SELECT COUNT(*) FROM postes;")
        total_led = um("SELECT COUNT(*) FROM postes WHERE upper(tipo_luminaria) LIKE '%LED%';")
        total_chamados = um(f"SELECT COUNT(*) FROM postes WHERE status IN ({marcadores});", STATUS_EM_ALERTA)
        os_abertas = um("SELECT COUNT(*) FROM ordens_servico WHERE status = 'aberta';")
        os_concluidas = um("SELECT COUNT(*) FROM ordens_servico WHERE status = 'concluida';")
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


def _escapar_like(texto: str) -> str:
    """'%' e '_' do usuário são texto, não curinga do LIKE (ex.: código "P_01")."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _termo_literal_postgrest(texto: str) -> str:
    """Termo de busca seguro dentro de ``or_()`` do PostgREST.

    Vírgula, parênteses e aspas quebrariam a sintaxe do filtro (erro 400); o
    ``*`` vira curinga no PostgREST. Esses viram espaço; ``%``/``_`` são escapados.
    """
    for caractere in ',()"*':
        texto = texto.replace(caractere, " ")
    return _escapar_like(texto)


@cache_ttl()
def _listar_postes_cache(filtro_status: str, termo_busca: str) -> List[Dict[str, Any]]:
    if not modo_local():
        sb = obter_supabase()

        def criar_consulta():
            consulta = sb.table("postes").select("*").order("id", desc=True)
            if filtro_status and filtro_status != "Todos":
                consulta = consulta.eq("status", filtro_status)
            if termo_busca:
                t = _termo_literal_postgrest(termo_busca)
                consulta = consulta.or_(
                    f"codigo.ilike.%{t}%,logradouro.ilike.%{t}%,bairro.ilike.%{t}%"
                )
            return consulta

        return buscar_todas_paginas(criar_consulta)

    conn = obter_conexao()
    cursor = conn.cursor()

    query = "SELECT * FROM postes WHERE 1=1"
    params: list = []

    if filtro_status and filtro_status != "Todos":
        query += " AND status = ?"
        params.append(filtro_status)

    if termo_busca:
        termo = f"%{_escapar_like(termo_busca)}%"
        query += (" AND (codigo LIKE ? ESCAPE '\\' OR logradouro LIKE ? ESCAPE '\\'"
                  " OR bairro LIKE ? ESCAPE '\\')")
        params.extend([termo, termo, termo])

    query += " ORDER BY id DESC"
    rows = cursor.execute(query, params).fetchall()
    conn.close()

    return [dict(r) for r in rows]


@cache_ttl()
def obter_poste_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    if not codigo:
        return None
    codigo = codigo.strip()

    if not modo_local():
        sb = obter_supabase()
        # ilike sem curinga = igualdade sem diferenciar maiúsculas. Escapa os
        # curingas do LIKE para "P_01" não casar com "PX01".
        padrao = codigo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        res = sb.table("postes").select("*").ilike("codigo", padrao).limit(10).execute()
        if not res.data:
            return None
        # Bases antigas podem ter "P-01" e "p-01": a grafia exata tem preferência.
        poste = next((r for r in res.data if r["codigo"] == codigo), res.data[0])
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

    conn = obter_conexao()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT * FROM postes WHERE codigo = ? COLLATE NOCASE ORDER BY (codigo = ?) DESC LIMIT 1;",
        (codigo, codigo),
    ).fetchone()
    if not row:
        conn.close()
        return None

    poste = dict(row)
    cursor.execute(
        "SELECT * FROM ordens_servico WHERE codigo_poste = ? ORDER BY id DESC LIMIT 10;",
        (poste["codigo"],),
    )
    poste["historico_os"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return poste


def _coordenada_ou_none(valor) -> Optional[float]:
    if valor is None or valor == "":
        return None
    return float(valor)


class PosteDuplicado(ValueError):
    """Já existe um poste com este código (sem diferenciar maiúsculas)."""

    def __init__(self, codigo_existente: str):
        super().__init__(f"Já existe um poste com o código {codigo_existente}.")
        self.codigo_existente = codigo_existente


def mesmo_codigo(a: Optional[str], b: Optional[str]) -> bool:
    """Códigos de plaqueta valem sem diferenciar maiúsculas: "p-01" é o "P-01"."""
    return (a or "").strip().casefold() == (b or "").strip().casefold()


def cadastrar_poste(dados: Dict[str, Any]) -> bool:
    """Cadastra um poste. Sem coordenada, ele fica como "localização pendente".

    Levanta :class:`PosteDuplicado` se o código já existe com outra caixa
    ("p-01" quando há "P-01"): no banco seriam dois postes diferentes.
    """
    existente = obter_poste_por_codigo(dados["codigo"])
    if existente:
        raise PosteDuplicado(existente["codigo"])

    novo_poste = {
        "codigo": dados["codigo"].strip(),
        "latitude": _coordenada_ou_none(dados.get("latitude")),
        "longitude": _coordenada_ou_none(dados.get("longitude")),
        "logradouro": (dados.get("logradouro") or "").strip() or "Não informado",
        "bairro": (dados.get("bairro") or "").strip() or "Centro",
        "referencia": (dados.get("referencia") or "").strip(),
        "tipo_luminaria": dados.get("tipo_luminaria") or "LED",
        "potencia": int(dados.get("potencia") or 100),
        "tipo_poste": dados.get("tipo_poste") or "Concreto Duplo T",
        "tipo_braco": dados.get("tipo_braco") or "Braço Médio 2m",
        "status": dados.get("status") or STATUS_NORMAL,
        "observacoes": (dados.get("observacoes") or "").strip(),
    }
    if novo_poste["latitude"] is None or novo_poste["longitude"] is None:
        novo_poste["latitude"] = novo_poste["longitude"] = None

    if not modo_local():
        obter_supabase().table("postes").insert(novo_poste).execute()
        limpar_cache()
        return True

    conn = obter_conexao()
    try:
        colunas = ", ".join(novo_poste)
        marcadores = ", ".join("?" for _ in novo_poste)
        conn.execute(f"INSERT INTO postes ({colunas}) VALUES ({marcadores})", tuple(novo_poste.values()))
        conn.commit()
    finally:
        conn.close()
    limpar_cache()
    return True


def codigo_duplicado(erro: Exception) -> bool:
    """Reconhece erro de código repetido no Postgres (23505) e no SQLite."""
    if isinstance(erro, PosteDuplicado):
        return True
    texto = str(erro).lower()
    return "23505" in texto or "duplicate" in texto or "unique constraint" in texto


def _conferir_gravacao(linhas_alteradas: int, codigo: str) -> None:
    """UPDATE que não muda nada (código inexistente, RLS) não pode parecer sucesso."""
    if not linhas_alteradas:
        raise NadaGravado(
            f"Nada foi gravado para o poste {codigo}: ele não foi encontrado ou seu usuário "
            "não tem permissão para alterá-lo."
        )


def atualizar_status_poste(codigo: str, status: str) -> None:
    if not modo_local():
        res = obter_supabase().table("postes").update({
            "status": status,
            "data_atualizacao": _agora_utc_iso(),
        }).eq("codigo", codigo).execute()
        limpar_cache()
        _conferir_gravacao(len(res.data or []), codigo)
        return

    conn = obter_conexao()
    cursor = conn.execute(
        "UPDATE postes SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;",
        (status, codigo),
    )
    conn.commit()
    conn.close()
    limpar_cache()
    _conferir_gravacao(cursor.rowcount, codigo)


def definir_localizacao_poste(codigo: str, latitude: float, longitude: float) -> None:
    """Grava as coordenadas medidas de um poste já cadastrado."""
    lat = float(latitude)
    lng = float(longitude)

    if not modo_local():
        res = obter_supabase().table("postes").update({
            "latitude": lat,
            "longitude": lng,
            "data_atualizacao": _agora_utc_iso(),
        }).eq("codigo", codigo).execute()
        limpar_cache()
        _conferir_gravacao(len(res.data or []), codigo)
        return

    conn = obter_conexao()
    cursor = conn.execute(
        "UPDATE postes SET latitude = ?, longitude = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE codigo = ?;",
        (lat, lng, codigo),
    )
    conn.commit()
    conn.close()
    limpar_cache()
    _conferir_gravacao(cursor.rowcount, codigo)
