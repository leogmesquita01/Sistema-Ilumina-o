"""QA — caminhos Supabase com cliente FALSO (sem rede, sem produção).

Integração real com o Supabase: BLOQUEADA (não existe projeto/branch de teste;
o único projeto é produção e o escopo proíbe escrita/login nele).
"""
import io

import pandas as pd
import pytest

from app.cache import limpar_cache
from app.database import conexao
from app.dashboard import sessao
from tests.auditoria.fake_supabase import FakeAPIError, FakeSupabase


def _csv(linhas):
    buf = io.StringIO()
    pd.DataFrame(linhas).to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


@pytest.fixture
def ss(monkeypatch):
    """st.session_state isolado (dict) para testar sessao.py fora do AppTest."""
    estado = {}
    monkeypatch.setattr(sessao.st, "session_state", estado)
    return estado


def _poste(codigo, **extra):
    base = {"codigo": codigo, "logradouro": "Rua A", "bairro": "Centro", "status": "normal",
            "latitude": None, "longitude": None}
    base.update(extra)
    return base


# =========================================================== QA-050..056 sessão / login
def test_qa050_entrar_sucesso(supabase_fake, ss):
    supabase_fake.tabelas["perfis"] = [{"id": "uid-1", "nome": "Leo Mesquita", "papel": "admin", "ativo": True}]
    assert sessao.entrar("  Pessoa@Exemplo.COM ", "s3nha") is None
    assert supabase_fake.auth.credenciais == {"email": "pessoa@exemplo.com", "password": "s3nha"}
    u = ss["usuario_logado"]
    assert (u["nome"], u["papel"], u["email"], u["cliente"]) == ("Leo Mesquita", "admin", "pessoa@exemplo.com",
                                                                  supabase_fake)
    q = supabase_fake.chamadas_de("perfis")[0]
    assert ("eq", ("id", "uid-1"), {}) in q.ops
    assert sessao.preparar_sessao() is True and conexao.obter_supabase() is supabase_fake


@pytest.mark.parametrize("msg,esperado", [
    ("Invalid login credentials", "E-mail ou senha incorretos."),
    ("Email not confirmed", "E-mail ainda não confirmado"),
    ("Connection refused", "Não foi possível entrar agora"),
])
def test_qa051_entrar_erros_auth(supabase_fake, ss, msg, esperado):
    supabase_fake.auth.erro_login = Exception(msg)
    assert esperado in sessao.entrar("a@b.c", "x")
    assert "usuario_logado" not in ss


def test_qa052_entrar_campos_vazios(supabase_fake, ss):
    assert sessao.entrar("", "x") == "Informe e-mail e senha."
    assert sessao.entrar("a@b.c", "") == "Informe e-mail e senha."
    assert supabase_fake.auth.credenciais is None


@pytest.mark.parametrize("perfis", [[], [{"id": "uid-1", "nome": "X", "papel": "operador", "ativo": False}]])
def test_qa053_entrar_perfil_inexistente_ou_inativo(supabase_fake, ss, perfis):
    supabase_fake.tabelas["perfis"] = perfis
    erro = sessao.entrar("a@b.c", "x")
    assert "ainda não foi liberado" in erro
    assert supabase_fake.auth.sign_out_chamadas == 1
    assert "usuario_logado" not in ss
    with pytest.raises(conexao.SessaoNecessaria):
        conexao.obter_supabase()


def test_qa054_entrar_nome_e_papel_padrao(supabase_fake, ss):
    supabase_fake.tabelas["perfis"] = [{"id": "uid-1", "nome": "  ", "papel": None, "ativo": True}]
    assert sessao.entrar("joana.silva@pref.rn.gov.br", "x") is None
    assert ss["usuario_logado"]["nome"] == "joana.silva" and ss["usuario_logado"]["papel"] == "operador"


def test_qa055_sair_faz_sign_out_e_limpa(supabase_fake, ss):
    ss["usuario_logado"] = {"cliente": supabase_fake, "email": "a", "nome": "A", "papel": "admin"}
    sessao.sair("Sua sessão expirou. Entre novamente.")
    assert supabase_fake.auth.sign_out_chamadas == 1
    assert "usuario_logado" not in ss and ss["aviso_login"].startswith("Sua sessão expirou")
    with pytest.raises(conexao.SessaoNecessaria):
        conexao.obter_supabase()


