"""Arm runner for the v3 benchmark (PLAN-v3-bench §5, §7; PLAN-v3-bench-run §1, §2). One JSONL record per cell; resumable; budget-capped.

  .venv/bin/python bench/run.py --estimate                       # pilot and full-design cost estimate, no calls
  .venv/bin/python bench/run.py --pilot --out bench/results/pilot.jsonl --budget 3.00   # PLAN-v3-bench-run §5
  .venv/bin/python bench/run.py --arms T --models stub:key --n 25 --items M01 A1 --out /tmp/x.jsonl

A cell is (kind, arm, model, N, item, rep): an analyst session (A1-A3, four scripted turns) or a manager
question (M..). Arms:
  G    bench/material/N*.md in the system prompt (data model, glossary, how rules combine, rules, claims,
       example SQL) and a read-only `sql` tool
  G+   G plus the trusted functions of bench/gplus.py (fn_*)
  T    the data model only (the material's section 1), the goal vocabulary of the base, and the engine's
       tools resolve_term, describe, decide, why, why_not through spikes/v3/v3a-prolog/cli, plus `sql`
Every tool runs here and is logged here (name, args, seconds, result size, error), never read from model
output. Every model call records model, provider, tokens, cost and time, as v2.

Models: an OpenRouter id (deepseek/deepseek-v4.1-flash), or openai@<id>, or ollama@<tag> (local, $0, with
--context set and recorded; never mixed into the paid results).

Budget: --budget caps the summed cost of --out and of every --also file (the judge's records), earlier runs
included. Before every model call the call's maximum cost (prompt from its size at 3 characters per token, plus
max_tokens of completion, at list price) is reserved under a lock and settled with the charged cost after, so
concurrent cells cannot overshoot. A model without a known price is refused. A call that fails keeps its
reservation as its cost (marked cost_estimated). A cell stopped by the budget is recorded with error "budget".
Every other exception in a cell is recorded with its type, message and traceback, and with the cost spent so far.
Cells with an error are run again on resume; cells without are not.

Truncation: a call whose reported prompt tokens are fewer than its characters / TRUNC_CHARS, or (ollama) that
fills the context, fails the cell with error "truncated".

Clients that make no calls (tests, PLAN-v3-bench-run §1): stub:key answers with the oracle's keys (manager JSON;
analyst figures in the text), stub:tool calls one tool first, stub:abstain answers UNDERDETERMINED;
fake:<usd>[:<mode>] is stub:tool charging <usd> per call and sleeping 20 ms, with modes raise (on the second
call), badargs (tool arguments not JSON), nofunc (a tool call without "function"), notools (a reply without a
"tool_calls" field), trunc (reports 10 prompt tokens).
"""
import argparse, concurrent.futures as cf, datetime, decimal, json, pathlib, re, shlex, subprocess, sys, threading, time, traceback

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "bench"), str(ROOT / "spikes/v3/shared")]
from harness import openrouter                      # noqa: E402
from harness.read import _last_json                 # noqa: E402
import gplus, integrity                             # noqa: E402

CLI = "spikes/v3/v3a-prolog/cli"
EXT = "spikes/v3/shared/extension.edn"
CFG = {"backend": "duckdb", "duckdb": "spikes/v3/shared/slice.duckdb", "fetch_limit": 10000}
BENCH = ROOT / "bench"
MODELS = ["deepseek/deepseek-v4.1-flash", "z-ai/glm-5.3"]
JUDGE = "openai@gpt-6.2-sol"         # via the Batch API (half price), paid from OpenAI credits
ARMS = ["G", "G+", "T"]
NS = [25, 50, 100, 200]
TASKS = ["A1", "A2", "A3"]
ANALYST_ARMS = ["G", "T"]      # G+ targets manager questions (Matthias, 2026-11-26)
PILOT = {"models": ["deepseek/deepseek-v4.1-flash"], "n": [25, 200],
         "items": TASKS + ["M01", "M03", "M08", "M13", "M16", "M17", "M19", "M21", "M46", "M50"]}
# USD per token, OpenRouter public model list fetched 2026-11-25 (prompt, completion, cache read)
PRICE = {"deepseek/deepseek-v4.1-flash": (1.4e-7, 4.2e-7, 4.2e-9),
         "z-ai/glm-5.3": (6.99e-8, 1.4e-6, 6.89e-8)}
