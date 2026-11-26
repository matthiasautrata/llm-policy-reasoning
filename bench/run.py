"""Arm runner for the v3 benchmark (PLAN-v3-bench §5, §7; HISTORY phase 11; PLAN-v3-bench-full §1). One JSONL record per cell; resumable; budget-capped.

  .venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --analyst-arms G G+ T --estimate
  .venv/bin/python bench/run.py --models deepseek/deepseek-v4.1-flash --n 25 200 --out bench/results/b1.jsonl --budget 3
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
included. Prices come from OpenRouter's endpoints list at start (load_prices; recorded in config.prices with the
fetch time): per field the highest over the endpoints the quantization filter admits ("reserve") and the lowest
("typical"). Before every model call the call's maximum cost (prompt from its size at RESERVE_CHARS characters per
token, plus max_tokens of completion, at the reserve price) is reserved under a lock and settled with the charged
cost after, so concurrent cells cannot overshoot. A model without a priced endpoint is refused. A live run first
estimates its cells from the pilot (calibrate) and refuses, before any call, if that exceeds the remaining budget.
A call that fails keeps its reservation as its cost (marked cost_estimated). A cell stopped by the budget is recorded with error "budget".
Every other exception in a cell is recorded with its type, message and traceback, and with the cost spent so far.
Cells with an error are run again on resume; cells without are not.

Truncation: a call whose reported prompt tokens are fewer than its characters / TRUNC_CHARS, or (ollama) that
fills the context, fails the cell with error "truncated".

Clients that make no calls (tests): stub:key answers with the oracle's keys (manager JSON;
analyst figures in the text), stub:tool calls one tool first, stub:abstain answers UNDERDETERMINED;
fake:<usd>[:<mode>] is stub:tool charging <usd> per call and sleeping 20 ms, with modes raise (on the second
call), badargs (tool arguments not JSON), nofunc (a tool call without "function"), notools (a reply without a
"tool_calls" field), trunc (reports 10 prompt tokens), empty (an empty final reply), loop (calls a tool whenever
tools are allowed).
Call limit: a turn that has made ROUNDS calls with tools is closed by one more call with tool_choice "none" and
FINAL_NOW (answer from what was found, say what was not checked); the turn is marked tool_limit and forced_final,
and that call forced (PLAN-v3-bench-full §1.4). Before that fix every turn at the limit ended empty.
A turn whose final reply is empty is marked "empty" (score.py counts it as an empty reply): recorded, not retried,
not an error (seen on gpt-oss:20b, HISTORY phase 11).
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
PRICES = {}             # OpenRouter model -> fetched prices (load_prices), recorded in each record's config
CALIB = BENCH / "results" / "pilot.jsonl.gz"                 # the estimate's tokens and calls per cell (HISTORY 11)
JUDGE_CALIB = BENCH / "results" / "pilot.judge-medium.jsonl.gz"
SQL_ROWS, SQL_SECONDS, RESULT_CHARS = 200, 30, 12000
TRUNC_CHARS = 8          # characters per reported prompt token above which a prompt counts as cut (tokenizers give 3-5)
RESERVE_CHARS = 2.5      # characters per token when reserving a call's maximum prompt cost (pilot minimum 2.80)
ROUNDS = {"manager": 8, "analyst": 12}      # model calls with tools per turn, the same for every arm
FINAL_NOW = ("You have reached the limit of tool calls for this turn. Answer now from what you found, in the form "
             "asked for, without further tool calls, and say what you could not check.")

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
            keys, t = task_keys(item["id"]), sum(m["role"] == "user" and m["content"] != FINAL_NOW for m in msgs)
            figs = [f"{c['component']}: {json.dumps(keys[c['id']]['value'])}" for c in item["checks"] if c["turn"] == t]
            return "Design.\n" + "\n".join(figs) if mode != "abstain" else "I cannot design this."
        o = key_answer(manager_key(item)) if mode != "abstain" else {"status": "UNDERDETERMINED", "value": None}
        return "Answer.\n```json\n" + json.dumps(o) + "\n```"

    def call(m, msgs, tools, tool_choice=None):
        last = msgs[-1]
        tool_turn = tool_choice != "none" and (fault == "loop" or (mode == "tool" and last["role"] == "user"))
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
            content, tc = ("" if fault == "empty" else reply(msgs)), []
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


def load_prices(models, quantization):
    """For each OpenRouter model, from its endpoints list now: the highest price per field over the endpoints the
    quantization filter admits ("reserve", the budget's upper bound, since routing may fall back to any of them)
    and the lowest ("typical", sort by price tries it first; the estimate's). Refuses a model with no such endpoint."""
    for model in models:
        e, m = endpoint_of(model)
        if e != "openrouter" or model.startswith(("stub:", "fake:")) or model in PRICES:
            continue
        eps = [x for x in openrouter.endpoint_prices(m) if quantization == "any" or x["quantization"] == quantization]
        eps = [x for x in eps if x["prompt"] is not None and x["completion"] is not None]
        if not eps:
            raise SystemExit(f"no {quantization} endpoint with a price for {m}")
        cache = lambda x: x["cache_read"] if x["cache_read"] is not None else x["prompt"]
        fields = lambda x: (x["prompt"], x["completion"], cache(x))
        PRICES[model] = {"reserve": tuple(max(fields(x)[i] for x in eps) for i in range(3)),
                         "typical": tuple(min(fields(x)[i] for x in eps) for i in range(3)),
                         "endpoints": len(eps), "quantization": quantization,
                         "fetched": time.strftime("%Y-%m-%dT%H:%M:%S")}
    return {m: PRICES[m] for m in models if m in PRICES}


def price(model, which="reserve"):
    """USD per token (prompt, completion, cache read). KeyError for a model without a known price, so it is refused."""
    e, m = endpoint_of(model)
    if model.startswith("stub:") or e == "ollama":
        return (0.0, 0.0, 0.0)
    if e == "openai":
        i, o, c = openrouter.OPENAI_PRICE[m]
        return (i, o, c)
    return PRICES[model][which]


def max_cost(model, msgs, tools, max_tokens):
    """The most a call can cost: its prompt at RESERVE_CHARS characters per token, plus max_tokens."""
    if model.startswith("fake:"):
        return float(model.split(":")[1])
    p = price(model)
    chars = len(json.dumps(msgs)) + len(json.dumps(tools or []))
    return chars / RESERVE_CHARS * p[0] + max_tokens * p[1]


def live_client(config):
    def call(model, msgs, tools, tool_choice=None):
        e, m = endpoint_of(model)
        kw = {k: config[k] for k in ("temperature", "max_tokens")}
        kw["tool_choice"] = tool_choice
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
    with every call made so far and its cost. A turn that reaches ROUNDS is closed by one more call with tools
    forbidden and FINAL_NOW (forced_final), the same for every arm."""
    msgs, tools, calls, tlog, turns, err, extra = [], [], [], [], [], None, {}

    def ask(t, tool_choice=None):
        held = budget.reserve(max_cost(model, msgs, tools, max_tokens))
        try:
            res = client(model, msgs, tools, tool_choice)
            res["cost"] = call_cost(res, model)
        except BaseException:
            budget.settle(held, held)           # cost unknown: count the reservation
            calls.append({"turn": t, "cost": held, "cost_estimated": True, "prompt_tokens": None,
                          "completion_tokens": None, "seconds": None, "tool_calls": 0})
            raise
        budget.settle(held, res["cost"])
        calls.append(dict({k: res.get(k) for k in CALL_FIELDS}, turn=t, tool_calls=len(res.get("tool_calls") or []),
                          sent_chars=len(json.dumps(msgs)) + len(json.dumps(tools)), **({"forced": True} if tool_choice else {})))
        cut = truncation(res, msgs, tools, context)
        if cut:
            raise Truncated(cut)
        return res

    try:
        msgs.append({"role": "system", "content": system_prompt(arm, n, kind)})
        tools = tools_for(arm)
        for t, text in enumerate(user_turns(item), 1):
            msgs.append({"role": "user", "content": text})
            for i in range(ROUNDS[kind]):
                res = ask(t)
                tcs = res.get("tool_calls") or []
                msgs.append(res.get("message") or {"role": "assistant", "content": res["content"]})
                if not tcs:
                    break
                for tc in tcs:
                    out, log = execute(arm, n, tc["function"]["name"], tc["function"].get("arguments"))
                    tlog.append(dict(log, turn=t, call=len(calls)))
                    msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": out})
            limit = bool(tcs)
            if limit:
                msgs.append({"role": "user", "content": FINAL_NOW})
                res = ask(t, "none")
                msgs.append({"role": "assistant", "content": res["content"]})   # any tool call it still makes is dropped
            turns.append({"turn": t, "content": res["content"], "reasoning": res.get("reasoning") or "",
                          "tool_limit": limit, "forced_final": limit, "empty": not (res["content"] or "").strip()})
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


# ---------------------------------------------------------------- estimate (before any call; PLAN-v3-bench-full §1.3)

def _read(path):
    import gzip
    with (gzip.open(path, "rt") if str(path).endswith(".gz") else open(path)) as f:
        return [json.loads(l) for l in f if l.strip()]


def calibrate(path=CALIB, judge=JUDGE_CALIB):
    """Per (kind, arm, N) of the pilot, the mean per cell of: calls, uncached prompt, cached prompt and completion
    tokens, and turns at the call limit (each now costs one more forced call, of the cell's mean size). Also the
    ratio of the pilot's charged cost to its tokens at the model's current typical price (routing does not always
    reach the cheapest endpoint) and the judge's mean cost per analyst session."""
    recs = [r for r in _read(path) if not r.get("error")]
    cal = {}
    for r in recs:
        c = cal.setdefault((r["kind"], r["arm"], r["n"]), [0, 0, 0, 0, 0, 0])
        cached = sum(x.get("cached_tokens") or 0 for x in r["calls"])
        for k, v in enumerate((len(r["calls"]), sum(x["prompt_tokens"] or 0 for x in r["calls"]) - cached, cached,
                               sum(x["completion_tokens"] or 0 for x in r["calls"]),
                               sum(1 for t in r["turns"] if t.get("tool_limit")), 1)):
            c[k] += v
    per = {}
    for key, (k, u, ca, co, lim, m) in cal.items():
        per[key] = {"calls": (k + lim) / m, "uncached": u / m * (1 + lim / k), "cached": ca / m * (1 + lim / k),
                    "completion": co / m * (1 + lim / k)}
    model = recs[0]["model"]
    load_prices([model], recs[0]["config"]["provider"]["quantizations"][0])
    p = price(model, "typical")
    tok = sum(tok_cost(r_tokens(r), p) for r in recs)
    j = [x for x in _read(judge) if not x.get("error")]
    return {"cells": per, "model": model, "factor": sum(r["cost"] for r in recs) / tok,
            "judge_session": sum(x["cost"] for x in j) / len(j), "source": str(pathlib.Path(path).relative_to(ROOT))}


def r_tokens(r):
    cached = sum(x.get("cached_tokens") or 0 for x in r["calls"])
    return {"uncached": sum(x["prompt_tokens"] or 0 for x in r["calls"]) - cached, "cached": cached,
            "completion": sum(x["completion_tokens"] or 0 for x in r["calls"])}


def tok_cost(t, p):
    return t["uncached"] * p[0] + t["completion"] * p[1] + t["cached"] * p[2]


def cell_tokens(cal, kind, arm, n):
    """The pilot's mean cell; G+ analyst uses G's; N between pilot sizes interpolated linearly in N."""
    arm = "G" if (kind, arm) == ("analyst", "G+") else arm
    ns = sorted(m for (k, a, m) in cal["cells"] if (k, a) == (kind, arm))
    lo = max([m for m in ns if m <= n] or ns[:1]); hi = min([m for m in ns if m >= n] or ns[-1:])
    a, b = cal["cells"][(kind, arm, lo)], cal["cells"][(kind, arm, hi)]
    w = 0 if hi == lo else (n - lo) / (hi - lo)
    return {f: a[f] + w * (b[f] - a[f]) for f in a}


def estimate(jobs, cal=None):
    """USD for these jobs: pilot tokens at each model's typical price times the pilot's factor; judge per analyst
    session. Assumes the tokens transfer to other models and to T with its design tools (both untested)."""
    cal = cal or calibrate()
    by, tot = {}, {"cells": 0, "calls": 0.0, "usd": 0.0, "judge_usd": 0.0}
    for j in jobs:
        t = cell_tokens(cal, j["kind"], j["arm"], j["n"])
        usd = 0.0 if j["model"].startswith(("stub:", "fake:")) else tok_cost(t, price(j["model"], "typical")) * cal["factor"]
        k = (j["model"], j["kind"], j["arm"])
        b = by.setdefault(k, [0, 0.0]); b[0] += 1; b[1] += usd
        tot["cells"] += 1; tot["calls"] += t["calls"]; tot["usd"] += usd
        tot["judge_usd"] += cal["judge_session"] if j["kind"] == "analyst" else 0.0
    return by, tot


def print_estimate(jobs):
    cal = calibrate()
    by, t = estimate(jobs, cal)
    print(f"Estimate from {cal['source']} (model {cal['model']}): pilot tokens per cell at the current typical "
          f"(cheapest fp8) price x {cal['factor']:.2f} (pilot charged / typical); forced final calls added; judge "
          f"${cal['judge_session']:.4f} per analyst session (medium). Assumes the tokens transfer to other models "
          "and to T with its design tools.")
    for (m, kind, arm), (c, usd) in sorted(by.items()):
        print(f"  {m:30} {kind:8} {arm:3} cells {c:4}  ${usd:.4f}")
    print(f"total: cells {t['cells']}  calls {t['calls']:.0f}  OpenRouter ${t['usd']:.2f}; judge (OpenAI Batch) "
          f"${t['judge_usd']:.2f}")
    return t


# ---------------------------------------------------------------- main

def main():
    openrouter.load_env()                 # first: refuses a .env that git does not ignore
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true", help="print the cost estimate of the selected cells and exit")
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
    live = [m for m in a.models if not m.startswith(("stub:", "fake:"))]
    prices = load_prices(live, a.quantization)            # refuses a model without a priced endpoint
    if not a.out and not a.estimate:
        ap.error("--out is required to run")
    out = pathlib.Path(a.out or "/dev/null")
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        done = {cell(r) for r in map(json.loads, out.read_text().splitlines()) if not r.get("error")}
    budget = Budget(a.budget, spent_in(out, *a.also))
    provider = None if a.quantization == "any" else {"quantizations": [a.quantization], "sort": "price"}
    config = {"temperature": a.temperature, "max_tokens": a.max_tokens, "provider": provider, "prices": prices}
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
    if a.estimate or live:
        est = print_estimate(jobs)
        if a.estimate:
            return
        if est["usd"] > a.budget - budget.spent:
            print(f"estimate ${est['usd']:.2f} exceeds the remaining budget ${a.budget - budget.spent:.2f}: no call made")
            sys.exit(2)
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
