import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


@pytest.fixture(autouse=True)
def banco_local(tmp_path, monkeypatch):
    """Cada teste roda no modo local, com um SQLite novo e cache limpo."""
    monkeypatch.setenv("ILUMINA_MODO_LOCAL", "1")
    from app.cache import limpar_cache
    from app.database import conexao

    monkeypatch.setattr(conexao, "DB_DIR", tmp_path)
    monkeypatch.setattr(conexao, "DB_PATH", tmp_path / "teste.db")
    conexao.inicializar_banco()
    limpar_cache()
    yield tmp_path / "teste.db"
    limpar_cache()
