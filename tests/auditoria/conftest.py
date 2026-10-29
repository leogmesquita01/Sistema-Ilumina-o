"""Fixtures da suíte da auditoria (out/2026): modo Supabase com cliente FALSO, sem rede.

O ``banco_local`` (SQLite temporário) vem do ``tests/conftest.py``.
"""
import pytest

from tests.auditoria.fake_supabase import FakeSupabase


def pytest_configure(config):
    config.addinivalue_line("markers", "defeito(id): teste que guarda/revela o defeito indicado")


@pytest.fixture(autouse=True)
def _sem_cliente_ao_final():
    yield
    from app.database import conexao

    conexao.definir_cliente_sessao(None)


@pytest.fixture
def supabase_fake(monkeypatch):
    """Liga o modo Supabase com um cliente FALSO registrado na sessão (sem rede)."""
    from app.database import conexao
    from app.dashboard import sessao

    monkeypatch.setenv("ILUMINA_MODO_LOCAL", "0")
    monkeypatch.setenv("SUPABASE_URL", "https://exemplo.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "sb_publishable_teste")
    fake = FakeSupabase()
    monkeypatch.setattr(sessao, "criar_cliente_supabase", lambda: fake)
    conexao.definir_cliente_sessao(fake)
    yield fake
    conexao.definir_cliente_sessao(None)


# Defeitos da auditoria AINDA NÃO corrigidos. Os testes continuam rodando como
# xfail estrito: quando a correção entra, o teste passa a "XPASS" e a suíte
# falha — sinal para tirar o nome daqui. Ver auditoria/relatorio-auditoria-2026-10-28.md.
PENDENTES = {
    "test_qa019_ler_potencia_milhar_pt_br": "AUD-12 potência '1.000'",
    "test_qa020_xls_anunciado_mas_sem_xlrd": "AUD-12 .xls sem xlrd",
    "test_qa031_localizacao_pendente_nan_e_fora_da_faixa": "AUD-22 NaN/fora da faixa",
    "test_qa037_paginacao_max_rows_menor_que_pagina": "AUD-23 paginação",
    "test_qa042_cache_args_nao_hashable": "AUD-26 chave do cache",
    "test_qa057_falha_ao_ler_perfil_nao_deixa_sessao_meio_aberta": "AUD-10 login",
    "test_qa058_cache_global_entre_sessoes": "AUD-07 cache entre sessões",
    "test_qa066_import_supabase_falha_no_meio_nao_e_atomica": "AUD-05 importação parcial",
    "test_qa072_criar_os_sem_protocolo_nao_deixa_os_orfa": "AUD-05 O.S. órfã",
    "test_qa075_concluir_duas_vezes_update_filtra_status": "AUD-05 conclusão dupla",
    "test_qa076_update_sem_linha_afetada_e_silencioso": "AUD-13 UPDATE silencioso",
    "test_qa079_criar_os_falha_ao_recalcular_status": "AUD-05 status do poste",
    "test_qa081_listar_postes_or_caracteres_especiais": "AUD-20 curingas na busca",
    "test_qa155_jwt_expirado_no_modo_local_nao_entra_em_laco": "AUD-10 laço de rerun",
    "test_qa157_navegar_reparo_supabase_sem_permissao_insert_mostra_erro_amigavel": "AUD-10 mensagem de erro",
    "test_qa159_falha_de_rede_no_login_vira_traceback": "AUD-10 login",
    "test_qa160_mapa_busca_ficha_e_ir_para_reparo": "AUD-11 ficha x busca",
}


def pytest_collection_modifyitems(items):
    for item in items:
        motivo = PENDENTES.get(getattr(item, "originalname", item.name))
        if motivo and not item.name.endswith("[a.b]"):  # o ponto já é tratado corretamente
            item.add_marker(pytest.mark.xfail(reason=f"pendente: {motivo}", strict=True))
