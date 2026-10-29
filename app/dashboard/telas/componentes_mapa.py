"""Mapa da rede (folium) com milhares de postes.

Desempenho: antes, cada poste virava um ``folium.Marker`` com popup próprio, e o
HTML inteiro (≈1,8 KB por poste) era gerado e reenviado a cada clique em
qualquer controle da tela. Com 3.000 postes: ~4,6 s de CPU e 5,4 MB por clique.

Agora:
* ``FastMarkerCluster``: os postes vão como uma lista de dados (JSON) e os
  marcadores são criados no navegador por uma função JS;
* o HTML pronto fica guardado: se os postes, o centro, o zoom e a camada não
  mudaram, ele não é gerado de novo.

Segurança: os textos do banco entram só como dados JSON (o ``tojson`` do Jinja
escapa ``<``, ``>``, ``&`` e ``'``) e o popup é montado com ``textContent`` —
nada vindo do banco é interpretado como HTML ou JavaScript.
"""
import hashlib
import json
from collections import OrderedDict

import folium
import streamlit as st
from folium import plugins

from app.constantes import STATUS_CHAMADO, eh_urgente
from app.servicos.dados_postes import localizacao_pendente

URL_ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# Nome mostrado no controle da tela -> (tiles, atribuição)
CAMADAS = {
    "Ruas": ("OpenStreetMap", None),
    "Satélite": (URL_ESRI, "Esri World Imagery"),
    "Noturno": ("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", "CartoDB Dark"),
}

ALTURA_MAPA = 480

# HTMLs já gerados (poucos: um por combinação de filtro/camada recente).
_MAXIMO_GUARDADOS = 8
_guardados: "OrderedDict[str, str]" = OrderedDict()

# Recebe uma linha de `dados` e devolve o marcador. Textos via textContent.
_CALLBACK_JS = """
function callback(row) {
    var lat = row[0], lng = row[1], codigo = row[2], local = row[3],
        luminaria = row[4], situacao = row[5], cor = row[6], icone = row[7];
    var marker = L.marker([lat, lng], {
        icon: L.AwesomeMarkers.icon({icon: icone, prefix: 'fa', markerColor: cor, iconColor: 'white'})
    });

    var caixa = document.createElement('div');
    caixa.style.cssText = "font-family: 'IBM Plex Sans', system-ui, sans-serif; min-width: 190px; color: #15171A;";
    function linha(texto, estilo) {
        var d = document.createElement('div');
        d.style.cssText = estilo;
        d.textContent = texto;
        caixa.appendChild(d);
        return d;
    }
    linha(codigo, "font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 13px; margin-bottom: 2px;");
    linha(local, "font-size: 12px; color: #3F4448; margin-bottom: 6px;");
    var rodape = linha('', "border-top: 1px solid #E7E9E4; padding-top: 6px; font-size: 12px;");
    function campo(rotulo, valor) {
        var r = document.createElement('div');
        r.appendChild(document.createTextNode(rotulo + ': '));
        var b = document.createElement('b');
        b.textContent = valor;
        r.appendChild(b);
        rodape.appendChild(r);
    }
    campo('Luminária', luminaria);
    campo('Situação', situacao);

    marker.bindPopup(caixa, {maxWidth: 260});
    marker.bindTooltip(document.createTextNode(codigo + ' · ' + local));
    return marker;
}
"""


def _aparencia(status: str):
    """Cor do marcador, ícone e rótulo — no padrão preto/âmbar/vermelho do tema."""
    if eh_urgente(status):
        return "red", "exclamation", "Urgente"
    if status == STATUS_CHAMADO:
        return "orange", "warning", "Chamado aberto"
    return "black", "bolt", "Operacional"


def _texto(valor, padrao: str = "—") -> str:
    texto = "" if valor is None else str(valor).strip()
    return texto or padrao


def dados_dos_marcadores(postes: list) -> list:
    """Uma linha por poste com coordenada: [lat, lng, código, local, luminária, situação, cor, ícone]."""
    linhas = []
    for p in postes:
        # Postes sem coordenada confiável não entram: desenhá-los no ponto padrão
        # empilharia a base no centro da cidade. Eles ficam na tela "Localizar".
        if localizacao_pendente(p):
            continue
        cor, icone, rotulo = _aparencia(p.get("status"))
        linhas.append([
            float(p["latitude"]),
            float(p["longitude"]),
            _texto(p.get("codigo")),
            f"{_texto(p.get('logradouro'))} · {_texto(p.get('bairro'))}",
            f"{_texto(p.get('tipo_luminaria'))} {_texto(p.get('potencia') or 100)} W",
            rotulo,
            cor,
            icone,
        ])
    return linhas


def gerar_html_mapa(postes: list, centro_mapa: list, zoom_inicial: int, camada_padrao: str) -> str:
    """HTML completo do mapa. Guarda o resultado: mesma entrada → mesmo HTML, sem gerar de novo."""
    dados = dados_dos_marcadores(postes)
    chave = hashlib.sha256(
        json.dumps([dados, list(centro_mapa), zoom_inicial, camada_padrao], ensure_ascii=False).encode()
    ).hexdigest()
    if chave in _guardados:
        _guardados.move_to_end(chave)
        return _guardados[chave]

    m = folium.Map(location=centro_mapa, zoom_start=zoom_inicial, tiles=None, control_scale=True)
    for nome, (tiles, atribuicao) in CAMADAS.items():
        folium.TileLayer(
            tiles=tiles, attr=atribuicao, name=nome, overlay=False, control=True,
            show=(nome == camada_padrao),
        ).add_to(m)

    plugins.LocateControl(
        auto_start=False, position="topleft",
        strings={"title": "Minha localização"},
        locate_options={"enableHighAccuracy": True, "maxZoom": 18},
    ).add_to(m)
    plugins.FastMarkerCluster(dados, callback=_CALLBACK_JS, name="Postes").add_to(m)

    pagina = m.get_root().render()
    _guardados[chave] = pagina
    while len(_guardados) > _MAXIMO_GUARDADOS:
        _guardados.popitem(last=False)
    return pagina


def renderizar_mapa_folium(postes: list, centro_mapa: list, zoom_inicial: int, camada_padrao: str) -> None:
    _exibir_html(gerar_html_mapa(postes, centro_mapa, zoom_inicial, camada_padrao), ALTURA_MAPA)


def _exibir_html(conteudo: str, altura: int) -> None:
    # st.iframe substitui st.components.v1.html (depreciado no Streamlit 1.66).
    st.iframe(conteudo, height=altura)