SQL_ROWS, SQL_SECONDS, RESULT_CHARS = 200, 30, 12000
TRUNC_CHARS = 8          # characters per reported prompt token above which a prompt counts as cut (tokenizers give 3-5)
RESERVE_CHARS = 3        # characters per token when reserving a call's maximum prompt cost (an upper bound)
ROUNDS = {"manager": 8, "analyst": 12}      # model calls per turn; the last reply stands if the limit is hit

MANAGER = """\
Answer the manager's question. Check against the data with the tools; do not guess figures. End your reply with \
one JSON object in a ```json block with these fields:
- "status": "ANSWER" if the question has a determined answer; "CONFLICT" if rules or claims for and against both \
apply and neither prevails (contested); "UNDERDETERMINED" if the term asked about is known but nothing defines \
its value; "OUT_OF_SCOPE" if the term asked about is unknown here.
- "value": a number, an id, true or false, a list of ids, or null (null for anything but ANSWER).
- "sides": for CONFLICT, the rule or claim ids on each side, [[...], [...]]; else null.
- "qualified": true if the answer rests only on not finding something in the data (a "no", or a total, over the \
known facts), else false.
- "standing": only if asked whether a claim holds: "holds", "holds_with_qualifier" (holds, but a supporting \
sub-claim failed), "rebutted", "contested" or "not_in_force"; else null.
- "defeater": for "rebutted", the id of the claim that defeats it; else null.
- "term": only if asked what a term means: "concept" (one definition fits), "several" (more than one fits) or \
"none" (not defined here); else null.
- "candidates": for "term", the labels of the fitting terms; else [].
- "rules": the rule and claim ids the answer rests on."""

ANALYST = """\
You are helping an analyst design a dashboard over this data. Each user turn asks for a design or a change to it. \
Reply to each turn with the design: its components; for each component, the rule and claim ids it rests on, the \
{how} it runs, and its figures for the worked example the turn names (run it; do not estimate); and caveats. You \
may refer to components of earlier turns by name."""

T_HEAD = """\
# Procurement data: instructions for the analytics assistant

This space answers questions about purchase requests, cost centres, approvals and vendors. Its {rules} rules and \
{claims} claims are held by a rule engine, reached through the tools resolve_term, describe, decide, why and \
why_not; the engine applies them, so do not re-derive a rule in SQL. The data is in DuckDB; use the `sql` tool \
(read-only) for what the rules do not cover. Cite the rule and claim ids (R…, G…, C…, H…) the engine reports for \
every conclusion you draw from them. Today is {today}.
"""


# ---------------------------------------------------------------- material per arm

def stem(n):
    return BENCH / "bases" / f"N{n:03d}"


def _modes():
    t = (ROOT / "spikes/v3/shared/modes.edn").read_text()
    return dict(re.findall(r':(\w+) "([+-]+)"', re.sub(r";[^\n]*", "", t)))


def vocabulary(n):
    """The goals T can ask: every predicate the base concludes, with its arguments, and the claims' predicates."""
    S, rules, claims = integrity.rule_base([str(stem(n).with_suffix(".edn")), EXT])
    modes, heads, seen = _modes(), {}, set()
    for r in rules:
        h = r.get("head")
        if h:
            h = h[1] if h[0] == "neg" else h
            heads.setdefault(h[0], h[1:])
    o = ["## Goals the engine decides\n",
         'A goal is EDN: a vector of a keyword predicate and its arguments; strings quoted, unknowns as ?variables, '
         'e.g. `[:headroom "cc0009" ?v]` or `[:approved "r000001"]`. A + argument must be given; a - argument may be a '
         '?variable, and decide returns its value (or the list of values). To evaluate at a date, pass as_of.\n']
    for p, args in sorted(heads.items()):
        m = modes.get(p, "+" * len(args))
        o.append(f"- `{p}` " + " ".join(f"{a if str(a).startswith('?') else '?code'}{m[i] if i < len(m) else ''}"
                                         for i, a in enumerate(args)))
        seen.add(p)
    cl = sorted({(c["assertion"][1] if c["assertion"][0] == "neg" else c["assertion"])[0] for c in claims} - seen)
    o.append("\nPredicates asserted by claims (decide them like the others; describe an asset to see its claims): "
             + ", ".join(f"`{p}`" for p in cl) + ".")
    o.append("\nAssets for describe: " + ", ".join(a["id"] for a in S["assets"]) + ".\n")
    return "\n".join(o), len(rules), len(claims), S["today"]


