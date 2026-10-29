"""Área do administrador no modo Supabase, com o cliente FALSO (sem rede)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.erros import NadaGravado
from app.servicos import admin_service as adm

APP = str(Path(__file__).resolve().parents[2] / "app" / "dashboard" / "main.py")

EQUIPE = [
    {"id": "uid-1", "email": "leo@pref.gov.br", "nome": "Leonardo", "papel": "admin", "ativo": True,
     "liberado": True, "criado_em": "2026-10-01T10:00:00+00:00", "ultimo_acesso": "2026-10-29T12:00:00+00:00"},
    {"id": "uid-2", "email": "op@pref.gov.br", "nome": "Operador", "papel": "operador", "ativo": True,
     "liberado": True, "criado_em": "2026-10-02T10:00:00+00:00", "ultimo_acesso": None},
    {"id": "uid-3", "email": "novo@pref.gov.br", "nome": "", "papel": "operador", "ativo": False,
     "liberado": False, "criado_em": "2026-10-28T10:00:00+00:00", "ultimo_acesso": None},
]


@pytest.fixture
def com_equipe(supabase_fake):
    supabase_fake.respostas_rpc["listar_equipe"] = EQUIPE
    supabase_fake.respostas_rpc["liberar_usuario"] = None
    supabase_fake.tabelas["perfis"] = [{k: m[k] for k in ("id", "nome", "papel", "ativo")} for m in EQUIPE[:2]]
    return supabase_fake


def test_listar_equipe_usa_a_funcao_do_banco(com_equipe):
    assert [m["email"] for m in adm.listar_equipe()] == [m["email"] for m in EQUIPE]
    assert com_equipe.rpcs == [("listar_equipe", {})]


def test_atualizar_membro_grava_so_nome_papel_ativo(com_equipe):
    adm.atualizar_membro("uid-2", "  Zé  ", "admin", False)
    payload = com_equipe.chamadas_de("perfis", "update")[0].payload
    assert payload == {"nome": "Zé", "papel": "admin", "ativo": False}


def test_atualizar_membro_barrado_pelo_rls_avisa(com_equipe):
    com_equipe.update_vazio = True
    with pytest.raises(NadaGravado):
        adm.atualizar_membro("uid-2", "Zé", "operador", True)


def test_liberar_usuario_chama_rpc(com_equipe):
    adm.liberar_usuario("uid-3", "Novo", "operador")
    assert com_equipe.rpcs[-1] == ("liberar_usuario", {"p_id": "uid-3", "p_nome": "Novo", "p_papel": "operador"})


def test_papel_invalido_recusado(com_equipe):
    with pytest.raises(adm.AcaoRecusada):
        adm.liberar_usuario("uid-3", "Novo", "dono")


def test_excluir_poste_barrado_pelo_rls_avisa(com_equipe):
    com_equipe.tabelas["postes"] = [{"id": 1, "codigo": "P-01"}]
    com_equipe.update_vazio = True
    with pytest.raises(NadaGravado):
        adm.excluir_poste("P-01")


def test_historico_troca_ids_por_nomes(com_equipe):
    com_equipe.tabelas["historico"] = [
        {"id": 1, "em": "2026-10-29T15:00:00+00:00", "usuario": "uid-1", "tabela": "ordens_servico",
         "acao": "UPDATE", "registro": "OS-2026-0001",
         "antes": {"status": "aberta"}, "depois": {"status": "cancelada"}},
        {"id": 2, "em": "2026-10-29T15:05:00+00:00", "usuario": "uid-1", "tabela": "perfis",
         "acao": "UPDATE", "registro": "uid-2", "antes": {"ativo": True}, "depois": {"ativo": False}},
    ]
    linhas = adm.listar_historico()
    assert [l["Registro"] for l in linhas] == ["Operador", "OS-2026-0001"]  # mais recente primeiro
    assert linhas[1] == {"Quando": "29/10/2026 12:00", "Quem": "Leonardo", "Ação": "Alterou", "Tipo": "O.S.",
                         "Registro": "OS-2026-0001", "O que mudou": "status: aberta → cancelada"}


def _app(fake, papel):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = "admin"
    at.session_state["usuario_logado"] = {"cliente": fake, "email": "leo@pref.gov.br", "nome": "Leonardo", "papel": papel}
    at.run()
    assert not at.exception, at.exception
    return at


def test_tela_admin_mostra_equipe_e_pendentes(com_equipe):
    at = _app(com_equipe, "admin")
    assert not at.error, [e.value for e in at.error]
    assert any("Contas aguardando liberação" in m.value for m in at.markdown)
    assert any(b.label == "Liberar acesso" for b in at.button)


def test_tela_admin_sem_migracao_avisa(com_equipe):
    com_equipe.respostas_rpc["listar_equipe"] = Exception("{'code': 'PGRST202', 'message': 'not found'}")
    at = _app(com_equipe, "admin")
    assert any("005_area_admin.sql" in w.value for w in at.warning)


def test_operador_logado_nao_entra(com_equipe):
    at = _app(com_equipe, "operador")
    assert at.session_state["pagina_atual"] == "mapa"
    assert com_equipe.rpcs == []


# ---- Adicionar membro (Edge Function criar-membro) ---------------------------

def test_criar_membro_chama_a_funcao(com_equipe):
    adm.criar_membro(" Nova@Pref.gov.br ", " Nova ", "operador", "senha-forte-1")
    assert com_equipe.functions.chamadas == [(
        "criar-membro", {"email": "nova@pref.gov.br", "nome": "Nova", "papel": "operador", "senha": "senha-forte-1"},
    )]


@pytest.mark.parametrize("email, nome, senha", [
    ("sem-arroba", "Nova", "senha-forte-1"),
    ("nova@pref.gov.br", "  ", "senha-forte-1"),
    ("nova@pref.gov.br", "Nova", "curta"),
])
def test_criar_membro_valida_antes_de_chamar(com_equipe, email, nome, senha):
    with pytest.raises(adm.AcaoRecusada):
        adm.criar_membro(email, nome, "operador", senha)
    assert com_equipe.functions.chamadas == []


def test_criar_membro_mostra_a_mensagem_da_funcao(com_equipe):
    from supabase_functions.errors import FunctionsHttpError

    com_equipe.functions.respostas["criar-membro"] = FunctionsHttpError("Já existe uma conta com esse e-mail.", 409)
    with pytest.raises(adm.AcaoRecusada, match="Já existe uma conta"):
        adm.criar_membro("leo@pref.gov.br", "Leo", "operador", "senha-forte-1")


def test_criar_membro_sem_funcao_publicada_orienta(com_equipe):
    from supabase_functions.errors import FunctionsHttpError

    com_equipe.functions.respostas["criar-membro"] = FunctionsHttpError("Requested function was not found", 404)
    with pytest.raises(adm.AcaoRecusada, match="não está publicada"):
        adm.criar_membro("nova@pref.gov.br", "Nova", "operador", "senha-forte-1")


def test_tela_cria_membro(com_equipe):
    at = _app(com_equipe, "admin")
    next(t for t in at.text_input if t.label == "E-mail").input("nova@pref.gov.br")
    next(t for t in at.text_input if t.label == "Nome").input("Nova Pessoa")
    next(b for b in at.button if b.label == "Criar conta").click()
    at.run()
    assert not at.exception, at.exception
    assert any("Conta criada para nova@pref.gov.br" in s.value for s in at.success)
    nome, corpo = com_equipe.functions.chamadas[0]
    assert nome == "criar-membro" and corpo["nome"] == "Nova Pessoa" and len(corpo["senha"]) == 10
