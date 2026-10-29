"""QA — testes unitários (sem banco): importer, fuso, ordens, paginação, cache.

Convenção: o teste afirma o comportamento ESPERADO. Se falhar, o defeito
indicado em @pytest.mark.defeito está confirmado (status "Reprovado").
"""
import datetime
import math
import urllib.parse

import pandas as pd
import pytest

from app import cache
from app.database.paginacao import MAXIMO_PAGINAS, buscar_todas_paginas
from app.fuso import para_local
from app.importer import (
    _ler_planilha,
    identify_columns,
    ler_coordenadas,
    ler_potencia,
    preparar_registros,
)
from app.servicos.dados_postes import localizacao_pendente
from app.servicos.ordens_service import gerar_mensagem_whatsapp, link_rota, status_pelas_ordens_abertas
from tests.auditoria.fake_supabase import FakeConsultaPaginada

KOBO_META = ["_id", "_uuid", "_submission_time", "_validation_status", "_notes", "_status",
             "_submitted_by", "__version__", "_tags", "_index"]


# ---------------------------------------------------------------- QA-010..015 importer: colunas
def test_qa010_kobo_xml_names_geopoint():
    colunas = ["start", "end", "codigo", "localizacao", "_localizacao_latitude", "_localizacao_longitude",
               "_localizacao_altitude", "_localizacao_precision", "foto", "foto_URL", "logradouro", "bairro",
               "referencia", "tipo_luminaria", "potencia", "tipo_poste", "tipo_braco", "observacoes", *KOBO_META]
    m = identify_columns(colunas)
    assert m["codigo"] == "codigo"
    assert m["latitude"] == "_localizacao_latitude"
    assert m["longitude"] == "_localizacao_longitude"
    assert m["logradouro"] == "logradouro"
    usados = set(m.values())
    for meta in ["start", "end", "foto", "foto_URL", "_id", "_uuid", "_submission_time", "_index",
                 "_localizacao_altitude", "_localizacao_precision", "localizacao"]:
        assert meta not in usados, f"coluna de metadado {meta} foi mapeada: {m}"


def test_qa011_kobo_rotulos_geopoint():
    colunas = ["start", "end", "Código da plaqueta", "Localização do poste", "_Localização do poste_latitude",
               "_Localização do poste_longitude", "_Localização do poste_altitude",
               "_Localização do poste_precision", "Foto do poste", "Foto do poste_URL", "Rua / Logradouro",
               "Bairro ou comunidade", "Ponto de referência", "Tipo de luminária", "Potência (W)",
               "Tipo de estrutura", "Tipo de braço", "Observações", *KOBO_META]
    m = identify_columns(colunas)
    assert m == {
        "codigo": "Código da plaqueta",
        "latitude": "_Localização do poste_latitude",
        "longitude": "_Localização do poste_longitude",
        "logradouro": "Rua / Logradouro",
        "bairro": "Bairro ou comunidade",
        "referencia": "Ponto de referência",
        "tipo_luminaria": "Tipo de luminária",
        "potencia": "Potência (W)",
        "tipo_poste": "Tipo de estrutura",
        "tipo_braco": "Tipo de braço",
        "observacoes": "Observações",
    }


def test_qa012_kobo_so_metadados_sem_codigo():
    """Sem coluna de código, nenhum metadado (_id, _index, _uuid) pode virar código."""
    m = identify_columns(["start", "end", "foto", "foto_URL", *KOBO_META])
    assert "codigo" not in m


