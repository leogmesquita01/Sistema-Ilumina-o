"""
Gerenciador de Conexão com o Banco de Dados SQLite
"""

import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "postes_boasaude.db"

def obter_conexao() -> sqlite3.Connection:
    """Retorna uma conexão com o banco SQLite."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    """Garante que as tabelas necessárias existam."""
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

if __name__ == "__main__":
    inicializar_banco()
    print("Banco inicializado com sucesso!")
