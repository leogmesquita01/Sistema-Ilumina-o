"""QA — fluxos de interface com streamlit.testing.v1.AppTest.

Modo local (SQLite) para os fluxos de negócio; modo Supabase com cliente FALSO
para login/logout/erro de sessão. Componentes folium (st_folium/components.html)
não são dirigíveis pelo AppTest: cliques no mapa são simulados via session_state.
"""
import io
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from app.database.conexao import obter_conexao
from app.servicos.dados_postes import cadastrar_poste, obter_poste_por_codigo
from app.servicos.ordens_service import criar_ordem_servico

APP = str(Path(__file__).resolve().parents[2] / "app" / "dashboard" / "main.py")


def _app(pagina="mapa", **estado):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["pagina_atual"] = pagina
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, at.exception
    return at


def _textos(at):
    return " ".join([m.value for m in at.markdown] + [e.value for e in at.success] + [e.value for e in at.error]
                    + [w.value for w in at.warning] + [i.value for i in at.info])


def _contar(sql, params=()):
    conn = obter_conexao()
    n = conn.execute(sql, params).fetchone()[0]
    conn.close()
    return n


def _por_rotulo(widgets, rotulo):
    return next(w for w in widgets if w.label == rotulo)


# ============================================================ QA-100..104 Cadastrar poste
def test_qa100_cadastrar_poste_valido():
    at = _app("cadastro")
    _por_rotulo(at.text_input, "Código da plaqueta").input("  P-77  ")
    _por_rotulo(at.text_input, "Rua / logradouro").input("Rua <i>X</i>")
    _por_rotulo(at.button, "Registrar poste").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    assert any("Poste P-77 gravado com localização pendente" in s.value for s in at.success)
    p = obter_poste_por_codigo("P-77")
    assert p["codigo"] == "P-77" and p["latitude"] is None and p["status"] == "normal"
    assert "Rua <i>X</i>" not in " ".join(m.value for m in at.markdown)  # escapado na tabela "Últimos"


def test_qa101_cadastrar_poste_com_ponto_marcado():
    at = _app("cadastro", cad_ponto={"lat": -6.15, "lng": -35.61})
    _por_rotulo(at.text_input, "Código da plaqueta").input("P-78")
    _por_rotulo(at.button, "Registrar poste").click()
    at.run()
    assert any("com localização —" in s.value for s in at.success)
    p = obter_poste_por_codigo("P-78")
    assert (p["latitude"], p["longitude"]) == (-6.15, -35.61)
    assert "cad_ponto" not in at.session_state


@pytest.mark.parametrize("codigo", ["", "   "])
def test_qa102_cadastrar_poste_vazio(codigo):
    at = _app("cadastro")
    _por_rotulo(at.text_input, "Código da plaqueta").input(codigo)
    _por_rotulo(at.button, "Registrar poste").click()
    at.run()
    assert any("Informe o código da plaqueta" in e.value for e in at.error)
    assert _contar("SELECT COUNT(*) FROM postes") == 0


def test_qa103_cadastrar_poste_duplicado():
    cadastrar_poste({"codigo": "P-01"})
    at = _app("cadastro")
    _por_rotulo(at.text_input, "Código da plaqueta").input("P-01")
    _por_rotulo(at.button, "Registrar poste").click()
    at.run()
    assert any("Já existe um poste com o código P-01" in e.value for e in at.error)
    assert _contar("SELECT COUNT(*) FROM postes") == 1


@pytest.mark.defeito("DEF-03")
def test_qa104_cadastrar_poste_duplicado_caixa_diferente():
    """'p-01' com 'P-01' existente: cadastrado como segundo poste (busca trata como o mesmo)."""
    cadastrar_poste({"codigo": "P-01"})
    at = _app("cadastro")
    _por_rotulo(at.text_input, "Código da plaqueta").input("p-01")
    _por_rotulo(at.button, "Registrar poste").click()
    at.run()
    assert _contar("SELECT COUNT(*) FROM postes") == 1, "duplicado lógico aceito"