# ---------------------------------------------------------------- QA-016..019 preparar/ler
def test_qa016_preparar_registros_kobo():
    df = pd.DataFrame([
        {"codigo": 1001.0, "_localizacao_latitude": "-6,15", "_localizacao_longitude": "-35,61",
         "tipo_luminaria": "vapor_de_sodio", "potencia": "70 W", "_id": 9},
        {"codigo": None, "_localizacao_latitude": None, "_localizacao_longitude": None,
         "tipo_luminaria": None, "potencia": None, "_id": 10},
        {"codigo": "1001", "_localizacao_latitude": 0, "_localizacao_longitude": 0,
         "tipo_luminaria": "LED", "potencia": "", "_id": 11},
    ])
    prep = preparar_registros(df, identify_columns(list(df.columns)))
    assert prep["ignoradas"] == 1 and prep["duplicados"] == 1
    assert len(prep["registros"]) == 1
    r = prep["registros"][0]
    # vale a última ocorrência: coordenada 0,0 descartada, potência vazia -> None
    assert r == {"codigo": "1001", "tipo_luminaria": "LED", "potencia": None, "latitude": None, "longitude": None}
    assert any("0,0" in a for a in prep["avisos"]) and any("repetido" in a for a in prep["avisos"])


@pytest.mark.parametrize("lat,lng,esperado", [
    ("-6,15", "-35,60", (-6.15, -35.6, None)),
    ("-6.15", "-35.6", (-6.15, -35.6, None)),
    (None, None, (None, None, None)),
    (float("nan"), float("nan"), (None, None, None)),
    ("-6.15", None, (None, None, "coordenada ilegível, ignorada")),
    ("abc", "-35", (None, None, "coordenada ilegível, ignorada")),
    (91, -35, (None, None, "coordenada fora da faixa válida, ignorada")),
    (0, 0, (None, None, "coordenada 0,0 ignorada")),
    ("inf", "-35", (None, None, "coordenada ilegível, ignorada")),
])
def test_qa017_ler_coordenadas(lat, lng, esperado):
    assert ler_coordenadas(lat, lng) == esperado


@pytest.mark.parametrize("valor,esperado", [("100 W", 100), ("100w", 100), (150, 150), ("70.0", 70),
                                           ("", None), (None, None), ("abc", None), (float("nan"), None)])
def test_qa018_ler_potencia(valor, esperado):
    assert ler_potencia(valor) == esperado


@pytest.mark.defeito("DEF-07")
def test_qa019_ler_potencia_milhar_pt_br():
    """'1.000' (mil watts, notação pt-BR) vira 1 W."""
    assert ler_potencia("1.000") == 1000


@pytest.mark.defeito("DEF-08")
def test_qa020_xls_anunciado_mas_sem_xlrd():
    """A tela aceita .xls, mas o venv/requirements não têm xlrd: arquivo .xls real falha."""
    assinatura_ole = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1" + b"\x00" * 504
    try:
        _ler_planilha(assinatura_ole, "kobo.xls")
    except ImportError as erro:  # dependência ausente
        pytest.fail(f".xls não suportado de fato: {erro}")
    except Exception:
        pass  # qualquer outro erro = arquivo inválido, aceitável para bytes sintéticos


# ---------------------------------------------------------------- QA-025 fuso
@pytest.mark.parametrize("entrada,esperado", [
    ("2026-10-28 15:00:00", "2026-10-28 12:00"),            # SQLite (UTC, sem fuso)
    ("2026-10-28T15:00:00Z", "2026-10-28 12:00"),
    ("2026-10-28T15:00:00.12345+00:00", "2026-10-28 12:00"),  # Supabase (5 casas)
    ("2026-10-28T02:00:00+00:00", "2026-10-27 23:00"),      # vira o dia
    (datetime.datetime(2026, 10, 28, 15, 0), "2026-10-28 12:00"),
])
def test_qa025_para_local(entrada, esperado):
    dt = para_local(entrada)
    assert dt.strftime("%Y-%m-%d %H:%M") == esperado
    assert dt.utcoffset() == datetime.timedelta(hours=-3)


@pytest.mark.parametrize("entrada", [None, "", "ontem", "28/10/2026"])
def test_qa026_para_local_invalido(entrada):
    assert para_local(entrada) is None


# ---------------------------------------------------------------- QA-027 regra de status
@pytest.mark.parametrize("prioridades,esperado", [
    ([], "normal"), (iter([]), "normal"), (["Normal"], "chamado_aberto"), (["Alta", "Normal"], "chamado_aberto"),
    (["Normal", "Urgente"], "urgente"), ([None], "chamado_aberto"),
])
def test_qa027_status_pelas_ordens_abertas(prioridades, esperado):
    assert status_pelas_ordens_abertas(prioridades) == esperado


