"""Paginação de consultas PostgREST.

O Supabase responde no máximo ``db-max-rows`` linhas por requisição (1.000 por
padrão) e **não sinaliza** o corte: a resposta vem com menos linhas e parece
completa. Consultas sem ``range()`` explícito recebem só a primeira página.

Com o inventário real da COSERN (milhares de postes), isso fazia o painel
mostrar "1.000 postes", a taxa de LED ser calculada sobre uma amostra e o mapa
esconder o resto do município.
"""
from typing import Any, Callable, Dict, List

TAMANHO_PAGINA = 1000

# Guarda-corpo: evita laço infinito se o servidor ignorar o range.
MAXIMO_PAGINAS = 500


def buscar_todas_paginas(
    criar_consulta: Callable[[], Any],
    tamanho: int = TAMANHO_PAGINA,
) -> List[Dict[str, Any]]:
    """Executa ``criar_consulta()` em páginas até esgotar o resultado.

    Recebe uma **fábrica** de consulta (não uma consulta pronta) porque os
    builders do PostgREST são mutáveis: reutilizar o mesmo objeto entre páginas
    reaplicaria o ``range`` anterior.

    >>> buscar_todas_paginas(lambda: sb.table("postes").select("*").order("id"))
    """
    registros: List[Dict[str, Any]] = []
    inicio = 0

    for _ in range(MAXIMO_PAGINAS):
        fim = inicio + tamanho - 1
        resposta = criar_consulta().range(inicio, fim).execute()
        lote = resposta.data or []
        registros.extend(lote)

        if len(lote) < tamanho:
            return registros

        inicio += tamanho

    raise RuntimeError(
        f"Paginação interrompida após {MAXIMO_PAGINAS} páginas "
        f"({len(registros)} registros). Verifique os filtros da consulta."
    )
