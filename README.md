# 💡 Ilumina Boa Saúde — Gestão e Mapa de Postes COSERN
### Prefeitura Municipal de Boa Saúde / RN — Secretaria de Obras e Infraestrutura

Sistema de georreferenciamento, busca instantânea por código de plaqueta da COSERN e emissão de ordens de serviço de manutenção com kit de equipamentos para viaturas de iluminação pública.

---

## 🚀 Como Executar o Aplicativo

Para iniciar o sistema localmente via Streamlit:

```bash
# 1. Ativar o ambiente virtual (se estiver usando venv):
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate        # Linux / macOS

# 2. Iniciar o dashboard Streamlit:
streamlit run app/dashboard/main.py
```

O aplicativo abrirá automaticamente no seu navegador em:
- **Painel:** `http://localhost:8501`

### Configuração do banco (Supabase)

Crie um arquivo `.env` na raiz (use o `.env.example` como modelo):

| Variável | Valor | Uso |
|---|---|---|
| `SUPABASE_URL` | `https://...supabase.co` | URL do projeto (não é segredo) |
| `SUPABASE_KEY` | `sb_publishable_...` | Chave publicável. O login de cada usuário passa por ela |
| `ILUMINA_MODO_LOCAL` | `0` ou `1` | `1` = só SQLite local, sem login (desenvolvimento) |

No Streamlit Community Cloud, cadastre as mesmas variáveis em **Settings → Secrets**.
O app **não usa** a chave secreta (`sb_secret_...`): cada pessoa entra com a própria
conta e o RLS do banco decide o que ela pode fazer.

### Primeira configuração do login (uma vez só)

1. No painel do Supabase, abra o **SQL Editor** e rode, nesta ordem, os arquivos de
   [`supabase/migrations/`](supabase/migrations/): `000_esquema_base.sql` (só em banco
   novo — cria as tabelas), `001_rls.sql`, `002_login.sql`, `003_ajustes_seguranca.sql`
   `004_ajustes_auditoria.sql` e `005_area_admin.sql`. Todos podem ser rodados de novo sem erro.
2. **Authentication → Sign In / Providers → Email**: desligue
   *"Allow new users to sign up"* (só o administrador cria contas).
3. **Authentication → Users → Add user**: crie a conta com e-mail e senha e marque
   *Auto Confirm User*.
4. Libere a **primeira** conta de administrador rodando no SQL Editor (troque nome e e-mail).
   As próximas o administrador libera pelo próprio app, na tela **Admin → Equipe**:

   ```sql
   insert into public.perfis (id, nome, papel)
   select id, 'Nome da Pessoa', 'admin' from auth.users where email = 'pessoa@exemplo.com'
   on conflict (id) do update set nome = excluded.nome, papel = excluded.papel, ativo = true;
   ```

Uma conta sem linha em `perfis` (ou com `ativo = false`) não consegue ler nem gravar
nada, mesmo que exista no Auth.

### Área do administrador (tela Admin)

Só aparece para quem tem papel `admin`, e o banco (migração 005) barra o operador
mesmo fora do app:

- **Equipe**: ver quem tem acesso, trocar papel, desativar e liberar contas novas do Auth.
- **Ações sensíveis**: renomear código de poste (as O.S. acompanham), excluir poste sem
  O.S., cancelar O.S. com motivo, corrigir protocolo e excluir O.S.
- **Histórico**: quem criou, alterou ou excluiu postes, O.S. e usuários (gravado por gatilho).
- **Backup**: planilha Excel com todos os postes e todas as O.S.

> Recarregar a página (F5) encerra a sessão e pede login de novo. O token é renovado
> enquanto a aba está em uso; uma aba parada por muito tempo pede login de novo.

### Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Os testes rodam sem internet: o modo local usa um SQLite temporário e
`tests/auditoria/` simula o Supabase com um cliente falso
(`tests/auditoria/fake_supabase.py`). Defeitos conhecidos e ainda não corrigidos
ficam listados em `PENDENTES` (`tests/auditoria/conftest.py`) como *xfail* estrito.

---

## 🎯 Funcionalidades Principais

1. **Busca Instantânea por Código de Poste:**
   * Basta digitar o código da plaqueta (ex: `P-01` ou o nome de uma rua) na barra de pesquisa no topo.
   * O mapa navega automaticamente até o local exato e destaca o poste focado.

2. **Mapa Interativo (Ruas, Noturno e Satélite de Alta Resolução):**
   * Centrado no município de **Boa Saúde / RN** e suas comunidades rurais.
   * Alternância entre mapa de ruas (OpenStreetMap), modo noturno (Dark) e satélite (Esri World Imagery).
   * Agrupamento de marcadores (*clusters*) para alta performance mesmo com milhares de postes.
   * Cores indicativas de status:
     * ⬛ **Preto:** Funcionando normalmente
     * 🟧 **Âmbar:** Chamado de reparo aberto
     * 🟥 **Vermelho:** Defeito urgente (risco de curto, 24h aceso ou áreas prioritárias)
   * Situação sempre escrita ao lado da cor (legível para quem não distingue cores).

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
   * Upload de arquivos em **Excel (`.xlsx`)** ou **CSV**.
   * Identifica colunas automaticamente mesmo com nomes variados.
   * Atualiza ou cadastra milhares de postes em lote no Supabase / banco local.
   * Reimportar é seguro: postes existentes **mantêm o status** (chamados abertos continuam
     abertos) e **mantêm a localização**, a menos que a planilha traga coordenada válida.
   * Aceita a exportação do **KoboToolbox** (coleta offline em campo, com GPS).
   * Botão para download de planilha modelo pronta.