# ---------------------------------------------------------------- QA-028..030 rota / whatsapp / pendente
def test_qa028_link_rota():
    url = link_rota(-6.15, -35.61)
    assert url == "https://www.google.com/maps/dir/?api=1&destination=-6.15,-35.61"
    url = link_rota(None, None, "Rua São José & Cia #2", "Centro")
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert q["destination"] == ["Rua São José & Cia #2, Centro, Boa Saúde - RN"]
    # coordenada do centro conta como pendente -> usa endereço
    assert "Rua A" in urllib.parse.unquote(link_rota(-6.1611, -35.6025, "Rua A", "Centro"))


def test_qa029_whatsapp_caracteres_especiais():
    url = gerar_mensagem_whatsapp(
        "OS-2026-0001", "P-01 & #2", "Rua <São> José + 10%", "Bairro/Água", "Fiação \"rompida\"\n",
        "Urgente (Posto de Saúde / Centro / Risco)", "LED 100W", latitude=None, longitude=None,
        materiais=[{"item": "Relé 100–240V", "quantidade": 2}],
    )
    partes = urllib.parse.urlparse(url)
    assert (partes.scheme, partes.netloc, partes.path) == ("https", "wa.me", "/")
    assert " " not in url and "\n" not in url and "#" not in url and "&" not in url.split("?", 1)[1]
    texto = urllib.parse.parse_qs(partes.query)["text"][0]
    for trecho in ["P-01 & #2", "Rua <São> José + 10%", "2x Relé 100–240V", "🚨"]:
        assert trecho in texto
    # o link do Maps dentro da mensagem continua codificado e decodifica para o endereço
    link = texto.rsplit("\n", 1)[1]
    assert link.startswith("https://www.google.com/maps/dir/?api=1&destination=")
    assert urllib.parse.parse_qs(urllib.parse.urlparse(link).query)["destination"] == [
        "Rua <São> José + 10%, Bairro/Água, Boa Saúde - RN"]


def test_qa030_localizacao_pendente():
    assert localizacao_pendente({})
    assert localizacao_pendente({"latitude": "", "longitude": ""})
    assert localizacao_pendente({"latitude": -6.16112, "longitude": -35.60249})  # centro arredondado
    assert not localizacao_pendente({"latitude": "-6.15", "longitude": "-35.61"})


@pytest.mark.defeito("DEF-13")
def test_qa031_localizacao_pendente_nan_e_fora_da_faixa():
    """NaN/fora da faixa não é coordenada confiável, mas é tratada como localizada (vai ao mapa)."""
    assert localizacao_pendente({"latitude": math.nan, "longitude": math.nan})
    assert localizacao_pendente({"latitude": 200, "longitude": -35})


# ---------------------------------------------------------------- QA-035..039 paginação
@pytest.mark.parametrize("total,chamadas", [(0, 1), (999, 1), (1000, 2), (2500, 3)])
def test_qa035_paginacao(total, chamadas):
    fab = FakeConsultaPaginada(total)
    registros = buscar_todas_paginas(fab)
    assert len(registros) == total
    assert [r["id"] for r in registros] == list(range(total))
    assert len(fab.ranges) == chamadas
    assert fab.ranges[0] == (0, 999)


def test_qa036_paginacao_servidor_ignora_range():
    fab = FakeConsultaPaginada(5000, ignorar_range=True)
    with pytest.raises(RuntimeError, match="500 páginas"):
        buscar_todas_paginas(fab)
    assert len(fab.ranges) == MAXIMO_PAGINAS


@pytest.mark.defeito("DEF-12")
def test_qa037_paginacao_max_rows_menor_que_pagina():
    """Se o 'Max rows' do projeto for < 1000, a 1ª página curta encerra a busca e os dados somem em silêncio."""
    fab = FakeConsultaPaginada(2500, max_rows=500)
    assert len(buscar_todas_paginas(fab)) == 2500