def system_prompt(arm, n, kind):
    md = (BENCH / "material" / f"N{n:03d}.md").read_text()
    if arm in ("G", "G+"):
        s = md
        if arm == "G+":
            s += ("\n## 7 Trusted functions\n\nThe fn_* tools are certified SQL for frequent questions, checked against "
                  "the policy. Prefer them where they answer the question; use `sql` otherwise.\n")
    else:
        voc, nr, nc, today = vocabulary(n)
        data_model = md[md.index("## 1 Data model"):md.index("## 2 Glossary")]
        s = T_HEAD.format(rules=nr, claims=nc, today=today) + "\n" + data_model + voc
    how = "SQL or engine call" if arm == "T" else "SQL"
    return s + "\n## Your task\n\n" + (MANAGER if kind == "manager" else ANALYST.format(how=how))


def _fn(name, desc, props, req):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": {k: {"type": "string", "description": v} for k, v in props.items()},
        "required": req}}}


SQL_TOOL = _fn("sql", f"Run one read-only DuckDB SQL query over the tables of the data model. At most {SQL_ROWS} "
               f"rows are returned (truncated is then true); {SQL_SECONDS} s limit.", {"query": "the SQL query"}, ["query"])
AS_OF = "date YYYY-MM-DD at which to evaluate dated rules, statuses and claims; default today"
T_TOOLS = [
    _fn("resolve_term", "Which governed term a business phrase means: status concept (one term), several (ambiguous) "
        "or none (unknown), with each candidate's definition and owner.", {"text": "the phrase"}, ["text"]),
    _fn("describe", "An asset (vendor:<id>, emp:<id>): its doc, data bindings, and every claim about it with its "
        "standing on as_of: holds, holds_with_qualifier (a supporting sub-claim failed), rebutted (with the "
        "defeater), contested (with sides) or not_in_force.", {"asset": "asset id", "as_of": AS_OF}, ["asset"]),
    _fn("decide", "Decide a goal. Returns status (ANSWER, CONFLICT: rules or claims on both sides and none prevails, "
        "UNDERDETERMINED: a known term nothing defines, OUT_OF_SCOPE: an unknown predicate), value, sides of a "
        "conflict, the owners of the rules used, and qualifier (\"total over known facts in declared scope\" when "
        "the answer rests on absence).", {"goal": "EDN goal", "as_of": AS_OF}, ["goal"]),
    _fn("why", "decide plus the proof: the rules, claims and data rows the answer rests on.",
        {"goal": "EDN goal", "as_of": AS_OF}, ["goal"]),
    _fn("why_not", "For a goal that does not hold: per rule that could conclude it, the conditions that failed.",
        {"goal": "EDN goal", "as_of": AS_OF}, ["goal"]),
    SQL_TOOL]


def tools_for(arm):
    return {"G": [SQL_TOOL], "G+": [SQL_TOOL] + gplus.tools(), "T": T_TOOLS}[arm]


# ---------------------------------------------------------------- tool execution (logged here)

_DB, _DB_LOCK = None, threading.Lock()


def _con():
    global _DB
    with _DB_LOCK:
        if _DB is None:
            import duckdb
            _DB = duckdb.connect(str(gplus.DB), read_only=True,
                                 config={"enable_external_access": False, "lock_configuration": True})
        return _DB.cursor()


def _plain(v):
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return int(v) if v == v.to_integral_value() else float(v)
    return v


def run_sql(query):
    c = _con()
    timer = threading.Timer(SQL_SECONDS, c.interrupt)
    timer.start()
    try:
        cur = c.execute(query)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(SQL_ROWS + 1)
    finally:
        timer.cancel()
        c.close()
    return {"columns": cols, "rows": [[_plain(v) for v in r] for r in rows[:SQL_ROWS]], "truncated": len(rows) > SQL_ROWS}


def run_fn(name, args):
    c = _con()
    try:
        rows = gplus.call(c, name, args)
    finally:
        c.close()
    out = [{k: _plain(v) for k, v in r.items()} for r in rows]
    return {"rows": out[:SQL_ROWS], "truncated": len(out) > SQL_ROWS}


