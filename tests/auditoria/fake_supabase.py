"""Fake do cliente supabase-py (postgrest) para testes SEM rede.

* Builder encadeável: table().select().eq().neq().ilike().in_().or_().order()
  .range().limit().insert().update().upsert().execute().
* Guarda TODAS as chamadas em ``cliente.chamadas`` (tabela, ação, ops, payload).
* Mini banco em memória que imita o essencial do PostgREST/Postgres usado pelo
  app: UNIQUE case-sensitive em postes.codigo, FK ordens_servico.codigo_poste ->
  postes.codigo (case-sensitive), gatilho de protocolo, ``count=exact``,
  ``range`` e ``db-max-rows`` (``max_rows``), upsert com ``columns`` = união das
  chaves do lote (comportamento do postgrest-py 2.x com default_to_null=True).

Não reproduz RLS, tipos, nem a gramática completa do PostgREST: os testes que
dependem disso são marcados como BLOQUEADOS no relatório.
"""
import copy
import datetime
import re
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional


class FakeAPIError(Exception):
    """Imita postgrest.exceptions.APIError (a mensagem leva o código SQLSTATE)."""


DEFAULTS = {
    "postes": {
        "latitude": None, "longitude": None, "logradouro": None, "bairro": None, "referencia": None,
        "tipo_luminaria": "LED", "potencia": 100, "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m", "status": "normal", "observacoes": None,
    },
    "ordens_servico": {
        "prioridade": "Normal", "materiais": None, "solicitante": "Secretaria de Infraestrutura",
        "status": "aberta", "data_conclusao": None, "observacoes": None,
    },
}


def _like_para_regex(padrao: str) -> "re.Pattern":
    saida, i = [], 0
    while i < len(padrao):
        c = padrao[i]
        if c == "\\" and i + 1 < len(padrao):
            saida.append(re.escape(padrao[i + 1]))
            i += 2
            continue
        if c in "%*":
            saida.append(".*")
        elif c == "_":
            saida.append(".")
        else:
            saida.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(saida) + "$", re.IGNORECASE | re.DOTALL)


class FakeQuery:
    def __init__(self, cliente: "FakeSupabase", tabela: str):
        self.cliente = cliente
        self.tabela = tabela
        self.ops: List[tuple] = []
        self.acao = "select"
        self.payload: Any = None
        self.colunas = "*"
        self.count = None
        self.on_conflict = ""

    def _op(self, nome, *args, **kwargs):
        self.ops.append((nome, args, kwargs))
        return self

    # leitura ------------------------------------------------------------------
    def select(self, colunas="*", count=None, **kw):
        self.colunas, self.count = colunas, count
        return self._op("select", colunas, count=count)

    def eq(self, c, v): return self._op("eq", c, v)
    def neq(self, c, v): return self._op("neq", c, v)
    def ilike(self, c, v): return self._op("ilike", c, v)
    def in_(self, c, v): return self._op("in_", c, list(v))
    def or_(self, filtros, reference_table=None): return self._op("or_", filtros)
    def order(self, c, desc=False, **kw): return self._op("order", c, desc=desc)
    def range(self, a, b): return self._op("range", a, b)
    def limit(self, n, **kw): return self._op("limit", n)

    # escrita ------------------------------------------------------------------
    def insert(self, dados, **kw):
        self.acao, self.payload = "insert", copy.deepcopy(dados)
        return self._op("insert", dados)

    def update(self, dados, **kw):
        self.acao, self.payload = "update", copy.deepcopy(dados)
        return self._op("update", dados)

    def upsert(self, dados, on_conflict="", **kw):
        self.acao, self.payload, self.on_conflict = "upsert", copy.deepcopy(dados), on_conflict
        return self._op("upsert", dados, on_conflict=on_conflict)

    def execute(self):
        return self.cliente._executar(self)


class FakeAuth:
    def __init__(self):
        self.erro_login: Optional[Exception] = None
        self.usuario = SimpleNamespace(id="uid-1", email="pessoa@exemplo.com")
        self.credenciais = None
        self.sign_out_chamadas = 0

    def sign_in_with_password(self, cred):
        self.credenciais = cred
        if self.erro_login:
            raise self.erro_login
        return SimpleNamespace(user=self.usuario, session=SimpleNamespace(access_token="tok"))

    def sign_out(self):
        self.sign_out_chamadas += 1

    def get_session(self):
        import time
        return SimpleNamespace(expires_at=time.time() + 3600, access_token="tok")

    def refresh_session(self):
        self.refresh_chamadas = getattr(self, "refresh_chamadas", 0) + 1


