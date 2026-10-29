-- ============================================================================
-- 004_ajustes_auditoria.sql — correções de integridade da auditoria (out/2026)
-- ============================================================================
-- 1) Código do poste único SEM diferenciar maiúsculas: "P-01" e "p-01" passam a
--    ser o mesmo poste também para o banco (o app já trata assim).
-- 2) Protocolo da O.S.: lpad('10000', 4, '0') devolve '1000' (corta o número), o
--    que repetiria protocolos a partir da O.S. de id 10.000.
-- 3) Permissões: o papel anon (quem não fez login) perde todo acesso às tabelas;
--    authenticated fica só com SELECT/INSERT/UPDATE. O RLS continua valendo — é
--    uma segunda camada caso alguma policy seja alterada por engano.
-- 4) Valida o CHECK de status (criado como NOT VALID na 002).
-- 5) Índice em ordens_servico.criado_por (aviso de desempenho do Supabase).
-- 6) Policy de perfis com (select auth.uid()) (aviso de desempenho do Supabase).
-- 7) Apagar um poste não apaga mais o histórico de O.S. dele (ON DELETE RESTRICT).
--
-- Como aplicar: Supabase Dashboard -> SQL Editor -> cole e rode.
-- Idempotente. Se o passo 1 falhar, a base tem códigos repetidos só na caixa:
-- a consulta no fim do arquivo lista quais são.
-- ============================================================================

-- 1) Código único sem diferenciar maiúsculas -----------------------------------
create unique index if not exists postes_codigo_lower_key on public.postes (lower(codigo));

-- 2) Protocolo sem cortar números com 5+ dígitos ------------------------------
create or replace function public.gerar_protocolo_os()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  if new.protocolo is null or new.protocolo = '' then
    new.protocolo := 'OS-'
      || to_char(now() at time zone 'America/Fortaleza', 'YYYY')
      || '-' || case when new.id < 10000 then lpad(new.id::text, 4, '0') else new.id::text end;
  end if;
  return new;
end;
$$;

-- 3) Permissões mínimas --------------------------------------------------------
revoke all on public.postes, public.ordens_servico from anon;
revoke delete, truncate, references, trigger on public.postes, public.ordens_servico from authenticated;
grant select, insert, update on public.postes, public.ordens_servico to authenticated;

-- 4) CHECK de status validado --------------------------------------------------
alter table public.postes validate constraint postes_status_valido;

-- 5) Índice da FK criado_por -----------------------------------------------------
create index if not exists idx_os_criado_por on public.ordens_servico (criado_por);

-- 6) Policy de perfis avaliada uma vez por consulta ------------------------------
drop policy if exists "ve o proprio perfil" on public.perfis;
create policy "ve o proprio perfil"
  on public.perfis for select to authenticated
  using (id = (select auth.uid()));

-- 7) Histórico de O.S. protegido ------------------------------------------------
alter table public.ordens_servico drop constraint if exists ordens_servico_codigo_poste_fkey;
alter table public.ordens_servico
  add constraint ordens_servico_codigo_poste_fkey
  foreign key (codigo_poste) references public.postes (codigo)
  on update cascade on delete restrict;

-- ============================================================================
-- Conferência
-- ============================================================================
-- Códigos repetidos só na caixa (deve voltar vazio):
select lower(codigo) as codigo, array_agg(codigo) as grafias
  from public.postes group by lower(codigo) having count(*) > 1;

-- Permissões (anon não deve aparecer):
select table_name, grantee, string_agg(privilege_type, ', ' order by privilege_type) as privilegios
  from information_schema.role_table_grants
 where table_schema = 'public' and table_name in ('postes', 'ordens_servico')
   and grantee in ('anon', 'authenticated')
 group by table_name, grantee order by 1, 2;