# ============================================================ QA-110..114 Solicitar reparo
def test_qa110_emitir_os_poste_existente():
    cadastrar_poste({"codigo": "P-01", "logradouro": "Rua A", "bairro": "Centro", "latitude": -6.15,
                     "longitude": -35.61, "potencia": 150})
    at = _app("reparo", poste_selecionado_os="P-01")
    assert at.selectbox(key="reparo_poste").value.startswith("P-01")
    _por_rotulo(at.selectbox, "Prioridade").set_value("Urgente (Posto de Saúde / Centro / Risco)")
    _por_rotulo(at.button, "Emitir ordem de serviço").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    assert "Ordem de serviço emitida" in _textos(at)
    assert obter_poste_por_codigo("P-01")["status"] == "urgente"
    os_ = obter_poste_por_codigo("P-01")["historico_os"][0]
    assert os_["prioridade"] == "Urgente" and "Lâmpada LED 150W" in os_["materiais"]
    botoes = [b for b in at.get("link_button")]
    assert botoes and botoes[0].proto.url.startswith("https://wa.me/?text=")


def test_qa111_emitir_os_novo_poste():
    cadastrar_poste({"codigo": "P-01"})
    at = _app("reparo")
    at.selectbox(key="reparo_poste").set_value("+ Novo poste não listado")
    at.run()
    _por_rotulo(at.text_input, "Código do poste").input(" N-9 ")
    _por_rotulo(at.text_input, "Rua / logradouro").input("Rua Nova")
    _por_rotulo(at.button, "Emitir ordem de serviço").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    p = obter_poste_por_codigo("N-9")
    assert p and p["logradouro"] == "Rua Nova" and p["status"] == "chamado_aberto" and p["latitude"] is None


def test_qa112_emitir_os_sem_postes_na_base_codigo_vazio():
    at = _app("reparo")
    _por_rotulo(at.button, "Emitir ordem de serviço").click()
    at.run()
    assert any("Informe o código" in e.value for e in at.error)
    assert _contar("SELECT COUNT(*) FROM ordens_servico") == 0


@pytest.mark.defeito("DEF-01")
def test_qa113_emitir_os_novo_poste_caixa_diferente():
    """Digitar 'p-01' (existe 'P-01'): não cadastra (ilike acha), mas grava O.S. com 'p-01'.
    No SQLite a FK é case-sensitive mas o PRAGMA foreign_keys aceita? -> verificar consistência."""
    cadastrar_poste({"codigo": "P-01"})
    at = _app("reparo")
    at.selectbox(key="reparo_poste").set_value("+ Novo poste não listado")
    at.run()
    _por_rotulo(at.text_input, "Código do poste").input("p-01")
    _por_rotulo(at.button, "Emitir ordem de serviço").click()
    at.run()
    assert not at.exception, at.exception
    assert not at.error, [e.value for e in at.error]
    assert _contar("SELECT COUNT(*) FROM ordens_servico WHERE codigo_poste = 'P-01'") == 1
    assert obter_poste_por_codigo("P-01")["status"] == "chamado_aberto"


# ============================================================ QA-120..123 Ordens de serviço
def test_qa120_concluir_os_pela_tela():
    cadastrar_poste({"codigo": "P-01"})
    p = criar_ordem_servico("P-01", "Lâmpada apagada", prioridade="Urgente")
    at = _app("ordens")
    at.button(key=f"btn_concluir_{p}").click()
    at.run()
    assert not at.exception and not at.error
    assert obter_poste_por_codigo("P-01")["status"] == "normal"
    assert _contar("SELECT COUNT(*) FROM ordens_servico WHERE status='concluida'") == 1
    assert "Nenhuma ordem de serviço encontrada" in _textos(at)  # filtro padrão "Abertas"


def test_qa121_busca_e_filtro_de_ordens():
    cadastrar_poste({"codigo": "P-01", "logradouro": "Rua das Flores"})
    cadastrar_poste({"codigo": "P-02"})
    criar_ordem_servico("P-01", "Relé colado")
    criar_ordem_servico("P-02", "Fiação rompida")
    at = _app("ordens")
    at.text_input(key="os_busca").input("flores")
    at.run()
    txt = _textos(at)
    assert "Relé colado" in txt and "Fiação rompida" not in txt