def engine(n, ops):
    script = {"config": CFG, "load": [str(stem(n).relative_to(ROOT)) + ".edn", EXT], "ops": ops}
    p = subprocess.run(shlex.split(CLI), input=json.dumps(script), capture_output=True, text=True, cwd=ROOT, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"engine failed: {p.stderr.strip()[-600:]}")
    rs = json.loads(p.stdout)["results"]
    for r in rs:
        r.pop("sql_log", None), r.pop("ms", None)
    return rs


def run_t(n, name, a):
    as_of = {"as_of": a["as_of"]} if a.get("as_of") else {}
    if name == "resolve_term":
        return engine(n, [{"op": "resolve_term", "text": a["text"]}])[0]
    if name == "describe":
        d, c = engine(n, [{"op": "describe", "asset": a["asset"]}, {"op": "claims", "asset": a["asset"], **as_of}])
        return dict(d, claims=c.get("claims", c))
    if name in ("decide", "why"):
        r = engine(n, [{"op": "decide", "goal": a["goal"], **as_of}])[0]
        return r if name == "why" else {k: v for k, v in r.items() if k != "why"}
    if name == "why_not":
        return engine(n, [{"op": "why_not", "goal": a["goal"], **as_of}])[0]
    raise KeyError(name)


def execute(arm, n, name, args):
    """-> (text for the model, log entry). Errors go back to the model as text."""
    t0, err = time.time(), None
    try:
        a = json.loads(args) if isinstance(args, str) else (args or {})
        if name == "sql":
            out = run_sql(a["query"])
        elif name.startswith("fn_") and arm == "G+":
            out = run_fn(name[3:], a)
        elif arm == "T" and name in ("resolve_term", "describe", "decide", "why", "why_not"):
            out = run_t(n, name, a)
        else:
            raise KeyError(f"no tool {name} in arm {arm}")
        text = json.dumps(out, default=str)
    except Exception as e:      # noqa: BLE001 — every failure is the model's to see
        err = f"{type(e).__name__}: {e}"[:600]
        text = json.dumps({"error": err})
    full = len(text)
    if full > RESULT_CHARS:
        text = text[:RESULT_CHARS] + f' ... [truncated: {full} chars; narrow the query]'
    return text, {"name": name, "args": args, "seconds": round(time.time() - t0, 3), "chars": full, "error": err,
                  "result": text}


# ---------------------------------------------------------------- items and keys

def items():
    out = {t: json.loads((BENCH / "tasks" / f"{t}.json").read_text()) for t in TASKS}
    for q in json.loads((BENCH / "questions/manager.json").read_text())["questions"]:
        out[q["id"]] = q
    return out


def task_keys(t):
    return json.loads((BENCH / "tasks" / f"{t}.keys.json").read_text())


SLICE_KEYS = None


def manager_key(q):
    global SLICE_KEYS
    if SLICE_KEYS is None:
        SLICE_KEYS = json.loads((ROOT / "spikes/v3/shared/keys.json").read_text())["extended"]
    return SLICE_KEYS[q["slice"]]


def user_turns(item):
    if "turns" in item:
        return [f"{t['text']} {t['example']}" for t in item["turns"]]
    scope = f" (I manage cost centre {item['scope']} and the centres under it.)" if item.get("scope") else ""
    return [item["text"] + scope]


# ---------------------------------------------------------------- clients

def key_answer(key):
    """The manager JSON a perfect answer gives (stub:key)."""
    if "standing" in key:
        return {"status": "ANSWER", "value": None, "standing": key["standing"], "defeater": key["defeater"], "rules": key["core"]}
    if "candidates" in key:
        return {"status": "ANSWER", "value": None, "term": key["status"],
                "candidates": [c.split(":", 1)[1].replace("_", " ") for c in key["candidates"]]}
    return {"status": key["status"], "value": key.get("value"), "sides": key.get("sides"),
            "qualified": key.get("qualifier") is not None, "rules": key.get("core", [])}


