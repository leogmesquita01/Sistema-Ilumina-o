"""Fumaça das telas: cada uma renderiza sem exceção no modo local."""
import pytest
from streamlit.testing.v1 import AppTest

from app.servicos.dados_postes import cadastrar_poste
from app.servicos.ordens_service import criar_ordem_servico

from pathlib import Path

APP = str(Path(__file__).resolve().parent.parent / "app" / "dashboard" / "main.py")
TITULOS = {
    "mapa": "Painel da rede",
    "reparo": "Solicitar reparo",
    "ordens": "Ordens de serviço",
    "cadastro": "Cadastrar poste",
    "importar": "Importar planilha",
    "localizar": "Localizar postes",
}
TELAS = list(TITULOS)


@pytest.fixture
def dados():
    cadastrar_poste({"codigo": "P-01", "logradouro": "Rua <b>A</b>", "bairro": "Centro",
                     "latitude": -6.15, "longitude": -35.61})
    cadastrar_poste({"codigo": "P-02"})
    criar_ordem_servico("P-01", "Lâmpada apagada", prioridade="Urgente")


@pytest.mark.parametrize("tela", TELAS)
def test_tela_renderiza(dados, tela):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = tela
    at.run()
    assert not at.exception, at.exception
    assert not at.error, [e.value for e in at.error]
    assert at.session_state["pagina_atual"] == tela
    assert any(TITULOS[tela] in m.value for m in at.markdown)


def test_html_do_banco_e_escapado(dados):
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    html = "".join(m.value for m in at.markdown)
    assert "Rua <b>A</b>" not in html


def test_sem_configuracao_mostra_erro(monkeypatch):
    monkeypatch.setenv("ILUMINA_MODO_LOCAL", "0")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert at.error and "SUPABASE_URL" in at.error[0].value


def test_supabase_sem_login_mostra_tela_de_login(monkeypatch):
    monkeypatch.setenv("ILUMINA_MODO_LOCAL", "0")
    monkeypatch.setenv("SUPABASE_URL", "https://exemplo.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "sb_publishable_teste")
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception
    assert any(b.label == "Entrar" for b in at.button)
    assert len(at.text_input) == 2
