import sqlite3
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "postes_boasaude.db"

DEFAULT_SUPABASE_URL = "https://mizjurmvnjovmpcnferf.supabase.co"
DEFAULT_SUPABASE_KEY = "sb_publishable_2U9j0LN5usYKCMI31-hslA_bfGsBU3B"

_supabase_client = None


def obter_supabase():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    key = os.getenv("SUPABASE_KEY", DEFAULT_SUPABASE_KEY)

    try:
        import streamlit as st
        if not url and "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        if not key and "SUPABASE_KEY" in st.secrets:
            key = st.secrets["SUPABASE_KEY"]
    except Exception:
        pass

    if url and key:
        try:
            from supabase import create_client
            _supabase_client = create_client(url, key)
            return _supabase_client
        except Exception:
            return None
    return None


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