def test_qa056_obter_supabase_sem_sessao(supabase_fake, ss):
    conexao.definir_cliente_sessao(None)
    with pytest.raises(conexao.SessaoNecessaria):
        conexao.obter_supabase()
    assert sessao.preparar_sessao() is False
    from app.servicos.dados_postes import listar_postes
    with pytest.raises(conexao.SessaoNecessaria):
        listar_postes()


@pytest.mark.defeito("DEF-17")
def test_qa057_falha_ao_ler_perfil_nao_deixa_sessao_meio_aberta(supabase_fake, ss):
    """Se a consulta ao perfil falhar (rede/RLS), o token já autenticado fica no cliente e no ContextVar."""
    supabase_fake.falha = lambda q: FakeAPIError("timeout") if q.tabela == "perfis" else None
    assert "perfil" in sessao.entrar("a@b.c", "x")  # mensagem, sem exceção nem traceback
    print("sign_out:", supabase_fake.auth.sign_out_chamadas, "ContextVar:", conexao._cliente_sessao.get())
    assert supabase_fake.auth.sign_out_chamadas == 1 and conexao._cliente_sessao.get() is None


@pytest.mark.defeito("DEF-16")
def test_qa058_cache_global_entre_sessoes(supabase_fake, ss):
    """Usuário B (perfil desativado/RLS diferente) não pode receber do cache o que foi lido com o token de A."""
    from app.servicos.dados_postes import listar_postes

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    conexao.definir_cliente_sessao(supabase_fake, identidade="usuario-a")
    assert len(listar_postes()) == 1
    chamadas_a = len(supabase_fake.chamadas)
    assert len(listar_postes()) == 1 and len(supabase_fake.chamadas) == chamadas_a  # A usa o próprio cache

    outro = FakeSupabase()  # sessão B: o banco devolve 0 linhas para ela
    conexao.definir_cliente_sessao(outro, identidade="usuario-b")
    assert listar_postes() == []
    print("CHAMADAS DA SESSÃO B:", len(outro.chamadas))
    assert outro.chamadas != [], "sessão B recebeu dados do cache da sessão A, sem consultar o banco"
    conexao.definir_cliente_sessao(None)
    with pytest.raises(conexao.SessaoNecessaria):
        listar_postes()


# =========================================================== QA-060..068 _gravar_supabase / import
def test_qa060_import_supabase_novo_e_existente(supabase_fake):
    from app.importer import import_poles_file

    supabase_fake.tabelas["postes"] = [
        _poste("P-01", status="urgente", latitude=-6.15, longitude=-35.61, tipo_luminaria="Vapor de Sódio", id=1)]
    res = import_poles_file(_csv([
        {"codigo": "P-01", "rua": "Rua Nova", "bairro": None, "latitude": None, "longitude": None, "potencia": None},
        {"codigo": "P-02", "rua": None, "bairro": "Lagoa", "latitude": -6.2, "longitude": -35.7, "potencia": "70"},
    ]), "a.csv")
    assert res["importados"] == 2

    # existentes: todos os códigos do banco, paginados (comparação sem diferenciar caixa)
    sel = supabase_fake.chamadas_de("postes", "select")[0]
    assert sel.ops[0] == ("select", ("codigo",), {"count": None}) and ("range", (0, 999), {}) in sel.ops
    ups = supabase_fake.chamadas_de("postes", "upsert")
    assert all(q.on_conflict == "codigo" for q in ups)
    enviados = {r["codigo"]: r for q in ups for r in q.payload}
    # existente: sem status, sem coordenada, sem campos vazios
    assert enviados["P-01"] == {"codigo": "P-01", "logradouro": "Rua Nova"}
    # novo: status normal + padrões
    assert enviados["P-02"]["status"] == "normal"
    assert enviados["P-02"]["logradouro"] == "Não informado" and enviados["P-02"]["potencia"] == 70
    # cada lote tem um único conjunto de colunas
    for q in ups:
        assert len({tuple(sorted(r)) for r in q.payload}) == 1
    p1 = next(p for p in supabase_fake.tabelas["postes"] if p["codigo"] == "P-01")
    assert (p1["status"], p1["latitude"], p1["longitude"], p1["bairro"], p1["tipo_luminaria"]) == (
        "urgente", -6.15, -35.61, "Centro", "Vapor de Sódio")


