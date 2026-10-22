"""Conexão com o Supabase (nuvem) e fallback SQLite local.

O projeto usa **duas** chaves, com papéis diferentes no banco:

* ``obter_supabase()``      -> chave PUBLICÁVEL (``sb_publishable_...``), que o
  Postgres trata como o papel ``anon``. É a chave de **leitura**. Com Row Level
  Security ligado, ela só enxerga o que as policies de SELECT permitirem.
* ``obter_supabase_admin()`` -> chave SECRETA (``sb_secret_...``), que o Postgres
  trata como ``service_role``. É a chave de **escrita** (insert/update/delete) e
  ignora o RLS. Por isso ela nunca pode ir para o código, para o navegador ou para
  o repositório: fica apenas no ``.env`` (local) ou em ``st.secrets`` (Streamlit
  Cloud).

As chaves vêm de ``st.secrets`` quando o app roda no Streamlit Cloud e de variáveis
de ambiente/``.env`` no desenvolvimento local. Não há mais chave fixa no código.
"""
import os
import sqlite3
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "postes_boasaude.db"

# URL não é segredo (aparece em toda requisição), então pode ter um padrão.
DEFAULT_SUPABASE_URL = "https://mizjurmvnjovmpcnferf.supabase.co"

_supabase_client = None
_supabase_admin = None
_aviso_admin_emitido = False


def _valor_config(nome: str, padrao: Optional[str] = None) -> Optional[str]:
    """Lê um valor de ``st.secrets`` (nuvem) ou do ambiente/``.env`` (local).

    ``st.secrets`` tem prioridade para que o deploy no Streamlit Cloud não caia no
    ``.env`` por acidente. Fora do runtime do Streamlit o acesso a ``st.secrets``
    levanta exceção e o código simplesmente segue para o ambiente.
    """
    try:
        import streamlit as st

        if nome in st.secrets:
            valor = st.secrets[nome]
            if valor:
                return str(valor).strip()
    except Exception:
        pass

    valor = os.getenv(nome)
    return valor.strip() if valor else padrao


def obter_supabase():
    """Cliente com a chave publicável: usar para LEITURAS."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = _valor_config("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    chave = _valor_config("SUPABASE_KEY")

    if not url or not chave:
        return None

    try:
        from supabase import create_client

        _supabase_client = create_client(url, chave)
        return _supabase_client
    except Exception:
        return None


def obter_supabase_admin():
    """Cliente com a chave secreta: usar para ESCRITAS (insert/update/delete).

    Se ``SUPABASE_SECRET_KEY`` não estiver configurada, devolve o cliente publicável
    (compatibilidade com ambientes ainda não migrados). Nesse caso, depois de ligar
    o RLS, as gravações passam a falhar com erro de permissão — falha explícita é
    melhor do que manter a tabela aberta para qualquer um.
    """
    global _supabase_admin, _aviso_admin_emitido
    if _supabase_admin is not None:
        return _supabase_admin

    url = _valor_config("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    chave = _valor_config("SUPABASE_SECRET_KEY")

    if not chave:
        if not _aviso_admin_emitido:
            _aviso_admin_emitido = True
            print(
                "[conexao] SUPABASE_SECRET_KEY ausente: as escritas usarão a chave "
                "publicável. Configure a chave secreta no .env ou em st.secrets."
            )
        return obter_supabase()

    try:
        from supabase import create_client

        _supabase_admin = create_client(url, chave)
        return _supabase_admin
    except Exception:
        return obter_supabase()


def obter_conexao() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_banco():
    conn = obter_conexao()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
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
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_postes_codigo ON postes(codigo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_postes_status ON postes(status);")

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