def stub_client(model, item, arm):
    """A client function for a stub or fake model, scripted from the oracle's keys."""
    if model.startswith("fake:"):
        f = model.split(":")
        mode, cost, fault = "tool", float(f[1]), (f[2] if len(f) > 2 else None)
    else:
        mode, cost, fault = model.split(":", 1)[1], 0.0, None
    turn = {"n": 0}

    def reply(msgs):
        if "turns" in item:
            keys, t = task_keys(item["id"]), sum(m["role"] == "user" for m in msgs)
            figs = [f"{c['component']}: {json.dumps(keys[c['id']]['value'])}" for c in item["checks"] if c["turn"] == t]
            return "Design.\n" + "\n".join(figs) if mode != "abstain" else "I cannot design this."
        o = key_answer(manager_key(item)) if mode != "abstain" else {"status": "UNDERDETERMINED", "value": None}
        return "Answer.\n```json\n" + json.dumps(o) + "\n```"

    def call(m, msgs, tools):
        last = msgs[-1]
        tool_turn = mode in ("tool",) and last["role"] == "user"
        turn["n"] += 1
        if model.startswith("fake:"):
            time.sleep(0.02)
        if fault == "raise" and turn["n"] == 2:
            raise ValueError("fake client failure")
        if tool_turn:
            name = tools[-1 if arm != "T" else 2]["function"]["name"] if tools else "sql"
            args = {"sql": {"query": "SELECT COUNT(*) AS n FROM req"}, "decide": {"goal": '[:headroom "cc0009" ?v]'}}.get(
                name, {"cc": "cc0009"})
            fn = {"name": name, "arguments": "{not json" if fault == "badargs" else json.dumps(args)}
            tc = [{"id": f"call_{turn['n']}", "type": "function"} if fault == "nofunc" else
                  {"id": f"call_{turn['n']}", "type": "function", "function": fn}]
            msg, content = {"role": "assistant", "content": "", "tool_calls": tc}, ""
        else:
            content, tc = reply(msgs), []
            msg = {"role": "assistant", "content": content}
        res = {"content": content, "reasoning": "", "finish_reason": "stop", "model_served": model, "provider": "stub",
               "prompt_tokens": 10 if fault == "trunc" else sum(len(json.dumps(x)) for x in msgs) // 4,
               "completion_tokens": len(content) // 4, "reasoning_tokens": 0, "cached_tokens": 0, "cost": cost,
               "seconds": 0.0, "attempts": 1, "tool_calls": tc, "message": msg}
        if fault == "notools" and not tc:
            del res["tool_calls"]
        return res
    return call


def endpoint_of(model):
    """-> (endpoint, model id at that endpoint)"""
    for e in ("openai", "ollama"):
        if model.startswith(e + "@"):
            return e, model.split("@", 1)[1]
    return "openrouter", model


def price(model):
    """USD per token (prompt, completion, cache read); KeyError for a model without a known price."""
    e, m = endpoint_of(model)
    if model.startswith("stub:") or e == "ollama":
        return (0.0, 0.0, 0.0)
    if e == "openai":
        i, o, c = openrouter.OPENAI_PRICE[m]
        return (i, o, c)
    return PRICE[m]


def max_cost(model, msgs, tools, max_tokens):
    """The most a call can cost: its prompt at RESERVE_CHARS characters per token, plus max_tokens."""
    if model.startswith("fake:"):
        return float(model.split(":")[1])
    p = price(model)
    chars = len(json.dumps(msgs)) + len(json.dumps(tools or []))
    return chars / RESERVE_CHARS * p[0] + max_tokens * p[1]


def live_client(config):
    def call(model, msgs, tools):
        e, m = endpoint_of(model)
        kw = {k: config[k] for k in ("temperature", "max_tokens")}
        if e == "openrouter":
            kw["provider"] = config.get("provider")
        return openrouter.chat(m, msgs, tools=tools, endpoint=e, **kw)
    return call


# ---------------------------------------------------------------- budget and sessions

class BudgetStop(Exception):
    pass


class Truncated(Exception):
    pass


class Budget:
    """A hard cap: each call reserves its maximum cost first and settles with the charged cost after."""
    def __init__(self, cap, spent):
        self.cap, self.spent, self.held = cap, spent, 0.0
        self.lock, self.stop = threading.Lock(), threading.Event()

    def reserve(self, usd):
        with self.lock:
            if self.stop.is_set() or self.spent + self.held + usd > self.cap + 1e-12:
                self.stop.set()
                raise BudgetStop(f"budget ${self.cap:.2f} reached (spent ${self.spent:.4f}, held ${self.held:.4f}, "
                                 f"next call up to ${usd:.4f})")
            self.held += usd
        return usd

    def settle(self, held, usd):
        with self.lock:
            self.held -= held
            self.spent += usd or 0.0