def test_qa122_os_com_html_no_defeito_e_escapada():
    cadastrar_poste({"codigo": "P-<1>"})
    criar_ordem_servico("P-<1>", "<script>alert(1)</script>", solicitante="<b>x</b>")
    at = _app("ordens")
    html = " ".join(m.value for m in at.markdown)
    assert "<script>alert(1)</script>" not in html and "<b>x</b>" not in html and "P-<1>" not in html


# ============================================================ QA-130..132 Importar
def test_qa130_importar_pela_tela_file_uploader():
    buf = io.StringIO()
    pd.DataFrame([{"codigo": "K-1", "_localizacao_latitude": -6.15, "_localizacao_longitude": -35.61, "_id": 1},
                  {"codigo": "", "_localizacao_latitude": None, "_localizacao_longitude": None, "_id": 2}]
                 ).to_csv(buf, index=False, sep=";")
    at = _app("importar")
    at.get("file_uploader")[0].set_value(("kobo.csv", buf.getvalue().encode(), "text/csv"))
    at.run()
    _por_rotulo(at.button, "Processar e salvar postes").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    p = obter_poste_por_codigo("K-1")
    assert (p["latitude"], p["longitude"]) == (-6.15, -35.61)
    assert "Salvos / atualizados" in _textos(at)


def test_qa131_importar_arquivo_sem_coluna_codigo():
    at = _app("importar")
    at.get("file_uploader")[0].set_value(("x.csv", b"_id;_uuid\n1;a\n", "text/csv"))
    at.run()
    _por_rotulo(at.button, "Processar e salvar postes").click()
    at.run()
    assert any("coluna obrigatória de Código" in e.value for e in at.error)


def test_qa132_importar_nome_de_arquivo_e_caminho_de_erro_sao_escapados():
    at = _app("importar")
    at.get("file_uploader")[0].set_value(("<img src=x onerror=alert(1)>.csv", b"codigo\nA\n", "text/csv"))
    at.run()
    html = " ".join(m.value for m in at.markdown)
    assert "<img src=x" not in html


# ============================================================ QA-140..142 Localizar
def test_qa140_localizar_salvar_ponto():
    cadastrar_poste({"codigo": "P-02"})
    at = _app("localizar")
    assert at.selectbox(key="loc_poste").value.startswith("P-02")
    at.session_state["loc_candidato"] = {"codigo": "P-02", "lat": -6.1555, "lng": -35.6111}
    at.run()
    at.button(key="loc_salvar").click()
    at.run()
    assert not at.exception and not at.error
    p = obter_poste_por_codigo("P-02")
    assert (p["latitude"], p["longitude"]) == (-6.1555, -35.6111)
    assert any("Localização do poste P-02 salva" in s.value for s in at.success)


def test_qa141_localizar_candidato_de_outro_poste_e_descartado():
    cadastrar_poste({"codigo": "P-02"})
    at = _app("localizar", loc_candidato={"codigo": "OUTRO", "lat": -6.1, "lng": -35.6})
    assert "loc_candidato" not in at.session_state
    assert not any(b.key == "loc_salvar" for b in at.button)


def test_qa142_localizar_ponto_distante_avisa():
    cadastrar_poste({"codigo": "P-02"})
    at = _app("localizar", loc_candidato={"codigo": "P-02", "lat": -8.05, "lng": -34.9})
    assert any("km do centro" in w.value for w in at.warning)
    at.button(key="loc_descartar").click()
    at.run()
    assert "loc_candidato" not in at.session_state
    assert obter_poste_por_codigo("P-02")["latitude"] is None


# ============================================================ QA-150..156 Erro de banco / sessão
def test_qa150_erro_generico_de_banco_mostra_mensagem(monkeypatch):
    import app.dashboard.telas.mapa_postes as tela_mapa

    def falha(*a, **k):
        raise Exception("connection reset by peer")

    monkeypatch.setattr(tela_mapa, "obter_resumo_indicadores", falha)
    at = _app("mapa")
    assert any("Não foi possível falar com o banco" in e.value and "connection reset" in e.value for e in at.error)


def _logado(fake):
    return {"cliente": fake, "email": "a@b.c", "nome": "Ana Souza", "papel": "operador"}


