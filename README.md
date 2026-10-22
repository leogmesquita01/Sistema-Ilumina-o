# 💡 Ilumina Boa Saúde — Gestão e Mapa de Postes COSERN
### Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura

Sistema de georreferenciamento, busca instantânea por código de plaqueta da COSERN e emissão de ordens de serviço de manutenção com kit de equipamentos para viaturas de iluminação pública.

---

## 🚀 Como Executar o Aplicativo

Para iniciar o sistema localmente via Streamlit:

```bash
# 1. Ativar o ambiente virtual (se estiver usando venv):
.\.venv\Scripts\activate

# 2. Iniciar o dashboard Streamlit:
streamlit run app/dashboard/main.py
```

O aplicativo abrirá automaticamente no seu navegador em:
- **Painel:** `http://localhost:8501`

### Configuração do banco (Supabase)

Crie um arquivo `.env` na raiz (use o `.env.example` como modelo) com três variáveis:

| Variável | Chave | Uso |
|---|---|---|
| `SUPABASE_URL` | — | URL do projeto (não é segredo) |
| `SUPABASE_KEY` | `sb_publishable_...` | **Leitura** (`anon`), sujeita ao RLS |
| `SUPABASE_SECRET_KEY` | `sb_secret_...` | **Escrita** (`service_role`), ignora o RLS |

A chave secreta é usada apenas pelo Python no servidor (`obter_supabase_admin()`) e
nunca chega ao navegador. No Streamlit Community Cloud, cadastre as mesmas três em
**Settings → Secrets**.

A escrita anônima é bloqueada por RLS — as policies vivem em
[`supabase/migrations/001_rls.sql`](supabase/migrations/001_rls.sql) e devem ser
aplicadas uma vez no **SQL Editor** do painel Supabase.

---


## 🎯 Funcionalidades Principais

1. **Busca Instantânea por Código de Poste:**
   * Basta digitar o código da plaqueta (ex: `CSR-1001`, `CSR-1004` ou o nome de uma rua) na barra de pesquisa no topo.
   * O mapa navega automaticamente até o local exato e destaca o poste focado.

2. **Mapa Interativo (Ruas, Noturno e Satélite de Alta Resolução):**
   * Centrado no município de **Boa Saúde / RN** e suas comunidades rurais.
   * Alternância entre mapa de ruas (OpenStreetMap), modo noturno (Dark) e satélite (Esri World Imagery).
   * Agrupamento de marcadores (*clusters*) para alta performance mesmo com milhares de postes.
   * Cores indicativas de status:
     * 🟢 **Verde:** Funcionando normalmente
     * 🟡 **Amarelo:** Chamado de reparo aberto
     * 🔴 **Vermelho:** Defeito urgente (risco de curto, 24h aceso ou áreas prioritárias)

3. **Ficha Completa do Poste:**
   * Código da plaqueta da concessionária.
   * Logradouro, Bairro ou Comunidade Rural e Ponto de Referência.
   * Luminária atual (ex: LED 100W, Vapor de Sódio 70W) e potência.
   * Tipo de braço e estrutura do poste.
   * Botão direto **"Como Chegar (GPS)"** via Google Maps para guiar a viatura.

4. **Solicitação de Reparo com Kit de Equipamentos (O.S.):**
   * Seleção do defeito (lâmpada apagada, relé fotoelétrico colado, braço quebrado, fiação em curto).
   * Checklist de equipamentos necessários para a viatura levar (Lâmpada LED, Relé fotoelétrico, Braço 2m, Conectores perfurantes, etc.).
   * **Disparo no WhatsApp:** Gera uma mensagem pronta com protocolo, código do poste, rota GPS e lista de materiais para despachar com 1 clique.

5. **Importador da Base da COSERN / ANEEL:**
   * Upload de arquivos em **Excel (`.xlsx`, `.xls`)** ou **CSV**.
   * Identifica colunas automaticamente mesmo com nomes variados.
   * Atualiza ou cadastra milhares de postes em lote no Supabase / banco local.
   * Botão para download de planilha modelo pronta.

6. **GPS em Campo:**
   * Botão de localização GPS em tempo real para o fiscal ou eletricista se localizar pelo celular.

---

## 📁 Estrutura do Projeto

```
Web App Mapa/
│
├── .streamlit/
│   └── config.toml           # Configurações do tema e servidor Streamlit
│
├── app/
│   ├── dashboard/
│   │   ├── main.py           # Ponto de entrada principal da interface Streamlit
│   │   ├── estilos/          # Identidade visual em CSS modular
│   │   │   ├── base.py       # Reset, fontes, variáveis e layout
│   │   │   ├── sidebar.py    # Sidebar em ilhas flutuantes
│   │   │   ├── cards.py      # KPIs, gráficos e cartões
│   │   │   └── componentes.py # Painéis, tabelas, pills e inputs
│   │   └── telas/
│   │       ├── mapa_postes.py       # Mapa interativo em tempo real
│   │       ├── solicitar_reparo.py  # Emissão de O.S. e despacho WhatsApp
│   │       ├── ordens_servico.py    # Gestão e conclusão de chamados
│   │       ├── importar_base.py     # Upload e importação de planilhas
│   │       └── cadastrar_poste.py   # Cadastro avulso de postes
│   │
│   ├── database/
│   │   └── conexao.py        # Conexão Supabase Cloud + fallback SQLite
│   │
│   ├── servicos/
│   │   ├── dados_postes.py   # Consultas, métricas e cadastro de postes
│   │   └── ordens_service.py # Gestão de O.S. e formatação de WhatsApp
│   │
│   ├── importer.py           # Leitura e mapeamento de planilhas Excel/CSV
│   └── fuso.py               # Datas no fuso de Boa Saúde/RN (America/Fortaleza)
│
├── supabase/
│   └── migrations/
│       └── 001_rls.sql       # RLS: leitura pública, escrita só via chave secreta
│
├── data/
│   └── postes_boasaude.db    # Banco SQLite local de fallback
│
├── .env.example              # Modelo das variáveis de ambiente
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação
```

---

## 🏛️ Como obter a Base de Postes da COSERN para Boa Saúde/RN

1. **Via Ofício Institucional:**
   * A Secretaria de Obras/Infraestrutura de Boa Saúde/RN envia um ofício simples para o setor de **Poder Público da Neoenergia Cosern** solicitando:
     > *"Planilha eletrônica (Excel/CSV) cadastral contendo a relação dos ativos de iluminação pública e postes do município de Boa Saúde/RN, com número de barramento/plaqueta, logradouros, coordenadas geográficas e tipo de luminária instalada."*
   * Ao receber a planilha, acesse a tela **"Importar base COSERN"** e carregue o arquivo.

2. **Via Portal de Dados Abertos da ANEEL:**
   * Acesso: [Portal de Dados Abertos ANEEL](https://dadosabertos-aneel.opendata.arcgis.com/)
   * Baixar o conjunto **BDGD Neoenergia Cosern** (camadas `PONNOT` e `LIP`).