def call_cost(res, model):
    """The charged cost; from tokens and the price list when the response lacks it."""
    if res.get("cost") is not None:
        return res["cost"]
    p = price(model)
    return (res.get("prompt_tokens") or 0) * p[0] + (res.get("completion_tokens") or 0) * p[1]


def truncation(res, msgs, tools, context):
    """A reason if the endpoint saw less prompt than was sent, else None."""
    pt, chars = res.get("prompt_tokens"), len(json.dumps(msgs)) + len(json.dumps(tools or []))
    if pt is not None and pt * TRUNC_CHARS < chars:
        return f"truncated: {pt} prompt tokens reported for {chars} characters sent"
    if context and pt is not None and pt + (res.get("completion_tokens") or 0) >= 0.98 * context:
        return f"truncated: {pt} prompt + {res.get('completion_tokens')} completion tokens fill the context {context}"
    return None


CALL_FIELDS = ("model_served", "provider", "generation_id", "finish_reason", "prompt_tokens", "completion_tokens",
               "reasoning_tokens", "cached_tokens", "cost", "seconds", "attempts")


def failure(e):
    return {"error_type": type(e).__name__, "traceback": traceback.format_exc()[-4000:]}


def session(client, model, arm, n, kind, item, budget, max_tokens, context=None):
    """Run one cell. -> record fields. Raises nothing: a budget stop, a truncation or any exception is recorded,
    with every call made so far and its cost."""
    msgs, tools, calls, tlog, turns, err, extra = [], [], [], [], [], None, {}
    try:
        msgs.append({"role": "system", "content": system_prompt(arm, n, kind)})
        tools = tools_for(arm)
        for t, text in enumerate(user_turns(item), 1):
            msgs.append({"role": "user", "content": text})
            for i in range(ROUNDS[kind]):
                held = budget.reserve(max_cost(model, msgs, tools, max_tokens))
                try:
                    res = client(model, msgs, tools)
                    res["cost"] = call_cost(res, model)
                except BaseException:
                    budget.settle(held, held)           # cost unknown: count the reservation
                    calls.append({"turn": t, "cost": held, "cost_estimated": True, "prompt_tokens": None,
                                  "completion_tokens": None, "seconds": None, "tool_calls": 0})
                    raise
                budget.settle(held, res["cost"])
                tcs = res.get("tool_calls") or []
                calls.append(dict({k: res.get(k) for k in CALL_FIELDS}, turn=t, tool_calls=len(tcs),
                                  sent_chars=len(json.dumps(msgs)) + len(json.dumps(tools))))
                cut = truncation(res, msgs, tools, context)
                if cut:
                    raise Truncated(cut)
                msgs.append(res.get("message") or {"role": "assistant", "content": res["content"]})
                if not tcs:
                    break
                for tc in tcs:
                    out, log = execute(arm, n, tc["function"]["name"], tc["function"].get("arguments"))
                    tlog.append(dict(log, turn=t, call=len(calls)))
                    msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": out})
            turns.append({"turn": t, "content": res["content"], "reasoning": res.get("reasoning") or "",
                          "tool_limit": bool(tcs)})
    except BudgetStop as e:
        err = "budget"
        print(f"  {e}", flush=True)
    except Truncated as e:
        err = str(e)
    except Exception as e:      # noqa: BLE001 — an unexpected error must never lose a record or its cost
        err, extra = f"{type(e).__name__}: {e}"[:600], failure(e)
    rec = {"calls": calls, "tools": tlog, "turns": turns, "messages": msgs[1:], "error": err, **extra,
           "cost": sum(c["cost"] or 0 for c in calls), "prompt_tokens": sum(c["prompt_tokens"] or 0 for c in calls),
           "completion_tokens": sum(c["completion_tokens"] or 0 for c in calls),
           "seconds": round(sum(c["seconds"] or 0 for c in calls), 3),
           "system_chars": len(msgs[0]["content"]) if msgs else 0}
    if kind == "manager" and turns:
        rec["answer"] = _last_json(turns[-1]["content"])
    return rec


def cell(r):
    return (r["kind"], r["arm"], r["model"], r["n"], r["item"], r["rep"])


def spent_in(*paths):
    s = 0.0
    for p in paths:
        p = pathlib.Path(p)
        if p.exists():
            s += sum(json.loads(l).get("cost") or 0.0 for l in p.read_text().splitlines() if l.strip())
    return s