def test_qa061_import_supabase_coordenada_valida_atualiza_existente(supabase_fake):
    from app.importer import import_poles_file

    supabase_fake.tabelas["postes"] = [_poste("P-01", latitude=-6.1, longitude=-35.5, status="chamado_aberto")]
    import_poles_file(_csv([{"codigo": "P-01", "latitude": -6.2, "longitude": -35.7}]), "a.csv")
    p = supabase_fake.tabelas["postes"][0]
    assert (p["latitude"], p["longitude"], p["status"]) == (-6.2, -35.7, "chamado_aberto")


def test_qa062_import_supabase_lotes_de_500(supabase_fake):
    from app.importer import import_poles_file

    supabase_fake.tabelas["postes"] = [_poste(f"E{i:04d}", id=i + 1) for i in range(300)]
    linhas = [{"codigo": f"E{i:04d}", "rua": "R"} for i in range(300)] + \
             [{"codigo": f"N{i:04d}", "rua": "R"} for i in range(1200)]
    import_poles_file(_csv(linhas), "a.csv")
    sel = supabase_fake.chamadas_de("postes", "select")
    assert len(sel) == 1  # 300 existentes cabem numa página de 1000
    tamanhos = sorted(len(q.payload) for q in supabase_fake.chamadas_de("postes", "upsert"))
    assert tamanhos == [200, 300, 500, 500]
    assert len(supabase_fake.tabelas["postes"]) == 1500


@pytest.mark.defeito("DEF-03")
def test_qa063_import_supabase_codigo_caixa_diferente(supabase_fake):
    """'P-01' existente + planilha 'p-01'. O resto do app trata o código sem diferenciar caixa
    (obter_poste_por_codigo usa ilike; SQLite usa NOCASE), mas o importador checa com in_ (case-sensitive):
    'p-01' é tratado como NOVO -> recebe status 'normal' e padrões e vira um 2º poste (duplicado lógico)."""
    from app.importer import import_poles_file
    from app.servicos.dados_postes import obter_poste_por_codigo

    supabase_fake.tabelas["postes"] = [_poste("P-01", status="urgente", latitude=-6.15, longitude=-35.61)]
    import_poles_file(_csv([{"codigo": "p-01", "rua": "Rua Nova"}]), "a.csv")
    enviado = supabase_fake.chamadas_de("postes", "upsert")[0].payload[0]
    # evidência do que foi enviado
    print("ENVIADO:", enviado)
    assert "status" not in enviado, f"poste existente tratado como novo: {enviado}"
    assert len(supabase_fake.tabelas["postes"]) == 1
    limpar_cache()
    assert obter_poste_por_codigo("P-01")["status"] == "urgente"


@pytest.mark.defeito("DEF-03")
def test_qa064_import_codigo_caixa_diferente_modo_local():
    """Mesmo cenário no SQLite: UNIQUE é case-sensitive no SQLite também -> 2 linhas."""
    from app.database.conexao import obter_conexao
    from app.importer import import_poles_file
    from app.servicos.dados_postes import cadastrar_poste

    cadastrar_poste({"codigo": "P-01"})
    import_poles_file(_csv([{"codigo": "p-01", "rua": "Rua Nova"}]), "a.csv")
    conn = obter_conexao()
    n = conn.execute("SELECT COUNT(*) FROM postes").fetchone()[0]
    conn.close()
    assert n == 1, f"{n} linhas após importar 'p-01' com 'P-01' existente"


