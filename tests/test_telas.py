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


def test_reparo_exige_escolher_o_poste(dados):
    """Antes vinha o 1º poste da lista já escolhido: dava para abrir O.S. no poste errado."""
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = "reparo"
    at.run()
    assert at.selectbox(key="reparo_poste").value == "— Escolha o poste —"
    next(b for b in at.button if b.label == "Emitir ordem de serviço").click()
    at.run()
    assert any("Escolha o poste" in e.value for e in at.error)


def test_poste_vindo_da_ficha_e_usado_uma_vez(dados):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = "reparo"
    at.session_state["poste_selecionado_os"] = "P-01"
    at.run()
    assert at.selectbox(key="reparo_poste").value.startswith("P-01")
    assert "poste_selecionado_os" not in at.session_state


def test_emitir_os_nao_deixa_reenviar_o_mesmo_formulario(dados):
    from app.servicos.ordens_service import listar_ordens

    antes = len(listar_ordens())
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = "reparo"
    at.session_state["poste_selecionado_os"] = "P-02"
    at.run()
    next(b for b in at.button if b.label == "Emitir ordem de serviço").click()
    at.run()
    assert not at.exception and not at.error
    # depois de emitir só há a confirmação: nenhum botão "Emitir" para um 2º clique
    assert not any(b.label == "Emitir ordem de serviço" for b in at.button)
    assert any("Ordem de serviço emitida" in m.value for m in at.markdown)
    from app.cache import limpar_cache
    limpar_cache()
    assert len(listar_ordens()) == antes + 1
    next(b for b in at.button if b.label == "Emitir outra O.S.").click()
    at.run()
    assert any(b.label == "Emitir ordem de serviço" for b in at.button)


def test_erro_de_permissao_mostra_mensagem_sem_texto_tecnico(dados, monkeypatch):
    import app.dashboard.telas.mapa_postes as tela_mapa

    def bloqueado(*a, **k):
        raise Exception("{'code': '42501', 'message': 'new row violates row-level security policy'}")

    monkeypatch.setattr(tela_mapa, "obter_resumo_indicadores", bloqueado)
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception
    texto = at.error[0].value
    assert "permissão" in texto and "row-level security" not in texto and "42501" in texto


def test_localizacao_de_poste_inexistente_nao_parece_sucesso():
    import pytest
    from app.erros import NadaGravado
    from app.servicos.dados_postes import definir_localizacao_poste

    with pytest.raises(NadaGravado):
        definir_localizacao_poste("NAO-EXISTE", -6.15, -35.6)