6. **GPS em Campo:**
   * Botão de localização GPS em tempo real para o fiscal ou eletricista se localizar pelo celular.

7. **Localização dos Postes (Georreferenciamento):**
   * **No cadastro:** mapa de satélite ao lado do formulário — clique no poste e a coordenada é gravada junto com a ficha. A marcação é opcional.
   * **Na tela "Localizar":** fila dos postes já cadastrados para corrigir ou completar a localização, um por vez.
   * Postes sem coordenada confiável ficam marcados como **"Localização pendente"** e **não aparecem no mapa** — em vez de serem empilhados no centro da cidade.
   * O cadastro em campo não exige GPS: anotar o código continua sendo suficiente, e a localização é resolvida depois no escritório.

---

## 📶 Coleta em campo sem internet (KoboToolbox)

Nas comunidades rurais não há sinal, então o levantamento dos postes é feito no
app **KoboCollect** (Android), que funciona offline — inclusive o GPS — e envia
tudo quando o celular volta a ter internet.

1. No [KoboToolbox](https://kf.kobotoolbox.org): **Novo projeto → Enviar um
   XLSForm** → escolha [`kobo/levantamento_postes.xlsx`](kobo/levantamento_postes.xlsx)
   e clique em **Implantar**.
2. No celular, instale o **KoboCollect**, conecte à conta e baixe o formulário
   (com internet, uma vez).
3. Em campo: um formulário por poste (código da plaqueta, GPS, foto, rua,
   bairro, luminária...). Fica salvo no celular.
4. Com internet: **Enviar formulários finalizados**.
5. No Kobo: **Dados → Downloads → XLS** e importe o arquivo na tela
   **"Importar planilha"** do Ilumina. Os postes já entram com a localização.

O importador aceita os dois formatos de cabeçalho do Kobo (rótulos ou valores
XML). Para mudar campos ou opções, edite `kobo/gerar_formulario.py` e rode
`python kobo/gerar_formulario.py` — as opções vêm de `app/constantes.py`, as
mesmas da tela de cadastro.

---

## 📁 Estrutura do Projeto

```
Sistema-Ilumina-o/
│
├── .streamlit/
│   └── config.toml           # Configurações do tema e servidor Streamlit
│
├── app/
│   ├── dashboard/
│   │   ├── main.py           # Ponto de entrada principal da interface Streamlit
│   │   ├── sessao.py         # Login (Supabase Auth) e sessão do usuário
│   │   ├── html_seguro.py    # Escape de texto antes de montar HTML
│   │   ├── ui.py             # Peças de interface (títulos, indicadores, painéis, status)
│   │   ├── estilos/
│   │   │   └── tema.py       # Tema "prancheta técnica" + animações de entrada (CSS)
│   │   └── telas/
│   │       ├── login.py             # Tela de login
│   │       ├── mapa_postes.py       # Mapa interativo em tempo real
│   │       ├── solicitar_reparo.py  # Emissão de O.S. e despacho WhatsApp
│   │       ├── ordens_servico.py    # Gestão e conclusão de chamados
│   │       ├── importar_base.py     # Upload e importação de planilhas
│   │       ├── cadastrar_poste.py   # Cadastro avulso de postes
│   │       └── localizacao_postes.py # Georreferenciamento no mapa de satélite
│   │
│   ├── database/
│   │   ├── conexao.py        # Supabase (cliente por sessão) ou SQLite no modo local
│   │   └── paginacao.py      # Paginação das consultas ao PostgREST
│   │
│   ├── servicos/
│   │   ├── dados_postes.py   # Consultas, métricas e cadastro de postes
│   │   └── ordens_service.py # Gestão de O.S. e formatação de WhatsApp
│   │
│   ├── constantes.py         # Status, prioridades e dados do município
│   ├── cache.py              # Cache TTL em memória, invalidado nas escritas
│   ├── importer.py           # Leitura e mapeamento de planilhas Excel/CSV
│   ├── fuso.py               # Datas no fuso de Boa Saúde/RN (America/Fortaleza)
│   └── erros.py              # Erros do banco traduzidos para o usuário
│
├── supabase/
│   └── migrations/
│       ├── 000_esquema_base.sql      # Tabelas postes e ordens_servico
│       ├── 001_rls.sql               # Liga o RLS nas tabelas
│       ├── 002_login.sql             # Perfis, RLS por usuário, protocolo e status
│       ├── 003_ajustes_seguranca.sql # Avisos do Security Advisor
│       ├── 004_ajustes_auditoria.sql # Código sem caixa, protocolo, permissões
│       └── 005_area_admin.sql        # Área do admin: equipe, ações sensíveis, histórico
│
├── kobo/                     # Formulário do KoboToolbox (coleta offline)
│   ├── gerar_formulario.py   # Gera o XLSForm a partir das constantes
│   └── levantamento_postes.xlsx
│
├── tests/                    # Testes (pytest)
│
├── data/
│   └── postes_boasaude.db    # SQLite do modo local (criado ao rodar com ILUMINA_MODO_LOCAL=1; fora do Git)
│
├── .env.example              # Modelo das variáveis de ambiente
├── requirements.txt          # Dependências do projeto (versões fixas)
├── requirements-dev.txt      # + ferramentas de teste
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
