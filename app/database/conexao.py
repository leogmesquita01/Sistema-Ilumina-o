"""Conexão com o Supabase (nuvem) ou com o SQLite local (desenvolvimento).

Modos de operação
-----------------
* **Supabase** (padrão): todas as leituras e escritas vão para a nuvem com o
  cliente **da sessão do usuário logado**. O Postgres recebe o token desse
  usuário, e o RLS (``supabase/migrations/002_login.sql``) decide o que ele pode
  fazer. Se o Supabase falhar, o erro **sobe** até a tela — nada de cair em
  silêncio num banco local vazio.
* **Local** (``ILUMINA_MODO_LOCAL=1``): usa só o SQLite em ``data/``. Serve para
  desenvolver e testar sem internet. Não há login nesse modo.

Por que um cliente por sessão
-----------------------------
O ``supabase-py`` guarda o token de quem fez login dentro do próprio cliente. Um
cliente global seria compartilhado por todos os usuários do servidor — o login de
um valeria para todos. Por isso o ``main.py`` cria um cliente por sessão do
Streamlit e o registra aqui a cada execução com :func:`definir_cliente_sessao`.
Os serviços continuam sem importar o Streamlit.

As configurações vêm de ``st.secrets`` (Streamlit Cloud) ou de variáveis de
ambiente/``.env`` (desenvolvimento local).
"""
import contextvars
import os
import sqlite3
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from app.constantes import CENTRO_MUNICIPIO, STATUS_URGENTE, STATUS_URGENTE_LEGADO

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "postes_boasaude.db"


class ErroConfiguracao(RuntimeError):
    """Supabase não configurado e modo local não ligado."""


class SessaoNecessaria(PermissionError):
    """Operação no Supabase sem usuário logado."""


_cliente_sessao: contextvars.ContextVar = contextvars.ContextVar("cliente_supabase_sessao", default=None)
_identidade_sessao: contextvars.ContextVar = contextvars.ContextVar("identidade_sessao", default=None)


def _valor_config(nome: str, padrao: Optional[str] = None) -> Optional[str]:
    """Lê um valor de ``st.secrets`` (nuvem) ou do ambiente/``.env`` (local)."""
    try:
        import streamlit as st

        if nome in st.secrets:
            valor = st.secrets[nome]
            if valor:
                return str(valor).strip()
    except Exception:  # fora do runtime do Streamlit ou sem secrets.toml
        pass

    valor = os.getenv(nome)
    return valor.strip() if valor else padrao


def modo_local() -> bool:
    """True quando o app deve usar só o SQLite (``ILUMINA_MODO_LOCAL=1``)."""
    return (_valor_config("ILUMINA_MODO_LOCAL") or "").lower() in ("1", "true", "sim")


def configuracao_supabase() -> tuple:
    """Devolve ``(url, chave_publicavel)`` ou levanta :class:`ErroConfiguracao`."""
    url = _valor_config("SUPABASE_URL")
    chave = _valor_config("SUPABASE_KEY")
    if not url or not chave:
        raise ErroConfiguracao(
            "SUPABASE_URL e SUPABASE_KEY não configuradas. Preencha o .env (local) ou "
            "Settings → Secrets (Streamlit Cloud). Para testar sem nuvem, use ILUMINA_MODO_LOCAL=1."
        )
    return url, chave


def criar_cliente_supabase():
    """Cria um cliente novo com a chave publicável. Um por sessão de usuário."""
    from supabase import ClientOptions, create_client

    url, chave = configuracao_supabase()
    # auto_refresh_token=False: com True, cada login criava uma thread que renovava
    # o token para sempre — mesmo depois de a aba ser fechada ou recarregada (F5).
    # A renovação agora é feita sob demanda em sessao.preparar_sessao().
    return create_client(url, chave, options=ClientOptions(persist_session=False, auto_refresh_token=False))


def definir_cliente_sessao(cliente, identidade: Optional[str] = None) -> None:
    """Registra o cliente do usuário logado (e quem é ele) para esta execução do script."""
    _cliente_sessao.set(cliente)
    _identidade_sessao.set(identidade if cliente is not None else None)


def identidade_sessao() -> Optional[str]:
    """Quem está consultando — separa o cache por usuário. ``None`` = sem sessão identificada."""
    if modo_local():
        return "modo-local"
    return _identidade_sessao.get()


