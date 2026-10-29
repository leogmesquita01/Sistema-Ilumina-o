"""Cache TTL em memória, sem dependência do Streamlit.

Cada usuário tem o próprio cache (a chave inclui quem consulta): o resultado
lido com o token de um usuário nunca é entregue a outro, e sem login não há
cache nenhum.

Motivo: o dashboard é rerenderizado a cada interação e cada tela consulta o
Supabase. Sem cache, abrir o mapa dispara várias consultas por clique. Como o
sistema é de uma única prefeitura e o inventário muda pouco, um cache global com
TTL curto resolve — e :func:`limpar_cache` é chamado depois de cada escrita, para
o usuário ver o próprio cadastro na hora.

Mantido fora do Streamlit de propósito: os módulos de serviço continuam
utilizáveis em scripts e testes fora do runtime do app.
"""
import functools
import threading
import time
from typing import Any, Callable, Dict, Tuple

TTL_PADRAO_SEGUNDOS = 20.0
MAXIMO_ENTRADAS = 256

_lock = threading.Lock()
_entradas: Dict[Tuple[Any, ...], Tuple[float, Any]] = {}


_geracao = 0  # muda a cada limpar_cache(): leitura iniciada antes não é guardada


def _chave(usuario: str, funcao: Callable[..., Any], args: tuple, kwargs: dict) -> Tuple[Any, ...]:
    identidade = (usuario, funcao.__module__, funcao.__qualname__)
    chave = identidade + (args, tuple(sorted(kwargs.items())))
    try:
        hash(chave)
        return chave
    except TypeError:  # argumento não hashable (lista, dict): cai no repr
        return identidade + (repr(args), repr(sorted(kwargs.items())))


def _remover_expirados(agora: float) -> None:
    for chave in [k for k, (expira, _) in _entradas.items() if expira <= agora]:
        _entradas.pop(chave, None)


def cache_ttl(segundos: float = TTL_PADRAO_SEGUNDOS):
    """Decora uma função com cache em memória válido por ``segundos``.

    O valor em cache é compartilhado entre as execuções do mesmo usuário:
    trate o retorno como somente-leitura.
    """

    def decorador(funcao: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(funcao)
        def envoltorio(*args, **kwargs):
            from app.database.conexao import identidade_sessao

            usuario = identidade_sessao()
            if usuario is None:
                # Sem sessão identificada não há cache: a função consulta o banco
                # (e levanta SessaoNecessaria se ninguém fez login).
                return funcao(*args, **kwargs)

            chave = _chave(usuario, funcao, args, kwargs)
            agora = time.monotonic()

            with _lock:
                item = _entradas.get(chave)
                if item is not None and item[0] > agora:
                    return item[1]
                geracao = _geracao

            valor = funcao(*args, **kwargs)

            with _lock:
                if geracao != _geracao:
                    return valor  # houve escrita durante a leitura: não guarda dado velho
                if len(_entradas) >= MAXIMO_ENTRADAS:
                    _remover_expirados(agora)
                    if len(_entradas) >= MAXIMO_ENTRADAS:
                        _entradas.clear()
                _entradas[chave] = (time.monotonic() + segundos, valor)

            return valor

        return envoltorio

    return decorador


def limpar_cache() -> None:
    """Descarta tudo. Chamar depois de qualquer escrita no banco."""
    global _geracao
    with _lock:
        _geracao += 1
        _entradas.clear()
