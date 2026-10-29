-- ============================================================================
-- 005_area_admin.sql — área do administrador (out/2026)
-- ============================================================================
-- Só quem tem perfis.papel = 'admin' e ativo = true passa nas regras abaixo.
-- O app esconde a tela "Administração" de quem é operador, mas quem decide é o
-- banco: mesmo chamando a API direto, o operador é barrado.
--
-- 1) eh_admin(): quem é administrador.
-- 2) Equipe: admin lê e altera todos os perfis (nome, papel, ativo), vê as contas
--    criadas no Supabase Auth que ainda não têm perfil e as libera.
--    Trava: nunca fica sem nenhum administrador ativo.
-- 3) Ações sensíveis, só admin: excluir poste/O.S., renomear o código do poste,
--    corrigir protocolo e cancelar O.S.
-- 4) Histórico: quem criou, alterou ou excluiu postes, O.S. e perfis (antes e
--    depois). Só o admin lê; ninguém escreve direto, só os gatilhos.
--
-- Pré-requisito: 000–004 aplicadas (a 004 já deixa a FK com ON UPDATE CASCADE,
-- que faz a O.S. acompanhar o poste renomeado).
-- Como aplicar: Supabase Dashboard -> SQL Editor -> cole e rode. Idempotente.
-- ============================================================================

begin;

-- 1) Quem é admin ---------------------------------------------------------------
-- security definer: lê perfis sem passar pelas policies (evita recursão no RLS).
create or replace function public.eh_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (
    select 1 from public.perfis
    where id = (select auth.uid()) and papel = 'admin' and ativo
  );
$$;
revoke all on function public.eh_admin() from public, anon;
grant execute on function public.eh_admin() to authenticated;

-- 2) Equipe ---------------------------------------------------------------------
-- Só nome, papel e ativo podem mudar (o id nunca).
grant update (nome, papel, ativo) on public.perfis to authenticated;

drop policy if exists "admin le perfis" on public.perfis;
create policy "admin le perfis" on public.perfis
  for select to authenticated using ((select public.eh_admin()));

drop policy if exists "admin altera perfis" on public.perfis;
create policy "admin altera perfis" on public.perfis
  for update to authenticated
  using ((select public.eh_admin())) with check ((select public.eh_admin()));

create or replace function public.protege_ultimo_admin()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if old.papel = 'admin' and old.ativo and (new.papel <> 'admin' or not new.ativo)
     and not exists (select 1 from perfis where papel = 'admin' and ativo and id <> old.id) then
    raise exception 'Precisa existir pelo menos um administrador ativo.';
  end if;
  return new;
end $$;
drop trigger if exists trg_protege_ultimo_admin on public.perfis;
create trigger trg_protege_ultimo_admin before update on public.perfis
  for each row execute function public.protege_ultimo_admin();

-- Lista de contas (Auth + perfil). Contas sem perfil aparecem com liberado = false.
create or replace function public.listar_equipe()
returns table (
  id uuid, email text, nome text, papel text, ativo boolean, liberado boolean,
  criado_em timestamptz, ultimo_acesso timestamptz
)
language plpgsql stable security definer set search_path = public, auth as $$
begin
  if not public.eh_admin() then
    raise exception 'Só o administrador pode ver a equipe.' using errcode = '42501';
  end if;
  return query
    select u.id, u.email::text, coalesce(p.nome, ''), coalesce(p.papel, 'operador'),
           coalesce(p.ativo, false), p.id is not null, u.created_at, u.last_sign_in_at
      from auth.users u left join public.perfis p on p.id = u.id
     order by (p.id is null) desc, lower(coalesce(nullif(p.nome, ''), u.email));
end $$;
revoke all on function public.listar_equipe() from public, anon;
grant execute on function public.listar_equipe() to authenticated;

-- Dá acesso a uma conta do Auth (cria o perfil, ou reativa se já existir).
create or replace function public.liberar_usuario(p_id uuid, p_nome text, p_papel text default 'operador')
returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.eh_admin() then
    raise exception 'Só o administrador pode liberar usuários.' using errcode = '42501';
  end if;
  if p_papel not in ('admin', 'operador') then
    raise exception 'Papel inválido: %', p_papel;
  end if;
  insert into perfis (id, nome, papel, ativo) values (p_id, coalesce(p_nome, ''), p_papel, true)
  on conflict (id) do update set nome = excluded.nome, papel = excluded.papel, ativo = true;
