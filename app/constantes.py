"""Valores fixos do sistema, num lugar só.

Antes, o status "urgente" era gravado pelas O.S. enquanto o filtro do mapa
procurava "defeito_urgente", e a coordenada do centro aparecia repetida em vários
arquivos. Tudo o que é usado em mais de um módulo mora aqui.
"""

# --- Status do poste --------------------------------------------------------
STATUS_NORMAL = "normal"
STATUS_CHAMADO = "chamado_aberto"
STATUS_URGENTE = "urgente"

# Valor antigo, gravado por versões anteriores. A migração 002 converte para
# "urgente"; continua reconhecido aqui para bancos ainda não migrados.
STATUS_URGENTE_LEGADO = "defeito_urgente"

STATUS_EM_ALERTA = (STATUS_CHAMADO, STATUS_URGENTE, STATUS_URGENTE_LEGADO)


def eh_urgente(status) -> bool:
    return status in (STATUS_URGENTE, STATUS_URGENTE_LEGADO)


# --- Status e prioridade da O.S. --------------------------------------------
OS_ABERTA = "aberta"
OS_CONCLUIDA = "concluida"

PRIORIDADE_NORMAL = "Normal"
PRIORIDADE_ALTA = "Alta"
PRIORIDADE_URGENTE = "Urgente"

# --- Município (vira configuração por prefeitura na fase multi-prefeitura) ---
NOME_MUNICIPIO = "Boa Saúde"
UF_MUNICIPIO = "RN"
CENTRO_MUNICIPIO = (-6.1611, -35.6025)

# --- Mapas -------------------------------------------------------------------
URL_SATELITE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# --- Opções de cadastro (tela "Cadastrar poste" e formulário do Kobo) -------
LUMINARIAS = ["LED", "Vapor de Sódio", "Vapor de Mercúrio", "Sem Luminária"]
ESTRUTURAS = ["Concreto Duplo T", "Concreto Circular", "Madeira Tratada", "Metálico"]
BRACOS = ["Braço Médio 2m", "Braço Curto 1m", "Braço Longo 3m", "Pétala Dupla", "Topo de Poste"]
