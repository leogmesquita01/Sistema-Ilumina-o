-- ============================================================================
-- 003_ajustes_seguranca.sql — avisos do Security Advisor do Supabase após a 002
-- ============================================================================
-- 1) gerar_protocolo_os sem search_path fixo (lint 0011).
-- 2) usuario_ativo() executável pelo papel anon (lint 0028). O Supabase dá
--    EXECUTE ao anon por padrão em funções novas; aqui isso é retirado.
--    O papel authenticated PRECISA manter o EXECUTE: as policies chamam essa
--    função com o token do usuário logado (o aviso 0029 é esperado).
-- Idempotente.
-- ============================================================================

alter function public.gerar_protocolo_os() set search_path = public;

revoke execute on function public.usuario_ativo() from anon;
grant execute on function public.usuario_ativo() to authenticated;