def obter_supabase():
    """Cliente do usuário logado, usado para leituras **e** escritas.

    Levanta :class:`SessaoNecessaria` se ninguém fez login — com o RLS da
    migração 002, a chave publicável sozinha não lê nem grava nada.
    """
    cliente = _cliente_sessao.get()
    if cliente is None:
        raise SessaoNecessaria("Sessão expirada ou ausente. Faça login novamente.")
    return cliente


def obter_supabase_admin():
    """Cliente com a chave SECRETA (``service_role``), que ignora o RLS.

    **O app não usa esta função.** Ela existe só para scripts de manutenção
    rodados na sua máquina (ex.: carga inicial). Nunca chame isto a partir de uma
    tela: qualquer visitante herdaria o poder de administrador.
    """
    from supabase import create_client

    url = _valor_config("SUPABASE_URL")
    chave = _valor_config("SUPABASE_SECRET_KEY")
    if not url or not chave:
        raise ErroConfiguracao("SUPABASE_SECRET_KEY não configurada.")
    return create_client(url, chave)


# --- SQLite (modo local) -----------------------------------------------------

def obter_conexao() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


_SQL_TABELA_POSTES = """
    CREATE TABLE IF NOT EXISTS {nome} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        latitude REAL,
        longitude REAL,
        logradouro TEXT,
        bairro TEXT,
        referencia TEXT,
        tipo_luminaria TEXT DEFAULT 'LED',
        potencia INTEGER DEFAULT 100,
        tipo_poste TEXT DEFAULT 'Concreto Duplo T',
        tipo_braco TEXT DEFAULT 'Braço Médio 2m',
        status TEXT DEFAULT 'normal',
        observacoes TEXT,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""


def _migrar_coordenadas_opcionais(conn: sqlite3.Connection) -> None:
    """Bancos antigos tinham latitude/longitude NOT NULL. Recria a tabela sem isso.

    O SQLite não faz ``ALTER COLUMN``; o caminho oficial é copiar para uma tabela
    nova. Postes na coordenada padrão do centro passam a ter coordenada NULL.
    """
    colunas = {c["name"]: c for c in conn.execute("PRAGMA table_info(postes);")}
    if not colunas or not colunas["latitude"]["notnull"]:
        return

    conn.execute("PRAGMA foreign_keys = OFF;")
    conn.execute(_SQL_TABELA_POSTES.format(nome="postes_novo"))
    conn.execute("""
        INSERT INTO postes_novo SELECT
            id, codigo, latitude, longitude, logradouro, bairro, referencia,
            tipo_luminaria, potencia, tipo_poste, tipo_braco, status, observacoes, data_atualizacao
        FROM postes;
    """)
    conn.execute("DROP TABLE postes;")
    conn.execute("ALTER TABLE postes_novo RENAME TO postes;")
    conn.execute(
        "UPDATE postes SET latitude = NULL, longitude = NULL "
        "WHERE round(latitude, 4) = ? AND round(longitude, 4) = ?;",
        (round(CENTRO_MUNICIPIO[0], 4), round(CENTRO_MUNICIPIO[1], 4)),
    )
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")


def inicializar_banco():
    """Cria/atualiza o SQLite local. Só faz algo no modo local."""
    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute(_SQL_TABELA_POSTES.format(nome="postes"))
    _migrar_coordenadas_opcionais(conn)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_postes_codigo ON postes(codigo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_postes_status ON postes(status);")
    cursor.execute(
        "UPDATE postes SET status = ? WHERE status = ?;", (STATUS_URGENTE, STATUS_URGENTE_LEGADO)
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo TEXT UNIQUE NOT NULL,
            codigo_poste TEXT NOT NULL,
            defeito TEXT NOT NULL,
            prioridade TEXT DEFAULT 'Normal',
            materiais TEXT,
            solicitante TEXT DEFAULT 'Secretaria de Infraestrutura',
            status TEXT DEFAULT 'aberta',
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_conclusao TIMESTAMP,
            observacoes TEXT,
            FOREIGN KEY (codigo_poste) REFERENCES postes(codigo) ON UPDATE CASCADE
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_os_codigo_poste ON ordens_servico(codigo_poste);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_os_status ON ordens_servico(status);")

    conn.commit()
    conn.close()