def test_qa065_import_supabase_existente_vira_novo_quando_outra_coluna_falta(supabase_fake):
    """Lote só com postes NOVOS: colunas de texto ausentes na planilha ficam fora do payload e o
    PostgREST usa o default do banco; ok. Mas se um poste novo e um existente caem no MESMO grupo de
    colunas, o existente seria sobrescrito com o padrão. Verifica que isso NÃO ocorre."""
    from app.importer import import_poles_file

    supabase_fake.tabelas["postes"] = [_poste("P-01", logradouro="Rua Velha", bairro="Bela Vista")]
    # P-01 existente com bairro vazio; P-02 novo com bairro vazio -> P-02 recebe "Centro"; P-01 mantém
    import_poles_file(_csv([{"codigo": "P-01", "rua": "Rua X", "bairro": None},
                            {"codigo": "P-02", "rua": "Rua Y", "bairro": None}]), "a.csv")
    p1 = next(p for p in supabase_fake.tabelas["postes"] if p["codigo"] == "P-01")
    assert p1["bairro"] == "Bela Vista"


@pytest.mark.defeito("DEF-15")
def test_qa066_import_supabase_falha_no_meio_nao_e_atomica(supabase_fake):
    """Erro no 2º lote: o 1º já foi gravado (sem transação) e o cache NÃO é limpo."""
    from app import importer

    cont = {"n": 0}

    def falha(q):
        if q.acao == "upsert":
            cont["n"] += 1
            if cont["n"] == 2:
                return FakeAPIError("{'code': '57014', 'message': 'canceling statement due to statement timeout'}")
        return None

    supabase_fake.falha = falha
    linhas = [{"codigo": f"N{i:04d}"} for i in range(700)]
    with pytest.raises(FakeAPIError):
        importer.import_poles_file(_csv(linhas), "a.csv")
    print("GRAVADOS APÓS FALHA:", len(supabase_fake.tabelas["postes"]))
    assert len(supabase_fake.tabelas["postes"]) == 0, "importação parcial (sem transação)"


# =========================================================== QA-070..075 ordens no Supabase
def test_qa070_criar_os_protocolo_do_banco_e_status(supabase_fake):
    from app.servicos.ordens_service import criar_ordem_servico

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    p = criar_ordem_servico("P-01", "Lâmpada apagada", prioridade="Urgente",
                            materiais=[{"item": "Relé", "quantidade": 1}])
    assert p.startswith("OS-") and p.endswith("-0001")
    ins = supabase_fake.chamadas_de("ordens_servico", "insert")[0]
    assert "protocolo" not in ins.payload and ins.payload["status"] == "aberta"
    assert ins.payload["materiais"] == '[{"item": "Relé", "quantidade": 1}]'
    upd = supabase_fake.chamadas_de("postes", "update")[0]
    assert upd.payload["status"] == "urgente" and ("eq", ("codigo", "P-01"), {}) in upd.ops
    assert supabase_fake.tabelas["postes"][0]["status"] == "urgente"


def test_qa071_criar_os_sem_protocolo(supabase_fake):
    from app.servicos.ordens_service import criar_ordem_servico

    supabase_fake.gatilho_protocolo = False
    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    with pytest.raises(RuntimeError, match="002_login.sql"):
        criar_ordem_servico("P-01", "X")


@pytest.mark.defeito("DEF-04")
def test_qa072_criar_os_sem_protocolo_nao_deixa_os_orfa(supabase_fake):
    """Quando o protocolo não volta, a O.S. JÁ foi inserida e o status do poste não é recalculado."""
    from app.servicos.ordens_service import criar_ordem_servico

    supabase_fake.gatilho_protocolo = False
    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    with pytest.raises(RuntimeError):
        criar_ordem_servico("P-01", "X", prioridade="Urgente")
    assert supabase_fake.tabelas["ordens_servico"] == [], "O.S. gravada sem protocolo e poste segue 'normal'"


@pytest.mark.defeito("DEF-01")
def test_qa073_criar_os_codigo_com_caixa_diferente(supabase_fake):
    """Tela de reparo (novo poste): obter_poste_por_codigo('p-01') acha 'P-01' via ilike, então não cadastra;
    mas a O.S. é criada com codigo_poste='p-01' -> FK (case-sensitive) rejeita a O.S."""
    from app.servicos.dados_postes import obter_poste_por_codigo
    from app.servicos.ordens_service import criar_ordem_servico

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    assert obter_poste_por_codigo("p-01")["codigo"] == "P-01"
    criar_ordem_servico("p-01", "Lâmpada apagada")  # é o que solicitar_reparo.py:309-331 faz


