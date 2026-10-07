# 💡 Web App de Gestão e Mapa de Postes COSERN
### Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura

Sistema de georreferenciamento, busca instantânea por código de plaqueta da COSERN e emissão de ordens de serviço de manutenção com kit de equipamentos para viaturas de iluminação pública.

---

## 🚀 Como Executar o Aplicativo

Como todo o backend foi desenvolvido em **Python**, você só precisa de **um comando** para iniciar o sistema:

```bash
# 1. Ativar o ambiente virtual (opcional se já estiver ativo):
.\.venv\Scripts\activate

# 2. Iniciar o aplicativo:
python run.py
```

O aplicativo abrirá automaticamente no seu navegador em:
- **Painel do Mapa:** `http://127.0.0.1:8000`
- **Documentação Interativa da API (Swagger):** `http://127.0.0.1:8000/docs`

---

## 🎯 Funcionalidades Principais

1. **Busca Instantânea por Código de Poste:**
   * Basta digitar o código da plaqueta (ex: `CSR-1001`, `CSR-1004` ou o nome de uma rua) na barra de pesquisa no topo.
   * O mapa navega automaticamente até o local exato com animação e destaca o poste.

2. **Mapa Interativo (Ruas e Satélite de Alta Resolução):**
   * Centrado no município de **Boa Saúde / RN** e suas comunidades rurais.
   * Alternância com um clique entre mapa de ruas (OpenStreetMap) e satélite (Esri World Imagery).
   * Agrupamento de marcadores (*clusters*) para alta performance mesmo com milhares de postes.
   * Cores indicativas de status:
     * 🟢 **Verde:** Funcionando normalmente
     * 🟡 **Amarelo:** Chamado de reparo aberto
     * 🔴 **Vermelho:** Defeito urgente (risco de curto, 24h aceso ou áreas prioritárias)

3. **Ficha Completa do Poste:**
   * Código da plaqueta da concessionária.
   * Logradouro, Bairro ou Comunidade Rural e Ponto de Referência.
   * Luminária atual (ex: LED 100W, Vapor de Sódio 70W) e potência.
   * Tipo de braço e tipo de estrutura do poste.
   * Botão direto **"Como Chegar (Google Maps / Waze)"** para guiar a viatura até o poste.

4. **Solicitação de Reparo com Kit de Equipamentos (O.S.):**
   * Selecione o defeito (lâmpada apagada, relé fotoelétrico colado, braço quebrado, fiação em curto).
   * Checklist inteligente de equipamentos necessários para a viatura levar (Lâmpada LED, Relé fotoelétrico, Braço 2m, Conectores perfurantes, etc.).
   * **Disparo no WhatsApp:** Gera uma mensagem pronta com protocolo, código do poste, rota GPS e lista de materiais para enviar ao eletricista de plantão com 1 clique!
   * Impressão de ficha de serviço.

5. **Importador da Base da COSERN / ANEEL:**
   * Arraste e solte arquivos em **Excel (`.xlsx`, `.xls`)** ou **CSV**.
   * Identifica colunas automaticamente mesmo se os cabeçalhos mudarem de nome.
   * Atualiza ou cadastra milhares de postes em segundos no banco SQLite local.
   * Botão para baixar planilha modelo pronta.

6. **GPS em Campo:**
   * Botão "Minha Posição" para o fiscal ou eletricista se localizar no mapa pelo celular.

---

## 📁 Estrutura do Projeto (100% Legível em Python)

```
Web App Mapa/
│
├── .venv/                  # Ambiente virtual Python com bibliotecas instaladas
├── run.py                  # Script inicializador (abre o navegador e sobe o servidor)
├── requirements.txt        # Dependências Python (FastAPI, Uvicorn, Pandas, OpenpyXL)
├── README.md               # Manual de instruções
│
├── data/
│   └── postes_boasaude.db  # Banco de dados local SQLite (criado automaticamente)
│
└── app/
    ├── main.py             # Servidor FastAPI com rotas de API e arquivos estáticos
    ├── database.py         # Conexão SQLite e criação das tabelas e índices
    ├── models.py           # Modelos de validação de dados (Pydantic)
    ├── importer.py         # Algoritmo Python (Pandas) para ler planilhas da COSERN
    ├── seed_data.py        # Dados iniciais realistas de Boa Saúde/RN
    │
    └── static/             # Interface visual (Frontend)
        ├── index.html      # Página principal com mapa e painéis
        ├── css/
        │   └── style.css   # Estilos dos marcadores e animações
        └── js/
            ├── api.js      # Integração com o backend Python
            └── app.js      # Lógica do mapa Leaflet, busca, O.S. e WhatsApp
```

---

## 🏛️ Como obter a Base de Postes da COSERN para Boa Saúde/RN

1. **Via Ofício Institucional (Mais simples e direto):**
   * A Secretaria de Obras/Infraestrutura de Boa Saúde/RN envia um ofício simples para o setor de **Poder Público da Neoenergia Cosern** solicitando:
     > *"Planilha eletrônica (Excel/CSV) cadastral contendo a relação dos ativos de iluminação pública e postes do município de Boa Saúde/RN, com número de barramento/plaqueta, logradouros, coordenadas geográficas e tipo de luminária instalada."*
   * Ao receber a planilha, basta abrir o app, clicar em **"Importar COSERN"** e carregar o arquivo.

2. **Via Portal de Dados Abertos da ANEEL (Público):**
   * Acesso: [Portal de Dados Abertos ANEEL](https://dadosabertos-aneel.opendata.arcgis.com/)
   * Baixar o conjunto **BDGD Neoenergia Cosern**.
   * As camadas de interesse são `PONNOT` (Pontos Notáveis/Postes) e `LIP` (Iluminação Pública).
