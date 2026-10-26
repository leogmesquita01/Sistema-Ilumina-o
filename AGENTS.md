# AGENTS.md — convenções do projeto

## Commits

- **Sempre commitar** ao concluir qualquer alteração. Nunca deixar trabalho apenas
  no working tree.
- Um assunto por commit: correção de UI, refatoração de segurança e ajuste de dados
  não vão juntos.
- Mensagens em português, no padrão `tipo(escopo): resumo`
  (`feat`, `fix`, `perf`, `refactor`, `docs`, `style`, `chore`).
- **Não fazer `push`** sem pedido explícito: o repositório é público.

## Segredos

- O app **não usa** `SUPABASE_SECRET_KEY`: cada pessoa entra com a própria conta e o
  RLS (`supabase/migrations/002_login.sql`) decide o acesso. `obter_supabase_admin()`
  é só para scripts de manutenção e nunca deve ser chamada por uma tela.
- `SUPABASE_SECRET_KEY` e qualquer chave nunca entram no código nem em arquivo
  versionado. Ficam apenas no `.env` (local) e em `st.secrets` (Streamlit Cloud).
- Antes de commitar, conferir o diff em busca de chave real.

## Verificação antes de commitar

```bash
.venv\Scripts\python.exe -m compileall -q app
.venv\Scripts\python.exe -m pytest -q
```

Os testes rodam no modo local (SQLite temporário), sem internet e sem tocar no
Supabase. Os testes de tela (`tests/test_telas.py`) já usam o `AppTest`.

Para mudanças de UI ou de serviço, rodar as telas com
`streamlit.testing.v1.AppTest` (nenhuma exceção esperada):

```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("app/dashboard/main.py", default_timeout=120)
at.run()
```
