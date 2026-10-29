// Edge Function "criar-membro": o administrador cria a conta de alguém da equipe
// direto pelo app (tela Admin → Equipe), sem abrir o painel do Supabase.
//
// Segurança
// - Quem chama precisa estar logado E ser admin: a conferência usa o token DELE na
//   função eh_admin() do banco (migração 005). Por isso o deploy é com
//   --no-verify-jwt: a própria função valida o token pelo banco.
//
// Deploy: supabase functions deploy criar-membro --no-verify-jwt
// - A chave service_role só existe aqui dentro (variável de ambiente que o próprio
//   Supabase injeta). Ela nunca vai para o app nem para o repositório.
// - O perfil é criado com liberar_usuario() usando o token do admin, então o
//   histórico registra quem criou.
//
// Entrada (JSON): { email, nome, papel: "operador" | "admin", senha }
// Saída: 200 { id, email } | 4xx { error: "mensagem para o usuário" }
import { createClient } from "jsr:@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function resposta(corpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

const erro = (mensagem: string, status = 400) => resposta({ error: mensagem }, status);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return erro("Use POST.", 405);

  const url = Deno.env.get("SUPABASE_URL")!;
  const chaveAnon = Deno.env.get("SUPABASE_ANON_KEY")!;
  const chaveServico = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const autorizacao = req.headers.get("Authorization") ?? "";

  // Cliente com o token de quem chamou: tudo que ele fizer passa pelo RLS.
  const comoUsuario = createClient(url, chaveAnon, {
    global: { headers: { Authorization: autorizacao } },
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: ehAdmin, error: erroAdmin } = await comoUsuario.rpc("eh_admin");
  if (erroAdmin) return erro("Não foi possível conferir seu acesso. Entre novamente.", 401);
  if (!ehAdmin) return erro("Só o administrador pode adicionar membros.", 403);

  let dados: Record<string, unknown>;
  try {
    dados = await req.json();
  } catch {
    return erro("Corpo da requisição inválido.");
  }
  const email = String(dados.email ?? "").trim().toLowerCase();
  const nome = String(dados.nome ?? "").trim();
  const papel = String(dados.papel ?? "operador");
  const senha = String(dados.senha ?? "");

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return erro("E-mail inválido.");
  if (!nome) return erro("Informe o nome da pessoa.");
  if (papel !== "operador" && papel !== "admin") return erro("Papel inválido.");
  if (senha.length < 8) return erro("A senha provisória precisa ter pelo menos 8 caracteres.");

  const servico = createClient(url, chaveServico, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: criado, error: erroCriar } = await servico.auth.admin.createUser({
    email,
    password: senha,
    email_confirm: true, // o admin já conhece a pessoa: entra sem e-mail de confirmação
    user_metadata: { nome },
  });
  if (erroCriar || !criado?.user) {
    const texto = (erroCriar?.message ?? "").toLowerCase();
    if (texto.includes("already") || texto.includes("registered") || texto.includes("exists")) {
      return erro("Já existe uma conta com esse e-mail. Se ela estiver aguardando, use “Liberar acesso”.", 409);
    }
    if (texto.includes("password")) return erro("Senha recusada pelo Supabase (fraca demais ou vazada). Escolha outra.");
    return erro("Não foi possível criar a conta agora.", 500);
  }

  const { error: erroPerfil } = await comoUsuario.rpc("liberar_usuario", {
    p_id: criado.user.id,
    p_nome: nome,
    p_papel: papel,
  });
  if (erroPerfil) {
    // Sem perfil a conta não serve para nada: desfaz para não deixar conta órfã.
    await servico.auth.admin.deleteUser(criado.user.id);
    return erro("A conta foi criada, mas não deu para liberar o acesso. Nada foi salvo; tente de novo.", 500);
  }

  return resposta({ id: criado.user.id, email });
});
