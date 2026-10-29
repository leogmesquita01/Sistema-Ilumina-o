"""Tradução de erros do banco em mensagens para quem usa o sistema.

Antes, qualquer erro virava "Verifique a internet" com o texto técnico cru (do
RLS, da FK...), e um texto contendo "jwt" deslogava o usuário — no modo local,
isso virava um laço de recarregamento. Aqui o erro é classificado pelo código
(SQLSTATE do Postgres / PGRST do PostgREST) e o detalhe completo vai para o log.
"""
import logging
import re
from typing import NamedTuple, Optional

log = logging.getLogger("ilumina")


class NadaGravado(RuntimeError):
    """O banco aceitou o comando, mas nenhuma linha mudou (código inexistente ou RLS)."""


class Mensagem(NamedTuple):
    texto: str
    sessao_expirada: bool = False


_CODIGOS_SESSAO = {"PGRST301", "PGRST302", "PGRST303"}

_POR_CODIGO = {
    "42501": "Seu usuário não tem permissão para esta ação (a conta pode ter sido desativada). "
             "Fale com o administrador.",
    "23503": "O poste informado não existe na base. Atualize a tela e tente de novo.",
    "23505": "Já existe um registro com esse código.",
    "23514": "Um dos valores não é aceito pelo banco (ex.: situação inválida).",
}


def codigo_do_erro(erro: Exception) -> Optional[str]:
    """SQLSTATE/PGRST do erro do PostgREST (atributo ``code`` ou texto ``'code': '...'``)."""
    codigo = getattr(erro, "code", None)
    if codigo:
        return str(codigo)
    achado = re.search(r"""['"]code['"]\s*:\s*['"]([A-Z0-9]+)['"]""", str(erro))
    return achado.group(1) if achado else None


def _falha_de_rede(erro: Exception) -> bool:
    nomes = {c.__name__ for c in type(erro).__mro__}
    return bool(nomes & {"ConnectError", "ConnectTimeout", "ReadTimeout", "TimeoutException",
                         "NetworkError", "RemoteProtocolError", "ConnectionError", "TimeoutError"})


def mensagem_para_usuario(erro: Exception, modo_local: bool = False) -> Mensagem:
    """Mensagem curta para a tela. Registra o erro completo no log."""
    from app.database.conexao import SessaoNecessaria

    codigo = codigo_do_erro(erro)
    detalhe = f"Detalhe técnico: {type(erro).__name__}" + (f" · código {codigo}" if codigo else "")

    if isinstance(erro, SessaoNecessaria):
        return Mensagem("Sua sessão expirou. Entre novamente.", sessao_expirada=not modo_local)
    if not modo_local and (codigo in _CODIGOS_SESSAO or "jwt expired" in str(erro).lower()):
        return Mensagem("Sua sessão expirou. Entre novamente.", sessao_expirada=True)

    log.error("Erro tratado na tela (%s)", detalhe, exc_info=erro)
    if isinstance(erro, NadaGravado):
        return Mensagem(f"{erro}\n\n{detalhe}")
    if codigo in _POR_CODIGO:
        return Mensagem(f"{_POR_CODIGO[codigo]}\n\n{detalhe}")
    if _falha_de_rede(erro):
        return Mensagem("Não foi possível falar com o banco de dados. Verifique a internet e tente de novo.\n\n"
                        f"{detalhe}")
    return Mensagem("Algo deu errado ao processar esta tela. O erro foi registrado para análise; "
                    f"tente de novo e, se continuar, avise o administrador.\n\n{detalhe}")
