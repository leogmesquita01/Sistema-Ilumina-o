"""Login com Supabase Auth e sessão do usuário no Streamlit.

Cada pessoa logada ganha o próprio cliente Supabase (guardado em
``st.session_state``). O token dela vai em toda consulta, e o RLS do banco
(migração 002) só libera quem tem perfil ativo em ``public.perfis``.

Limitação conhecida: recarregar a página (F5) apaga o ``st.session_state`` e pede
login de novo.
"""
from typing import Optional

import streamlit as st

from app.database.conexao import criar_cliente_supabase, definir_cliente_sessao, modo_local

_CHAVE = "usuario_logado"
_USUARIO_LOCAL = {"cliente": None, "email": "", "nome": "Modo local", "papel": "admin"}


def usuario_atual() -> Optional[dict]:
    if modo_local():
        return _USUARIO_LOCAL
    return st.session_state.get(_CHAVE)


def preparar_sessao() -> bool:
    """Registra o cliente do usuário para esta execução. False = precisa de login."""
    usuario = usuario_atual()
    if usuario is None:
        definir_cliente_sessao(None)
        return False
    definir_cliente_sessao(usuario["cliente"])
    return True


def entrar(email: str, senha: str) -> Optional[str]:
    """Faz login. Devolve ``None`` em caso de sucesso ou a mensagem de erro."""
    email = (email or "").strip().lower()
    if not email or not senha:
        return "Informe e-mail e senha."

    cliente = criar_cliente_supabase()
    try:
        resposta = cliente.auth.sign_in_with_password({"email": email, "password": senha})
    except Exception as erro:
        texto = str(erro).lower()
        if "invalid" in texto or "credentials" in texto:
            return "E-mail ou senha incorretos."
        if "not confirmed" in texto:
            return "E-mail ainda não confirmado. Peça ao administrador para confirmar a conta."
        return f"Não foi possível entrar agora: {erro}"

    usuario = resposta.user
    definir_cliente_sessao(cliente)
    perfil = (
        cliente.table("perfis").select("nome, papel, ativo").eq("id", usuario.id).limit(1).execute().data
    )
    if not perfil or not perfil[0].get("ativo"):
        try:
            cliente.auth.sign_out()
        except Exception:
            pass
        definir_cliente_sessao(None)
        return "Seu usuário ainda não foi liberado no sistema. Fale com o administrador."

    st.session_state[_CHAVE] = {
        "cliente": cliente,
        "email": usuario.email or email,
        "nome": (perfil[0].get("nome") or "").strip() or email.split("@")[0],
        "papel": perfil[0].get("papel") or "operador",
    }
    return None


def sair(mensagem: Optional[str] = None) -> None:
    usuario = st.session_state.pop(_CHAVE, None)
    if usuario and usuario.get("cliente") is not None:
        try:
            usuario["cliente"].auth.sign_out()
        except Exception:
            pass
    definir_cliente_sessao(None)
    if mensagem:
        st.session_state["aviso_login"] = mensagem


def iniciais(nome: str) -> str:
    partes = [p for p in (nome or "").split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()
