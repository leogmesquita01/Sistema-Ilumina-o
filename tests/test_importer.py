import io

import pandas as pd

from app.importer import identify_columns, import_poles_file, ler_coordenadas, limpar_codigo
from app.servicos.dados_postes import (
    atualizar_status_poste,
    definir_localizacao_poste,
    obter_poste_por_codigo,
)


def _csv(linhas):
    buffer = io.StringIO()
    pd.DataFrame(linhas).to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# --- detecção de colunas -----------------------------------------------------

def test_tipo_poste_nao_vira_codigo():
    mapa = identify_columns(["Plaqueta", "Tipo Poste", "Rua"])
    assert mapa["codigo"] == "Plaqueta"
    assert mapa["tipo_poste"] == "Tipo Poste"


def test_ponto_de_referencia_nao_vira_codigo():
    mapa = identify_columns(["Código", "Ponto de Referência"])
    assert mapa["codigo"] == "Código"
    assert mapa["referencia"] == "Ponto de Referência"


def test_sinonimo_curto_so_casa_exato():
    # "x", "y" e "w" não podem casar com qualquer coluna que contenha a letra
    mapa = identify_columns(["codigo", "taxa_y", "complexo", "wifi"])
    assert "latitude" not in mapa
    assert "longitude" not in mapa
    assert "potencia" not in mapa


def test_exportacao_kobo():
    colunas = [
        "start", "end", "Código da plaqueta", "Rua", "Bairro", "Tipo de luminária",
        "Potência", "localizacao", "_localizacao_latitude", "_localizacao_longitude",
        "_localizacao_altitude", "_localizacao_precision", "Foto do poste", "_id", "_uuid",
    ]
    mapa = identify_columns(colunas)
    assert mapa["codigo"] == "Código da plaqueta"
    assert mapa["latitude"] == "_localizacao_latitude"
    assert mapa["longitude"] == "_localizacao_longitude"
    assert mapa["logradouro"] == "Rua"
    assert mapa["tipo_luminaria"] == "Tipo de luminária"
    assert mapa["potencia"] == "Potência"


def test_coluna_nao_e_usada_duas_vezes():
    mapa = identify_columns(["codigo", "poste"])
    assert list(mapa.values()).count("codigo") <= 1
    assert mapa["codigo"] == "codigo"


# --- limpeza de valores ------------------------------------------------------

def test_codigo_numerico_do_excel():
    assert limpar_codigo(1001.0) == "1001"
    assert limpar_codigo(" P-01 ") == "P-01"
    assert limpar_codigo(float("nan")) is None


def test_coordenadas():
    assert ler_coordenadas("-6,15", "-35,60")[:2] == (-6.15, -35.6)
    assert ler_coordenadas(None, None) == (None, None, None)
    assert ler_coordenadas("abc", "-35")[0] is None
    assert ler_coordenadas(200, -35)[0] is None
    assert ler_coordenadas(0, 0)[0] is None


# --- gravação ----------------------------------------------------------------

def test_reimportar_preserva_status_e_localizacao():
    import_poles_file(_csv([{"codigo": "P-01", "rua": "Rua A", "bairro": "Centro"}]), "a.csv")
    atualizar_status_poste("P-01", "urgente")
    definir_localizacao_poste("P-01", -6.15, -35.61)

    resultado = import_poles_file(_csv([{"codigo": "P-01", "rua": "Rua Nova", "bairro": "Centro"}]), "b.csv")

    poste = obter_poste_por_codigo("P-01")
    assert resultado["importados"] == 1
    assert poste["logradouro"] == "Rua Nova"
    assert poste["status"] == "urgente"
    assert (poste["latitude"], poste["longitude"]) == (-6.15, -35.61)


def test_reimportar_com_coordenada_valida_atualiza():
    import_poles_file(_csv([{"codigo": "P-02", "latitude": -6.1, "longitude": -35.5}]), "a.csv")
    import_poles_file(_csv([{"codigo": "P-02", "latitude": -6.2, "longitude": -35.7}]), "b.csv")
    poste = obter_poste_por_codigo("P-02")
    assert (poste["latitude"], poste["longitude"]) == (-6.2, -35.7)


def test_celula_vazia_nao_apaga_dado_existente():
    import_poles_file(_csv([{"codigo": "P-03", "rua": "Rua A", "bairro": "Bela Vista"}]), "a.csv")
    import_poles_file(_csv([{"codigo": "P-03", "rua": "Rua B", "bairro": None}]), "b.csv")
    poste = obter_poste_por_codigo("P-03")
    assert poste["logradouro"] == "Rua B"
    assert poste["bairro"] == "Bela Vista"


def test_poste_novo_sem_coordenada_fica_pendente():
    import_poles_file(_csv([{"codigo": "P-04"}]), "a.csv")
    poste = obter_poste_por_codigo("P-04")
    assert poste["latitude"] is None
    assert poste["status"] == "normal"


def test_codigo_repetido_na_planilha():
    resultado = import_poles_file(_csv([{"codigo": "P-05", "rua": "A"}, {"codigo": "P-05", "rua": "B"}]), "a.csv")
    assert resultado["importados"] == 1
    assert resultado["duplicados"] == 1
    assert obter_poste_por_codigo("P-05")["logradouro"] == "B"
