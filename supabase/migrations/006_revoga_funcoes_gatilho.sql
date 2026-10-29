-- ============================================================================
-- 006_revoga_funcoes_gatilho.sql — avisos do Security Advisor após a 005
-- ============================================================================
-- As funções de gatilho da 005 ficaram executáveis via /rest/v1/rpc por anon e
-- authenticated (o Postgres dá EXECUTE a PUBLIC por padrão). Gatilho não precisa
-- desse privilégio para disparar, então ele sai de todo mundo.
-- eh_admin(), listar_equipe() e liberar_usuario() continuam para authenticated:
-- o app chama as duas últimas, e elas mesmas recusam quem não é admin.
-- Idempotente.
-- ============================================================================
revoke execute on function public.bloqueia_sensivel_ordens() from public, anon, authenticated;
revoke execute on function public.bloqueia_sensivel_postes() from public, anon, authenticated;
revoke execute on function public.protege_ultimo_admin() from public, anon, authenticated;
revoke execute on function public.registra_historico() from public, anon, authenticated;