# ---------------------------------------------------------------- estimate (PLAN §7: before any call)

# Assumptions, stated where they are used: model calls per manager question and per analyst turn, tokens each
# call adds to the context (tool results and replies), completion tokens per call (v2: 1.39M over 792 calls).
EST = {"calls": {("manager", "G"): 3, ("manager", "G+"): 3, ("manager", "T"): 4,
                 ("analyst", "G"): 4, ("analyst", "G+"): 4, ("analyst", "T"): 5},
       "grow": 1500, "completion": 1750, "judge_prompt": 14000, "judge_completion": 6000}


def estimate_cell(model, arm, n, kind, cached=False):
    sys_tok = (len(system_prompt(arm, n, kind)) + len(json.dumps(tools_for(arm)))) // 4
    per_turn, turns = EST["calls"][(kind, arm)], (4 if kind == "analyst" else 1)
    k = per_turn * turns
    prompt = sum(sys_tok + i * EST["grow"] for i in range(k))
    p = price(model)
    cost_prompt = (sys_tok * p[2] * k + (prompt - sys_tok * k) * p[0]) if cached else prompt * p[0]
    return k, prompt, k * EST["completion"], cost_prompt + k * EST["completion"] * p[1]


def estimate(models, arms, ns, reps, cached=False, ids=None, analyst_arms=ANALYST_ARMS):
    its = [i for i in items() if not ids or i in ids]
    per, tot = {}, {"calls": 0, "prompt": 0, "completion": 0, "usd": 0.0, "cells": 0, "judge_usd": 0.0}
    jp = [x / 2 for x in price(JUDGE)]      # Batch tier
    for model in models:
        for arm in arms:
            for n in ns:
                for kind in ("analyst", "manager"):
                    if kind == "analyst" and arm not in analyst_arms:
                        continue
                    m = len([i for i in its if i.startswith("A" if kind == "analyst" else "M")])
                    k, pr, co, usd = estimate_cell(model, arm, n, kind, cached)
                    per[(model, arm, n, kind)] = (m * reps, usd)
                    tot["calls"] += k * m * reps; tot["prompt"] += pr * m * reps
                    tot["completion"] += co * m * reps; tot["usd"] += usd * m * reps; tot["cells"] += m * reps
                    if kind == "analyst":
                        tot["judge_usd"] += m * reps * (EST["judge_prompt"] * jp[0] + EST["judge_completion"] * jp[1])
    return per, tot