end $$;
revoke all on function public.liberar_usuario(uuid, text, text) from public, anon;
grant execute on function public.liberar_usuario(uuid, text, text) to authenticated;

-- 3) Ações sensíveis ------------------------------------------------------------
-- 3a) Excluir: a 004 tirou o DELETE de todos; volta só para passar pela policy.
grant delete on public.postes, public.ordens_servico to authenticated;

drop policy if exists "admin exclui ordens" on public.ordens_servico;
create policy "admin exclui ordens" on public.ordens_servico
  for delete to authenticated using ((select public.eh_admin()));

drop policy if exists "admin exclui postes" on public.postes;
create policy "admin exclui postes" on public.postes
  for delete to authenticated using ((select public.eh_admin()));

-- 3b) Campos que só o admin muda. Uma função por tabela: em plpgsql, new.codigo
--     quebra quando a linha é de outra tabela.
create or replace function public.bloqueia_sensivel_postes()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if new.codigo is distinct from old.codigo and not public.eh_admin() then
    raise exception 'Só o administrador pode renomear o código do poste.';
  end if;
  return new;
end $$;
drop trigger if exists trg_sensivel_postes on public.postes;
create trigger trg_sensivel_postes before update on public.postes
  for each row execute function public.bloqueia_sensivel_postes();

create or replace function public.bloqueia_sensivel_ordens()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if public.eh_admin() then
    return new;
  end if;
  -- Renomear o poste propaga o código pela FK (cascade); isso é permitido.
  if new.protocolo is distinct from old.protocolo then
    raise exception 'Só o administrador pode corrigir o protocolo.';
  end if;
  if new.status = 'cancelada' and old.status is distinct from 'cancelada' then
    raise exception 'Só o administrador pode cancelar uma O.S.';
  end if;
  return new;
end $$;
drop trigger if exists trg_sensivel_ordens on public.ordens_servico;
create trigger trg_sensivel_ordens before update on public.ordens_servico
  for each row execute function public.bloqueia_sensivel_ordens();

-- 4) Histórico ------------------------------------------------------------------
create table if not exists public.historico (
  id bigint generated by default as identity primary key,
  em timestamptz not null default now(),
  usuario uuid default auth.uid() references auth.users (id) on delete set null,
  tabela text not null,
  acao text not null check (acao in ('INSERT', 'UPDATE', 'DELETE')),
  registro text,
  antes jsonb,
  depois jsonb
);
create index if not exists historico_em_idx on public.historico (em desc);
create index if not exists historico_usuario_idx on public.historico (usuario);
alter table public.historico enable row level security;

revoke all on public.historico from anon, authenticated;
grant select on public.historico to authenticated;

drop policy if exists "admin le historico" on public.historico;
create policy "admin le historico" on public.historico
  for select to authenticated using ((select public.eh_admin()));

create or replace function public.registra_historico()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  linha jsonb := coalesce(to_jsonb(new), to_jsonb(old));
begin
  insert into historico (tabela, acao, registro, antes, depois)
  values (
    tg_table_name, tg_op,
    case tg_table_name
      when 'postes' then linha ->> 'codigo'
      when 'ordens_servico' then linha ->> 'protocolo'
      else linha ->> 'id'
    end,
    case when tg_op <> 'INSERT' then to_jsonb(old) end,
    case when tg_op <> 'DELETE' then to_jsonb(new) end
  );
  return coalesce(new, old);
end $$;

drop trigger if exists trg_hist_postes on public.postes;
create trigger trg_hist_postes after insert or update or delete on public.postes
  for each row execute function public.registra_historico();
drop trigger if exists trg_hist_ordens on public.ordens_servico;
create trigger trg_hist_ordens after insert or update or delete on public.ordens_servico
  for each row execute function public.registra_historico();
drop trigger if exists trg_hist_perfis on public.perfis;
create trigger trg_hist_perfis after insert or update or delete on public.perfis
  for each row execute function public.registra_historico();

commit;

-- ============================================================================
-- Conferência
-- ============================================================================
-- Devem aparecer as policies "admin ..." em perfis, postes, ordens_servico e historico:
select tablename, policyname, cmd from pg_policies
 where schemaname = 'public' and policyname like 'admin %' order by 1, 2;
