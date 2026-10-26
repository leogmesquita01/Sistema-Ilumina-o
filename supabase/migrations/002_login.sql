-- ============================================================================
-- 002_login.sql — login com Supabase Auth, protocolo pelo banco e ajustes de dados
-- ============================================================================
-- O que muda:
--   1) Tabela public.perfis: quem pode usar o sistema. Só usuário com perfil
--      ATIVO lê ou grava. Criar a conta no Auth não basta — isso protege mesmo
--      se o cadastro público ficar ligado por engano.
--   2) RLS: sai a leitura pública (anon) e entra leitura/escrita para a equipe.
--      O app deixa de usar a chave secreta.
--   3) Protocolo da O.S. gerado pelo banco a partir do id (sem repetição).
--   4) Coordenada opcional: poste sem localização passa a ter latitude NULL em
--      vez do ponto fixo do centro da cidade.
--   5) Status: "defeito_urgente" vira "urgente" (um só nome para a mesma coisa).
--   6) ordens_servico.criado_por: quem abriu cada O.S.
--
-- Como aplicar: Supabase Dashboard -> SQL Editor -> cole e rode (Ctrl+Enter).
-- É idempotente: pode rodar mais de uma vez.
--
-- DEPOIS de rodar, ainda no painel:
--   a) Authentication -> Sign In / Providers -> Email: DESLIGUE
--      "Allow new users to sign up".
--   b) Authentication -> Users -> "Add user": crie a conta (e-mail + senha,
--      marque "Auto Confirm User").
--   c) Rode o bloco "CADASTRAR USUÁRIO" no fim deste arquivo para cada pessoa.
-- ============================================================================

-- 1) Perfis -------------------------------------------------------------------
create table if not exists public.perfis (
  id        uuid primary key references auth.users (id) on delete cascade,
  nome      text not null default '',
  papel     text not null default 'operador' check (papel in ('admin', 'operador')),
  ativo     boolean not null default true,
  criado_em timestamptz not null default now()
);

alter table public.perfis enable row level security;
-- Só leitura pelo app (o RLS abaixo limita ao próprio perfil). Cadastro de
-- perfis é feito pelo administrador no SQL Editor.
revoke all on public.perfis from anon, authenticated;
grant select on public.perfis to authenticated;

drop policy if exists "ve o proprio perfil" on public.perfis;
create policy "ve o proprio perfil"
  on public.perfis for select to authenticated
  using (id = auth.uid());

-- security definer: consegue ler perfis sem depender das policies da tabela.
create or replace function public.usuario_ativo()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (select 1 from public.perfis where id = auth.uid() and ativo);
$$;

revoke all on function public.usuario_ativo() from public;
grant execute on function public.usuario_ativo() to authenticated;

-- 2) RLS das tabelas do sistema ------------------------------------------------
alter table public.postes         enable row level security;
alter table public.ordens_servico enable row level security;

drop policy if exists "leitura publica postes" on public.postes;
drop policy if exists "leitura publica ordens" on public.ordens_servico;

drop policy if exists "equipe le postes" on public.postes;
create policy "equipe le postes" on public.postes
  for select to authenticated using (public.usuario_ativo());

drop policy if exists "equipe cadastra postes" on public.postes;
create policy "equipe cadastra postes" on public.postes
  for insert to authenticated with check (public.usuario_ativo());

drop policy if exists "equipe altera postes" on public.postes;
create policy "equipe altera postes" on public.postes
  for update to authenticated using (public.usuario_ativo()) with check (public.usuario_ativo());

drop policy if exists "equipe le ordens" on public.ordens_servico;
create policy "equipe le ordens" on public.ordens_servico
  for select to authenticated using (public.usuario_ativo());

drop policy if exists "equipe abre ordens" on public.ordens_servico;
create policy "equipe abre ordens" on public.ordens_servico
  for insert to authenticated with check (public.usuario_ativo());

drop policy if exists "equipe altera ordens" on public.ordens_servico;
create policy "equipe altera ordens" on public.ordens_servico
  for update to authenticated using (public.usuario_ativo()) with check (public.usuario_ativo());

-- Nenhuma policy de DELETE: apagar continua só pelo painel/chave secreta.

-- 3) Protocolo gerado pelo banco ----------------------------------------------
-- Usa o id da linha, que é único. Num BEFORE INSERT o id já foi preenchido
-- pelo default. Protocolos antigos (COUNT+1) nunca passam do próprio id, então
-- não há colisão com os novos.
create or replace function public.gerar_protocolo_os()
returns trigger
language plpgsql
as $$
begin
  if new.protocolo is null or new.protocolo = '' then
    new.protocolo := 'OS-'
      || to_char(now() at time zone 'America/Fortaleza', 'YYYY')
      || '-' || lpad(new.id::text, 4, '0');
  end if;
  return new;
end;
$$;

drop trigger if exists trg_gerar_protocolo_os on public.ordens_servico;
create trigger trg_gerar_protocolo_os
  before insert on public.ordens_servico
  for each row execute function public.gerar_protocolo_os();

-- 4) Coordenada opcional -------------------------------------------------------
alter table public.postes alter column latitude  drop not null;
alter table public.postes alter column longitude drop not null;

update public.postes
   set latitude = null, longitude = null
 where round(latitude::numeric, 4)  = -6.1611
   and round(longitude::numeric, 4) = -35.6025;

-- 5) Status padronizado --------------------------------------------------------
update public.postes set status = 'urgente' where status = 'defeito_urgente';

alter table public.postes drop constraint if exists postes_status_valido;
alter table public.postes
  add constraint postes_status_valido
  check (status in ('normal', 'chamado_aberto', 'urgente')) not valid;

-- 6) Quem abriu a O.S. ---------------------------------------------------------
alter table public.ordens_servico
  add column if not exists criado_por uuid default auth.uid() references auth.users (id);

-- ============================================================================
-- Conferência: devem aparecer as policies de perfis, postes e ordens_servico
-- ============================================================================
select tablename, policyname, cmd, roles
from pg_policies
where schemaname = 'public'
  and tablename in ('perfis', 'postes', 'ordens_servico')
order by tablename, cmd;

-- ============================================================================
-- CADASTRAR USUÁRIO (rode depois de criar a conta em Authentication -> Users)
-- Troque o e-mail e o nome. Papel: 'admin' ou 'operador'.
-- ============================================================================
-- insert into public.perfis (id, nome, papel)
-- select id, 'Nome da Pessoa', 'admin' from auth.users where email = 'pessoa@exemplo.com'
-- on conflict (id) do update set nome = excluded.nome, papel = excluded.papel, ativo = true;
--
-- Desativar alguém (sem apagar o histórico):
-- update public.perfis set ativo = false
--  where id = (select id from auth.users where email = 'pessoa@exemplo.com');