def print_estimate(models, arms, ids=None, analyst_arms=ANALYST_ARMS):
    print("Assumptions:", json.dumps({f"{k[0]}/{k[1]}": v for k, v in EST["calls"].items()}),
          f"calls per question or turn; +{EST['grow']} context tokens per call; {EST['completion']} completion tokens "
          f"per call; judge {EST['judge_prompt']}+{EST['judge_completion']} tokens per analyst session. Prices: OpenRouter "
          "list 2026-11-25.")
    print("\nPilot cells (one repetition), USD per cell, no caching:")
    per, _ = estimate(models, arms, [25, 200], 1, ids=ids, analyst_arms=analyst_arms)
    print(f"  {'model':30} {'arm':3} {'N':>4} {'analyst':>9} {'manager':>9}")
    for model in models:
        for arm in arms:
            for n in (25, 200):
                an = per.get((model, arm, n, "analyst"))
                print(f"  {model:30} {arm:3} {n:4} {f'{an[1]:9.4f}' if an else '        –'} {per[(model, arm, n, 'manager')][1]:9.4f}")
    out = {}
    for label, ns, reps in (("pilot (N 25, 200; 1 rep)", [25, 200], 1), ("full, 1 rep (N 25-200)", NS, 1),
                            ("full, 3 reps (N 25-200)", NS, 3)):
        for cached in (False, True):
            _, t = estimate(models, arms, ns, reps, cached, ids, analyst_arms)
            out[(label, cached)] = t
            print(f"{label:26} {'cached system prompt' if cached else 'no caching':21} cells {t['cells']:4}  calls "
                  f"{t['calls']:5}  prompt {t['prompt'] / 1e6:6.2f}M  completion {t['completion'] / 1e6:5.2f}M  "
                  f"OpenRouter ${t['usd']:.2f}; judge (OpenAI Batch) ${t['judge_usd']:.2f}")
    return out


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true", help="print the cost estimate and exit; no calls")
    ap.add_argument("--pilot", action="store_true", help="the pilot cells (PILOT; PLAN-v3-bench-run §5)")
    ap.add_argument("--arms", nargs="+", default=ARMS, choices=ARMS)
    ap.add_argument("--analyst-arms", nargs="+", default=ANALYST_ARMS, choices=ARMS, help="arms for analyst tasks")
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--n", type=int, nargs="+", default=[25, 200])
    ap.add_argument("--items", nargs="*", help="A1 A2 A3 M01 ...; default all")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--out")
    ap.add_argument("--also", nargs="*", default=[], help="other JSONL files whose cost counts against --budget")
    ap.add_argument("--budget", type=float, default=1.0, help="USD cap on the summed cost of --out and --also")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--quantization", default="fp8", help="provider quantization filter; 'any' to disable")
    ap.add_argument("--context", type=int, default=65536, help="ollama context length (recorded; checked per call)")
    a = ap.parse_args()
    if a.pilot:
        a.models, a.n, a.items, a.reps = PILOT["models"], PILOT["n"], PILOT["items"], 1
    live = [m for m in a.models if not m.startswith(("stub:", "fake:"))]
    if a.estimate or (a.pilot and live):
        est = print_estimate(live or MODELS, a.arms, a.items, a.analyst_arms)
        if a.estimate:
            return
        if est[("pilot (N 25, 200; 1 rep)", False)]["usd"] > a.budget:
            print(f"\npilot estimate exceeds the budget ${a.budget:.2f}: stopping before any call")
            sys.exit(2)
    if not a.out:
        ap.error("--out is required to run")
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        done = {cell(r) for r in map(json.loads, out.read_text().splitlines()) if not r.get("error")}
    budget = Budget(a.budget, spent_in(out, *a.also))
    provider = None if a.quantization == "any" else {"quantizations": [a.quantization], "sort": "price"}
    config = {"temperature": a.temperature, "max_tokens": a.max_tokens, "provider": provider}
    if any(endpoint_of(m)[0] == "ollama" for m in a.models):
        config["context"] = a.context
    its = items()
    jobs = []
    for model in a.models:
        for arm in a.arms:
            for n in a.n:
                for iid in (a.items or list(its)):
                    for rep in range(a.reps):
                        kind = "analyst" if "turns" in its[iid] else "manager"
                        if kind == "analyst" and arm not in a.analyst_arms:
                            continue
                        base = {"bench": "v3", "kind": kind, "arm": arm, "model": model, "n": n, "item": iid, "rep": rep}
                        if cell(base) not in done:
                            jobs.append(base)
    print(f"{len(done)} cells done, {len(jobs)} to run; spent ${budget.spent:.4f} of ${a.budget:.2f}", flush=True)
    if budget.spent >= a.budget:
        print("budget already reached"); sys.exit(1)
    lock, stats = threading.Lock(), {"ok": 0, "err": 0}

    def run(base):
        if budget.stop.is_set():
            return
        m = base["model"]
        rec = dict(base, config=config, ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
        try:
            client = stub_client(m, its[base["item"]], base["arm"]) if m.startswith(("stub:", "fake:")) else live_client(config)
            rec.update(session(client, m, base["arm"], base["n"], base["kind"], its[base["item"]], budget,
                               a.max_tokens, a.context if endpoint_of(m)[0] == "ollama" else None))
        except Exception as e:      # noqa: BLE001 — session() records its own; this is the last line of defence
            rec.update(error=f"{type(e).__name__}: {e}"[:600], cost=0.0, prompt_tokens=0, completion_tokens=0,
                       seconds=0.0, calls=[], tools=[], turns=[], **failure(e))
        with lock:
            with out.open("a") as f:
                f.write(json.dumps(rec, default=str) + "\n")
            stats["err" if rec["error"] else "ok"] += 1
            k = stats["ok"] + stats["err"]
            if k % 10 == 0 or k == len(jobs):
                print(f"  {k}/{len(jobs)}  ok {stats['ok']}  err {stats['err']}  ${budget.spent:.4f}", flush=True)

    with cf.ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(run, jobs))
    print(f"done: ok {stats['ok']}, errors {stats['err']}, spent ${budget.spent:.4f}")
    sys.exit(1 if budget.stop.is_set() or stats["err"] else 0)


if __name__ == "__main__":
    main()