def test_qa151_login_pela_tela_supabase_fake(supabase_fake):
    supabase_fake.tabelas["perfis"] = [{"id": "uid-1", "nome": "Ana Souza", "papel": "operador", "ativo": True}]
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    at.text_input[0].input("ana@pref.gov.br")
    at.text_input[1].input("senha")
    _por_rotulo(at.button, "Entrar").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    assert "Bom dia, Ana" in _textos(at) or "Boa tarde, Ana" in _textos(at) or "Boa noite, Ana" in _textos(at)
    assert "Operador" in _textos(at)


def test_qa152_login_invalido_pela_tela(supabase_fake):
    supabase_fake.auth.erro_login = Exception("Invalid login credentials")
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    at.text_input[0].input("ana@pref.gov.br")
    at.text_input[1].input("errada")
    _por_rotulo(at.button, "Entrar").click()
    at.run()
    assert any("E-mail ou senha incorretos" in e.value for e in at.error)


def test_qa153_jwt_expirado_desloga(supabase_fake):
    supabase_fake.falha = lambda q: Exception("{'code': 'PGRST301', 'message': 'JWT expired'}")
    at = _app("mapa", usuario_logado=_logado(supabase_fake))
    assert "usuario_logado" not in at.session_state
    assert any("Sua sessão expirou" in w.value for w in at.warning)
    assert any(b.label == "Entrar" for b in at.button)
    assert supabase_fake.auth.sign_out_chamadas == 1


def test_qa154_rerun_dentro_do_try_nao_e_engolido(supabase_fake):
    """st.rerun() (RerunException herda de BaseException) dentro do try/except Exception de main.py:128-131.
    Concluir O.S. chama st.rerun(): se fosse engolido, a tela mostraria a O.S. ainda aberta ou um st.error."""
    supabase_fake.tabelas["postes"] = [{"codigo": "P-01", "status": "normal", "latitude": None, "longitude": None}]
    from app.database.conexao import definir_cliente_sessao
    definir_cliente_sessao(supabase_fake)
    p = criar_ordem_servico("P-01", "X")
    at = _app("ordens", usuario_logado=_logado(supabase_fake))
    at.button(key=f"btn_concluir_{p}").click()
    at.run()
    assert not at.exception and not at.error, [e.value for e in at.error]
    assert "Nenhuma ordem de serviço encontrada" in _textos(at)


@pytest.mark.defeito("DEF-11")
def test_qa155_jwt_expirado_no_modo_local_nao_entra_em_laco(monkeypatch):
    """No modo local sair() não desloga (usuario_atual é fixo): erro com 'jwt' no texto -> rerun -> mesmo erro.
    Mais amplo: qualquer erro cujo texto contenha 'jwt' (ex.: coluna/valor com 'jwt') desloga o usuário."""
    import app.dashboard.telas.mapa_postes as tela_mapa

    def falha(*a, **k):
        raise Exception("JWT expired")

    monkeypatch.setattr(tela_mapa, "obter_resumo_indicadores", falha)
    at = AppTest.from_file(APP, default_timeout=20)
    at.session_state["pagina_atual"] = "mapa"
    at.run()
    assert not at.exception, "laço de rerun / timeout"


def test_qa156_sair_pelo_botao(supabase_fake):
    at = _app("mapa", usuario_logado=_logado(supabase_fake))
    at.button(key="btn_sair").click()
    at.run()
    assert "usuario_logado" not in at.session_state and supabase_fake.auth.sign_out_chamadas == 1
    assert any(b.label == "Entrar" for b in at.button)


@pytest.mark.defeito("DEF-02")
def test_qa157_navegar_reparo_supabase_sem_permissao_insert_mostra_erro_amigavel(supabase_fake):
    """RLS bloqueando INSERT (perfil desativado no meio da sessão): erro 42501 cai no handler genérico
    com 'Detalhe técnico' cru. Registrado como evidência (não falha)."""
    supabase_fake.tabelas["postes"] = [{"codigo": "P-01", "status": "normal"}]
    supabase_fake.falha = lambda q: (Exception("{'code': '42501', 'message': 'new row violates row-level security "
                                               "policy for table \"ordens_servico\"'}") if q.acao == "insert" else None)
    at = _app("reparo", usuario_logado=_logado(supabase_fake), poste_selecionado_os="P-01")
    _por_rotulo(at.button, "Emitir ordem de serviço").click()
    at.run()
    erros = [e.value for e in at.error]
    assert erros and "Detalhe técnico" in erros[0]
    assert "row-level security" not in erros[0], "mensagem técnica crua exibida ao usuário"