def test_qa074_concluir_os(supabase_fake):
    from app.servicos.ordens_service import concluir_ordem_servico, criar_ordem_servico

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    p1 = criar_ordem_servico("P-01", "A", prioridade="Urgente")
    criar_ordem_servico("P-01", "B", prioridade="Normal")
    concluir_ordem_servico(p1)
    assert supabase_fake.tabelas["postes"][0]["status"] == "chamado_aberto"
    os1 = next(o for o in supabase_fake.tabelas["ordens_servico"] if o["protocolo"] == p1)
    assert os1["status"] == "concluida" and os1["data_conclusao"]


@pytest.mark.defeito("DEF-05")
def test_qa075_concluir_duas_vezes_update_filtra_status(supabase_fake):
    """Concluir duas vezes (duplo clique / duas abas): o UPDATE não filtra status='aberta' e
    reescreve data_conclusao da 1ª baixa."""
    from app.servicos.ordens_service import concluir_ordem_servico, criar_ordem_servico

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    p = criar_ordem_servico("P-01", "A")
    concluir_ordem_servico(p)
    primeira = next(o for o in supabase_fake.tabelas["ordens_servico"])["data_conclusao"]
    concluir_ordem_servico(p)
    updates = supabase_fake.chamadas_de("ordens_servico", "update")
    assert len(updates) == 2
    print("FILTROS DO 2º UPDATE:", updates[1].ops)
    assert ("eq", ("status", "aberta"), {}) in updates[1].ops, "UPDATE sem filtro de status"
    assert next(o for o in supabase_fake.tabelas["ordens_servico"])["data_conclusao"] == primeira


@pytest.mark.defeito("DEF-06")
def test_qa076_update_sem_linha_afetada_e_silencioso(supabase_fake):
    """RLS que filtra o UPDATE (perfil desativado durante a sessão) devolve 0 linhas sem erro:
    concluir_ordem_servico/atualizar_status/definir_localizacao não verificam res.data."""
    from app.servicos.dados_postes import definir_localizacao_poste

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    supabase_fake.update_vazio = True
    with pytest.raises(Exception):
        definir_localizacao_poste("P-01", -6.15, -35.61)


def test_qa077_concluir_protocolo_inexistente(supabase_fake):
    from app.servicos.ordens_service import concluir_ordem_servico

    concluir_ordem_servico("OS-2026-9999")
    assert supabase_fake.chamadas_de("ordens_servico", "update") == []
    assert supabase_fake.chamadas_de("postes", "update") == []


def test_qa078_listar_ordens_achata_relacao(supabase_fake):
    from app.servicos.ordens_service import criar_ordem_servico, listar_ordens

    supabase_fake.tabelas["postes"] = [_poste("P-01", latitude=-6.15, longitude=-35.61, potencia=None)]
    criar_ordem_servico("P-01", "A", materiais=[{"item": "X", "quantidade": 2}])
    o = listar_ordens()[0]
    assert (o["logradouro"], o["latitude"], o["potencia"], o["materiais_lista"]) == (
        "Rua A", -6.15, 100, [{"item": "X", "quantidade": 2}])
    assert "postes" not in o
    q = supabase_fake.chamadas_de("ordens_servico", "select")[-1]
    assert ("range", (0, 999), {}) in q.ops


# =========================================================== QA-080..086 postes no Supabase
@pytest.mark.parametrize("termo,esperado", [
    ("P-01", "codigo.ilike.%P-01%,logradouro.ilike.%P-01%,bairro.ilike.%P-01%"),
    ("Rua (A), 2", "codigo.ilike.%Rua  A   2%,logradouro.ilike.%Rua  A   2%,bairro.ilike.%Rua  A   2%"),
])
def test_qa080_listar_postes_or_string(supabase_fake, termo, esperado):
    from app.servicos.dados_postes import listar_postes

    listar_postes(termo_busca=termo)
    q = supabase_fake.chamadas_de("postes", "select")[0]
    filtro = [a for n, a, _ in q.ops if n == "or_"][0][0]
    assert filtro == esperado
    assert ("order", ("id",), {"desc": True}) in q.ops and ("range", (0, 999), {}) in q.ops


