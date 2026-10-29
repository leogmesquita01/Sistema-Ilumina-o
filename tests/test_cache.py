"""Cache por usuário e sem dado velho depois de uma escrita."""
import threading

from app import cache


def test_leitura_lenta_iniciada_antes_da_escrita_nao_volta_ao_cache():
    chamadas = []
    entrou = threading.Event()
    liberar = threading.Event()

    @cache.cache_ttl(60)
    def ler():
        chamadas.append(1)
        if len(chamadas) == 1:
            entrou.set()
            liberar.wait(5)  # leitura lenta, "antes" da escrita
            return "velho"
        return "novo"

    t = threading.Thread(target=ler)
    t.start()
    assert entrou.wait(5)
    cache.limpar_cache()  # escrita acontece enquanto a leitura ainda está em andamento
    liberar.set()
    t.join()
    assert ler() == "novo"


def test_argumento_lista_nao_quebra_o_cache():
    @cache.cache_ttl(60)
    def soma(valores):
        return sum(valores)

    assert soma([1, 2]) == 3 and soma([1, 2]) == 3