class FakeSupabase:
    def __init__(self, tabelas: Optional[Dict[str, List[dict]]] = None, *, max_rows: Optional[int] = None,
                 ignorar_range: bool = False, gatilho_protocolo: bool = True,
                 falha: Optional[Callable[[FakeQuery], Optional[Exception]]] = None,
                 update_vazio: bool = False):
        self.tabelas: Dict[str, List[dict]] = {"postes": [], "ordens_servico": [], "perfis": []}
        for nome, linhas in (tabelas or {}).items():
            self.tabelas[nome] = []
            for linha in linhas:
                self._inserir_linha(nome, dict(linha), checar=False)
        self.max_rows = max_rows
        self.ignorar_range = ignorar_range
        self.gatilho_protocolo = gatilho_protocolo
        self.falha = falha
        self.update_vazio = update_vazio  # imita RLS que filtra todas as linhas no UPDATE
        self.chamadas: List[FakeQuery] = []
        self.auth = FakeAuth()

    def table(self, nome: str) -> FakeQuery:
        return FakeQuery(self, nome)

    # utilidades de teste --------------------------------------------------------
    def chamadas_de(self, tabela: str, acao: Optional[str] = None) -> List[FakeQuery]:
        return [q for q in self.chamadas if q.tabela == tabela and (acao is None or q.acao == acao)]

    # motor ----------------------------------------------------------------------
    def _proximo_id(self, tabela: str) -> int:
        return max((r.get("id") or 0 for r in self.tabelas[tabela]), default=0) + 1

    def _inserir_linha(self, tabela: str, linha: dict, checar: bool = True) -> dict:
        nova = dict(DEFAULTS.get(tabela, {}))
        nova.update(linha)
        nova.setdefault("id", self._proximo_id(tabela))
        if tabela == "postes":
            if any(r["codigo"] == nova["codigo"] for r in self.tabelas["postes"]):
                raise FakeAPIError(
                    "{'code': '23505', 'message': 'duplicate key value violates unique constraint \"postes_codigo_key\"'}")
        if tabela == "ordens_servico":
            if checar and not any(p["codigo"] == nova.get("codigo_poste") for p in self.tabelas["postes"]):
                raise FakeAPIError("{'code': '23503', 'message': 'insert or update on table \"ordens_servico\" "
                                   "violates foreign key constraint'}")
            nova.setdefault("data_abertura", datetime.datetime.now(datetime.timezone.utc).isoformat())
            if self.gatilho_protocolo and not nova.get("protocolo"):
                nova["protocolo"] = f"OS-{datetime.date.today().year}-{nova['id']:04d}"
        self.tabelas[tabela].append(nova)
        return nova

    def _casa(self, linha: dict, q: FakeQuery) -> bool:
        for nome, args, _ in q.ops:
            if nome == "eq" and linha.get(args[0]) != args[1]:
                return False
            if nome == "neq" and linha.get(args[0]) == args[1]:
                return False
            if nome == "in_" and linha.get(args[0]) not in args[1]:
                return False
            if nome == "ilike":
                valor = linha.get(args[0])
                if valor is None or not _like_para_regex(args[1]).match(str(valor)):
                    return False
            if nome == "or_":
                ok = False
                for parte in args[0].split(","):
                    col, op, val = parte.split(".", 2)
                    if op != "ilike":
                        raise NotImplementedError(op)
                    v = linha.get(col)
                    if v is not None and _like_para_regex(val).match(str(v)):
                        ok = True
                if not ok:
                    return False
        return True

    def _executar(self, q: FakeQuery):
        self.chamadas.append(q)
        if self.falha:
            erro = self.falha(q)
            if erro:
                raise erro
        tabela = self.tabelas.setdefault(q.tabela, [])

        if q.acao == "insert":
            itens = q.payload if isinstance(q.payload, list) else [q.payload]
            return SimpleNamespace(data=[dict(self._inserir_linha(q.tabela, dict(i))) for i in itens], count=None)

        if q.acao == "update":
            alvo = [r for r in tabela if self._casa(r, q)]
            if self.update_vazio:
                return SimpleNamespace(data=[], count=None)
            for r in alvo:
                r.update(q.payload)
            return SimpleNamespace(data=[dict(r) for r in alvo], count=None)

        if q.acao == "upsert":
            itens = q.payload if isinstance(q.payload, list) else [q.payload]
            colunas = []
            for i in itens:
                for k in i:
                    if k not in colunas:
                        colunas.append(k)
            saida = []
            for i in itens:
                existente = next((r for r in tabela if r.get(q.on_conflict) == i.get(q.on_conflict)), None)
                if existente is not None:
                    for c in colunas:
                        existente[c] = i.get(c)
                    saida.append(dict(existente))
                else:
                    saida.append(dict(self._inserir_linha(q.tabela, {c: i.get(c) for c in colunas})))
            return SimpleNamespace(data=saida, count=None)

        # select
        linhas = [copy.deepcopy(r) for r in tabela if self._casa(r, q)]
        for nome, args, kw in q.ops:
            if nome == "order":
                linhas.sort(key=lambda r: (r.get(args[0]) is None, r.get(args[0])), reverse=kw.get("desc", False))
        total = len(linhas)
        for nome, args, _ in q.ops:
            if nome == "range" and not self.ignorar_range:
                linhas = linhas[args[0]:args[1] + 1]
            if nome == "limit":
                linhas = linhas[:args[0]]
        if self.max_rows is not None:
            linhas = linhas[:self.max_rows]
        if "postes(" in q.colunas:
            for r in linhas:
                p = next((p for p in self.tabelas["postes"] if p["codigo"] == r.get("codigo_poste")), None)
                r["postes"] = dict(p) if p else None
        elif q.colunas.strip() != "*":
            campos = [c.strip() for c in q.colunas.split(",")]
            linhas = [{c: r.get(c) for c in campos} for r in linhas]
        return SimpleNamespace(data=linhas, count=total if q.count == "exact" else None)


class FakeConsultaPaginada:
    """Fábrica mínima para paginacao.buscar_todas_paginas (só range/execute)."""

    def __init__(self, total: int, ignorar_range: bool = False, max_rows: Optional[int] = None):
        self.total = total
        self.ignorar_range = ignorar_range
        self.max_rows = max_rows
        self.ranges: List[tuple] = []

    def __call__(self):
        return self

    def range(self, a, b):
        self.ranges.append((a, b))
        self._a, self._b = a, b
        return self

    def execute(self):
        if self.ignorar_range:
            a, b = 0, 999
        else:
            a, b = self._a, self._b
        linhas = [{"id": i} for i in range(self.total)][a:b + 1]
        if self.max_rows is not None:
            linhas = linhas[:self.max_rows]
        return SimpleNamespace(data=linhas)
