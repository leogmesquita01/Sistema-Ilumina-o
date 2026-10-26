import re
import urllib.parse

from app.constantes import CENTRO_MUNICIPIO
from app.fuso import agora_local
from app.servicos.dados_postes import cadastrar_poste, localizacao_pendente, obter_poste_por_codigo
from app.servicos.ordens_service import (
    concluir_ordem_servico,
    criar_ordem_servico,
    gerar_mensagem_whatsapp,
    link_rota,
    listar_ordens,
    status_pelas_ordens_abertas,
)


def _poste(codigo="P-01"):
    cadastrar_poste({"codigo": codigo, "logradouro": "Rua A", "bairro": "Centro"})


def test_protocolo_tem_ano_atual_e_nao_repete():
    _poste()
    p1 = criar_ordem_servico("P-01", "Lâmpada apagada")
    p2 = criar_ordem_servico("P-01", "Relé colado")
    ano = agora_local().year
    assert re.fullmatch(rf"OS-{ano}-\d{{4}}", p1)
    assert p1 != p2


def test_protocolo_nao_repete_apos_exclusao():
    from app.database.conexao import obter_conexao

    _poste()
    criar_ordem_servico("P-01", "A")
    p2 = criar_ordem_servico("P-01", "B")
    conn = obter_conexao()
    conn.execute("DELETE FROM ordens_servico WHERE protocolo != ?;", (p2,))
    conn.commit()
    conn.close()
    p3 = criar_ordem_servico("P-01", "C")  # COUNT(*)+1 geraria o mesmo número de p2
    assert p3 != p2


def test_status_do_poste_segue_as_ordens_abertas():
    _poste()
    urgente = criar_ordem_servico("P-01", "Fiação em curto", prioridade="Urgente")
    normal = criar_ordem_servico("P-01", "Lâmpada apagada", prioridade="Normal")
    assert obter_poste_por_codigo("P-01")["status"] == "urgente"

    concluir_ordem_servico(urgente)
    assert obter_poste_por_codigo("P-01")["status"] == "chamado_aberto"  # ainda há uma aberta

    concluir_ordem_servico(normal)
    assert obter_poste_por_codigo("P-01")["status"] == "normal"


def test_regra_de_status():
    assert status_pelas_ordens_abertas([]) == "normal"
    assert status_pelas_ordens_abertas(["Normal", "Alta"]) == "chamado_aberto"
    assert status_pelas_ordens_abertas(["Normal", "Urgente"]) == "urgente"


def test_listar_ordens_traz_materiais():
    _poste()
    criar_ordem_servico("P-01", "X", materiais=[{"item": "Relé", "quantidade": 2}])
    ordens = listar_ordens()
    assert ordens[0]["materiais_lista"] == [{"item": "Relé", "quantidade": 2}]


def test_localizacao_pendente():
    assert localizacao_pendente({"latitude": None, "longitude": None})
    assert localizacao_pendente({"latitude": CENTRO_MUNICIPIO[0], "longitude": CENTRO_MUNICIPIO[1]})
    assert not localizacao_pendente({"latitude": -6.15, "longitude": -35.61})


def test_link_rota():
    assert "destination=-6.15,-35.61" in link_rota(-6.15, -35.61)
    por_endereco = urllib.parse.unquote(link_rota(None, None, "Rua A", "Centro"))
    assert "Rua A, Centro, Boa Saúde - RN" in por_endereco


def test_whatsapp_usa_coordenada_quando_existe():
    url = gerar_mensagem_whatsapp("OS-1", "P-01", "Rua A", "Centro", "X", "Normal", "LED 100W",
                                  latitude=-6.15, longitude=-35.61)
    assert "-6.15%2C-35.61" in url or "-6.15,-35.61" in urllib.parse.unquote(url)
