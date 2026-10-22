-- ============================================================================
-- 001_rls.sql — fecha a escrita anônima no banco do Ilumina Boa Saúde
-- ============================================================================
-- Contexto: a chave publishable (sb_publishable_...) fica exposta de propósito no
-- código do app. Sem Row Level Security, qualquer pessoa que a encontre consegue
-- INSERT/UPDATE/DELETE em todas as linhas do projeto.
--
-- Depois deste script:
--   * anon/authenticated -> apenas SELECT (o app lê com a chave publishable)
--   * service_role       -> continua escrevendo (a chave SECRETA, usada somente no
--                           servidor via obter_supabase_admin(), ignora o RLS)
--
-- Como aplicar: Supabase Dashboard -> SQL Editor -> cole e rode (Ctrl+Enter).
-- É idempotente: pode rodar mais de uma vez sem erro.
-- ============================================================================

-- 1) Liga o RLS nas tabelas do app.
alter table public.postes         enable row level security;
alter table public.ordens_servico enable row level security;

-- 2) Leitura pública. O app precisa ler os postes e o histórico de O.S. com a
--    chave publishable, e esses dados não são sigilosos.
drop policy if exists "leitura publica postes" on public.postes;
create policy "leitura publica postes"
  on public.postes
  for select
  to anon, authenticated
  using (true);

drop policy if exists "leitura publica ordens" on public.ordens_servico;
create policy "leitura publica ordens"
  on public.ordens_servico
  for select
  to anon, authenticated
  using (true);

-- 3) Nenhuma policy de INSERT/UPDATE/DELETE é criada de propósito.
--    Com RLS ligado e sem policy, anon/authenticated recebem
--    "new row violates row-level security policy" (SQLSTATE 42501) ao tentar gravar.

-- ============================================================================
-- 4) Conferência (a saída deve listar exatamente as 2 policies de SELECT)
-- ============================================================================
select
  c.relname                              as tabela,
  c.relrowsecurity                       as rls_ligado,
  coalesce(p.policyname, '(sem policy)') as policy,
  p.cmd                                  as comando
from pg_class c
left join pg_policies p
       on p.schemaname = 'public'
      and p.tablename = c.relname
where c.relnamespace = 'public'::regnamespace
  and c.relname in ('postes', 'ordens_servico')
order by c.relname, p.cmd, p.policyname;