@pytest.mark.parametrize("tela", ["mapa", "reparo", "ordens", "cadastro", "importar", "localizar"])
def test_qa158_telas_renderizam_no_modo_supabase_fake(supabase_fake, tela):
    from app.database.conexao import definir_cliente_sessao

    supabase_fake.tabelas["postes"] = [
        {"codigo": "P-01", "logradouro": "Rua <b>A</b>", "bairro": "Centro", "status": "urgente",
         "latitude": -6.15, "longitude": -35.61},
        {"codigo": "P-02", "status": "normal"}]
    definir_cliente_sessao(supabase_fake)
    criar_ordem_servico("P-01", "Lâmpada apagada", prioridade="Urgente")
    at = _app(tela, usuario_logado=_logado(supabase_fake))
    assert not at.error, [e.value for e in at.error]
    assert "Rua <b>A</b>" not in " ".join(m.value for m in at.markdown)
    assert all(q.tabela in ("postes", "ordens_servico") for q in supabase_fake.chamadas)


@pytest.mark.defeito("DEF-17")
def test_qa159_falha_de_rede_no_login_vira_traceback(supabase_fake):
    """entrar() só trata exceção do sign_in; erro ao ler 'perfis' sobe sem tratamento (login fica fora do
    try/except de main.py) -> traceback do Streamlit na tela de login."""
    supabase_fake.falha = lambda q: Exception("connection reset") if q.tabela == "perfis" else None
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    at.text_input[0].input("ana@pref.gov.br")
    at.text_input[1].input("senha")
    _por_rotulo(at.button, "Entrar").click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.defeito("DEF-18")
def test_qa160_mapa_busca_ficha_e_ir_para_reparo():
    """Fluxo: buscar o código no mapa -> ficha do poste -> 'Solicitar reparo' leva à tela com o poste."""
    cadastrar_poste({"codigo": "P-01", "logradouro": "Rua A", "bairro": "Centro", "latitude": -6.15,
                     "longitude": -35.61, "observacoes": "<b>relé</b>"})
    cadastrar_poste({"codigo": "P-02", "logradouro": "Rua B", "bairro": "Centro"})
    criar_ordem_servico("P-01", "Relé colado")
    at = _app("mapa")
    at.text_input(key="mapa_busca").input("p-01")
    at.run()
    assert not at.exception and not at.error
    print("FICHA APÓS BUSCA:", at.selectbox(key="mapa_inspecao").value, at.session_state["mapa_foco"])
    if not at.selectbox(key="mapa_inspecao").value.startswith("P-01"):
        pytest.fail("busca define mapa_foco, mas o selectbox 'Inspecionar poste' mantém o valor anterior")
    txt = " ".join(m.value for m in at.markdown)
    assert "Relé colado" in txt and "<b>relé</b>" not in txt and "-6.150000, -35.610000" in txt
    at.button(key="ficha_reparo").click()
    at.run()
    assert at.session_state["pagina_atual"] == "reparo"
    assert at.selectbox(key="reparo_poste").value.startswith("P-01")


def test_qa161_mapa_ficha_por_selecao_e_ir_para_reparo():
    cadastrar_poste({"codigo": "P-01", "logradouro": "Rua A", "bairro": "Centro", "latitude": -6.15,
                     "longitude": -35.61, "observacoes": "<b>relé</b>"})
    criar_ordem_servico("P-01", "Relé colado")
    at = _app("mapa")
    at.selectbox(key="mapa_inspecao").set_value("P-01 · Rua A (Centro)")
    at.run()
    txt = " ".join(m.value for m in at.markdown)
    assert "Relé colado" in txt and "<b>relé</b>" not in txt and "-6.150000, -35.610000" in txt
    at.button(key="ficha_reparo").click()
    at.run()
    assert not at.exception and at.session_state["pagina_atual"] == "reparo"
    assert at.selectbox(key="reparo_poste").value.startswith("P-01")