@pytest.mark.defeito("DEF-09")
@pytest.mark.parametrize("termo", ['Rua "A"', "a.b", "50%", "P_01", "x\\y", "a*b"])
def test_qa081_listar_postes_or_caracteres_especiais(supabase_fake, termo):
    """Aspas, %, _, \\ e * não são escapados no or_(): aspas quebram a sintaxe do PostgREST
    (erro 400 -> tela de erro), '%'/'_'/'*' viram curinga. Esperado: termo tratado como literal."""
    from app.servicos.dados_postes import listar_postes

    listar_postes(termo_busca=termo)
    filtro = [a for n, a, _ in supabase_fake.chamadas_de("postes", "select")[0].ops if n == "or_"][0][0]
    print("OR ENVIADO:", filtro)
    valor = filtro.split(",")[0].split(".", 2)[2]
    miolo = valor[1:-1]
    assert '"' not in miolo and "*" not in miolo
    assert all(c not in miolo.replace("\\%", "").replace("\\_", "").replace("\\\\", "") for c in "%_\\")


def test_qa082_obter_poste_por_codigo_escapa_curingas(supabase_fake):
    from app.servicos.dados_postes import obter_poste_por_codigo

    supabase_fake.tabelas["postes"] = [_poste("PX01"), _poste("P_01")]
    assert obter_poste_por_codigo("P_01")["codigo"] == "P_01"
    limpar_cache()
    assert obter_poste_por_codigo("p%") is None
    q = supabase_fake.chamadas_de("postes", "select")[0]
    assert ("ilike", ("codigo", "P\\_01"), {}) in q.ops


def test_qa083_cadastrar_poste_duplicado_supabase(supabase_fake):
    from app.servicos.dados_postes import cadastrar_poste, codigo_duplicado

    from app.servicos.dados_postes import PosteDuplicado

    cadastrar_poste({"codigo": " P-01 "})
    for repetido in ("P-01", "p-01"):
        with pytest.raises(PosteDuplicado) as e:
            cadastrar_poste({"codigo": repetido})
        assert codigo_duplicado(e.value) and e.value.codigo_existente == "P-01"
    assert len(supabase_fake.chamadas_de("postes", "insert")) == 1
    # o UNIQUE do banco continua sendo reconhecido (corrida entre duas sessões)
    assert codigo_duplicado(FakeAPIError("{'code': '23505'}"))
    assert supabase_fake.chamadas_de("postes", "insert")[0].payload["codigo"] == "P-01"


def test_qa084_resumo_indicadores_supabase(supabase_fake):
    from app.servicos.dados_postes import obter_resumo_indicadores

    supabase_fake.tabelas["postes"] = [_poste("A", tipo_luminaria="LED 100W"), _poste("B", tipo_luminaria="led"),
                                       _poste("C", tipo_luminaria="Vapor de Sódio", status="urgente"),
                                       _poste("D", tipo_luminaria=None, status="defeito_urgente")]
    r = obter_resumo_indicadores()
    assert (r["total_postes"], r["total_led"], r["taxa_led"], r["total_chamados"]) == (4, 2, 50.0, 2)


@pytest.mark.defeito("DEF-04")
def test_qa079_criar_os_falha_ao_recalcular_status(supabase_fake):
    """INSERT da O.S. ok, UPDATE do poste falha: O.S. fica aberta, poste 'normal'; reenvio duplica a O.S."""
    from app.servicos.ordens_service import criar_ordem_servico

    supabase_fake.tabelas["postes"] = [_poste("P-01")]
    supabase_fake.falha = lambda q: FakeAPIError("timeout") if (q.tabela, q.acao) == ("postes", "update") else None
    with pytest.raises(FakeAPIError):
        criar_ordem_servico("P-01", "X", prioridade="Urgente")
    print("O.S. gravadas:", len(supabase_fake.tabelas["ordens_servico"]), "status:",
          supabase_fake.tabelas["postes"][0]["status"])
    assert supabase_fake.tabelas["ordens_servico"] == [] or supabase_fake.tabelas["postes"][0]["status"] == "urgente"