# ---------------------------------------------------------------- QA-040..045 cache
@pytest.fixture
def relogio(monkeypatch):
    agora = [1000.0]
    monkeypatch.setattr(cache.time, "monotonic", lambda: agora[0])
    return agora


def test_qa040_cache_expira(relogio):
    chamadas = []

    @cache.cache_ttl(20)
    def f(x):
        chamadas.append(x)
        return len(chamadas)

    assert f(1) == 1 and f(1) == 1
    relogio[0] += 19.9
    assert f(1) == 1
    relogio[0] += 0.2
    assert f(1) == 2
    assert f(2) == 3  # argumento diferente = entrada diferente


def test_qa041_cache_limpar(relogio):
    cont = []

    @cache.cache_ttl()
    def f():
        cont.append(1)
        return len(cont)

    f()
    cache.limpar_cache()
    assert f() == 2


@pytest.mark.defeito("DEF-14")
def test_qa042_cache_args_nao_hashable(relogio):
    cont = []

    @cache.cache_ttl()
    def f(lista, opcoes=None):
        cont.append(1)
        return sum(lista)

    assert f([1, 2]) == 3 and f([1, 2]) == 3 and len(cont) == 1
    assert f([1, 2], opcoes={"a": 1}) == 3 and len(cont) == 2
    assert f([2, 1]) == 3 and len(cont) == 3


def test_qa043_cache_limite_de_entradas(relogio, monkeypatch):
    monkeypatch.setattr(cache, "MAXIMO_ENTRADAS", 3)

    @cache.cache_ttl()
    def f(x):
        return x

    for i in range(10):
        f(i)
    assert len(cache._entradas) <= 3


def test_qa044_cache_nao_guarda_excecao(relogio):
    cont = []

    @cache.cache_ttl()
    def f():
        cont.append(1)
        if len(cont) == 1:
            raise ValueError("falha")
        return "ok"

    with pytest.raises(ValueError):
        f()
    assert f() == "ok"


def test_qa045_cache_devolve_objeto_mutavel_compartilhado(relogio):
    """Documentado ('trate como somente-leitura'). Registrado como risco: mutação vaza entre sessões."""

    @cache.cache_ttl()
    def f():
        return [{"codigo": "P-01"}]

    f()[0]["codigo"] = "ALTERADO"
    assert f()[0]["codigo"] == "ALTERADO"  # confirma o compartilhamento (comportamento atual)


# ---------------------------------------------------------------- QA-046 planilha modelo
def test_qa046_planilha_modelo_reimporta():
    from app.dashboard.telas.importar_base import _planilha_modelo
    from app.importer import import_poles_file
    from app.servicos.dados_postes import obter_poste_por_codigo

    r = import_poles_file(_planilha_modelo(), "modelo_postes.xlsx")
    assert r["importados"] == 3 and r["erros"] == 0
    p = obter_poste_por_codigo("P-002")
    assert (p["tipo_luminaria"], p["potencia"], p["tipo_braco"]) == ("Vapor de Sódio", 70, "Braço Curto 1m")


# ---------------------------------------------------------------- QA-047 volume do mapa (medição)
def test_qa047_mapa_5000_postes_medicao(monkeypatch):
    import time
    from app.dashboard.telas import componentes_mapa as cm

    postes = [{"codigo": f"P{i}", "logradouro": "Rua", "bairro": "B", "status": "normal",
               "latitude": -6.1 - i * 1e-5, "longitude": -35.6, "tipo_luminaria": "LED", "potencia": 100}
              for i in range(5000)]
    cap = {}
    monkeypatch.setattr(cm.components, "html", lambda h, height=None: cap.setdefault("h", h))
    t0 = time.perf_counter()
    cm.renderizar_mapa_folium(postes, [-6.15, -35.6], 15, "Ruas")
    dt = time.perf_counter() - t0
    print(f"MAPA 5000 postes: {dt:.2f}s, HTML {len(cap['h']) / 1e6:.1f} MB")
    assert dt < 30
