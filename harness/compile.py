"""Compile mode: the model writes plans (intermediate models) that the engine validates and executes.

A plan is plain data: {"readings": {fork: reading}, "goal": "<Prolog goal over the material's predicates>"}.
The model gives one to three plans in one reply (k candidates, one call); engine/compile.pl checks each
statically, runs it (expanding open forks the plan leaves unfixed, in the open configuration), and
aggregates: one distinct value -> ANSWER, several -> AMBIGUOUS. Validation or execution errors get one
repair turn. Abstentions are the model's to declare; CONFLICT is declared by the model (no plan) or
detected by the engine (a plan whose value differs in the exclusion-enforced program: the rule base derives
G and excluded(G)); records keep the two apart (parsed.engine_conflict).

Compile is offered for formal and structured material only (plans over declared relations); text has no
declared predicates to plan over. That asymmetry is reported, not hidden.
"""
import functools, json, pathlib, re, subprocess

from harness import read

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPRS = ("formal", "structured")
REPLY_STATUSES = ("PLAN", "CONFLICT", "UNDERDETERMINED", "OUT_OF_SCOPE")
MAX_PLANS = 3
BUILTINS = ("= \\= == \\== @< @> @=< @>= compare/3 < > =< >= =:= =\\= is between/3 succ/2 plus/3 "
            "atom/1 number/1 integer/1 atomic/1 var/1 nonvar/1 ground/1 is_list/1 "
            "member/2 memberchk/2 length/2 append/3 nth0/3 nth1/3 last/2 msort/2 sort/2 sort/4 list_to_set/2 "
            "sum_list/2 max_list/2 min_list/2 max_member/2 min_member/2 subtract/3 intersection/3 union/3; "
            "control: , ; -> \\+ once/1 forall/2 findall/3 setof/3 bagof/3 (with ^) and "
            "aggregate_all/3 (count, sum(E), max(E), min(E), bag(E), set(E))")

DATE_NOTE = {
    "formal": "",
    "structured": " In plans, dates are integers YYYYMMDD (2026-03-05 is 20260305), as the engine stores them.",
}

INSTRUCTIONS = """You answer questions about the records of a procurement organisation by writing a plan that an engine
runs against the records. {format_note}{date_note}

A plan is a Prolog goal over the predicates of the material (listed below) and a few built-ins. The engine
executes the goal on the records and its result is the answer; do not compute the answer yourself.
- If the question asks for a value or a list, the goal binds the variable V to it: one solution for a single
  value, one solution per member for a list (the engine removes duplicates).
- If the question asks whether something is so, the answer is whether the goal holds; V is not needed.
- Identifiers are atoms written as in the material (cc1_2, r017, pending); amounts are integers.
- Allowed built-ins: {builtins}. Nothing else: no assert, no input or output, no call/N, no module prefixes.

Predicates of the material (name/arity; arguments in the order the material gives them):
{predicates}

Use only what the material gives. Do not assume definitions, rules or data that it does not give. Classify
your reply with one status:

- PLAN: the material defines what the question needs. Give the plan. If the material leaves a question of
  interpretation open and the answer may depend on it, give one plan per reading (at most three), each naming
  the reading it adopts in readings, as {{"<id of the question of interpretation>": "<reading>"}}; the engine runs every plan and
  compares the results. Otherwise give one plan, with readings {{}}.
- CONFLICT: the material contradicts itself on this question and nothing in it says which side prevails.
- UNDERDETERMINED: the question is about something the material covers, but answering needs a definition,
  rule or data that the material does not give. Say what is missing.
- OUT_OF_SCOPE: the question is about something the material has no notion of at all.

Think as long as you need, then end your reply with one line holding a JSON object, and nothing after it:
{{"status": "<PLAN, CONFLICT, UNDERDETERMINED or OUT_OF_SCOPE>", "plans": [{{"readings": {{}}, "goal": "<goal>"}}] or null, "missing": "<what is missing>" or null}}

<material>
{material}
</material>"""

QUESTION = """Question: {text}
The answer, if the material settles it, is {hint}."""

REPAIR = """The engine reports:
{errors}
Reply again, ending with one JSON line in the same format. You may change the plans or the status."""


@functools.lru_cache(maxsize=None)
def predicates(layer):
    out = subprocess.run([str(ROOT / "engine/ask"), "--layer", str(layer), "--capabilities"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(ln.split()[1] for ln in out.splitlines() if ln.strip())     # alphabetical: no layer order shown


def messages(world_dir, layer, rep, q, cfg="decided"):
    if rep not in REPRS:
        raise ValueError(f"compile mode is not offered for {rep} material")
    note = read.FORMAT_NOTE[rep] + (read.RULES_NOTE[rep] if layer >= 1 else "")
    sys_ = INSTRUCTIONS.format(format_note=note, date_note=DATE_NOTE[rep], builtins=BUILTINS,
                               predicates="\n".join(predicates(layer)),
                               material=read.material(world_dir, layer, rep, cfg).rstrip())
    return [{"role": "system", "content": sys_},
            {"role": "user", "content": QUESTION.format(text=q["text"], hint=read.TYPE_HINT[q["type"]])}]


def parse_reply(content):
    """-> (status, plans, missing, errors). errors: what a repair turn reports."""
    o = read._last_json(content)
    if o is None:
        return None, [], None, ["no JSON line with a status field was found at the end of the reply"]
    st = str(o.get("status", "")).strip().upper().replace(" ", "_")
    if st == "ANSWER" and o.get("plans"):        # a plan under the read-mode status name: accept it as PLAN
        st = "PLAN"
    if st not in REPLY_STATUSES:
        return None, [], o.get("missing"), [f"unknown status {st!r} (use PLAN, CONFLICT, UNDERDETERMINED or OUT_OF_SCOPE)"]
    if st != "PLAN":
        return st, [], o.get("missing"), []
    ps = o.get("plans")
    if isinstance(ps, dict):
        ps = [ps]
    if not isinstance(ps, list) or not ps:
        return st, [], o.get("missing"), ["status PLAN needs at least one plan"]
    plans, errs = [], []
    if len(ps) > MAX_PLANS:          # not silently truncated: the first three run, and the excess is reported for repair
        errs.append(f"the reply gives {len(ps)} plans; give at most {MAX_PLANS} (only the first {MAX_PLANS} were run)")
    for p in ps[:MAX_PLANS]:
        if isinstance(p, str):
            p = {"goal": p}
        if not isinstance(p, dict):
            continue
        g = str(p.get("goal") or "").strip().rstrip(".").strip()
        rd = p.get("readings") if isinstance(p.get("readings"), dict) else {}
        plans.append({"readings": {str(k): str(v) for k, v in rd.items()}, "goal": g})
    if not plans:
        errs.append("the plans are not in the form {\"readings\": {...}, \"goal\": \"...\"}")
    return st, plans, o.get("missing"), errs


def execute(world, layer, cfg, typ, plans):
    req = {"world": str(ROOT / "worlds" / world), "layer": layer, "config": cfg, "type": typ, "plans": plans}
    p = subprocess.run(["swipl", str(ROOT / "engine/compile.pl")], input=json.dumps(req),
                       capture_output=True, text=True, timeout=600)
    line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    if p.returncode != 0 or not line:
        raise RuntimeError(f"engine/compile.pl failed: {p.stderr.strip()[-500:]}")
    return json.loads(line)


def evaluate(world, layer, cfg, typ, content):
    """One reply -> outcome: the reply's status and plans, the engine result, and the errors to repair."""
    st, plans, missing, errs = parse_reply(content)
    out = {"reply_status": st, "plans": plans, "missing": missing, "engine": None}
    if st == "PLAN" and plans:
        e = execute(world, layer, cfg, typ, plans)
        out["engine"] = e
        errs = errs + e["errors"]
    out["errors"] = errs
    return out


def parsed(o, typ):
    """The read-mode parse fields (status, value, reading_values) of an outcome, for score.py."""
    p = {"alias": False, "status": None, "value": None, "readings": None, "missing": o["missing"], "parse_error": None}
    if o["reply_status"] in (None, "PLAN"):
        e = o["engine"]
        if not e or e["status"] is None:
            p["parse_error"] = "no plan ran: " + "; ".join(o["errors"])[:300]
            return p
        p["status"] = e["status"]
        p["engine_conflict"] = bool(e.get("engine_conflict")) or any(
            v == "CONFLICT" for v in (e.get("readings") or {}).values())
        if e["status"] == "ANSWER":
            p["value"] = read.norm_value(e["value"], typ)
        elif e["status"] == "AMBIGUOUS":
            p["readings"] = e["readings"]
            p["reading_values"] = sorted({read.reading_value(v, typ) for v in e["readings"].values()})
    else:
        p["status"] = o["reply_status"]
    return p


def surfaced(plans):
    """Forks the model itself split on: fixed to different readings by different plans."""
    seen = {}
    for p in plans:
        for f, r in p["readings"].items():
            seen.setdefault(f, set()).add(r)
    return sorted(f for f, rs in seen.items() if len(rs) > 1)


def answer(call, world_dir, world, layer, rep, q, cfg):
    """Run one question in compile mode. call(messages) -> openrouter.chat-like dict.
    Returns the record fields: the final reply's fields, first/final outcomes, parsed, summed usage."""
    msgs = messages(world_dir, layer, rep, q, cfg)
    res = call(msgs)
    first = evaluate(world, layer, cfg, q["type"], res["content"])
    turns = [res]
    final = first
    if first["errors"]:
        msgs2 = msgs + [{"role": "assistant", "content": res["content"]},
                        {"role": "user", "content": REPAIR.format(errors="\n".join(f"- {e}" for e in first["errors"]))}]
        res2 = call(msgs2)
        turns.append(res2)
        final = evaluate(world, layer, cfg, q["type"], res2["content"])
    rec = dict(turns[-1])
    rec["content_first"] = turns[0]["content"] if len(turns) > 1 else None
    for f in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens", "cost", "seconds"):
        vals = [t.get(f) for t in turns if t.get(f) is not None]
        rec[f] = sum(vals) if vals else None
    if len(turns) > 1:
        rec["reasoning"] = (turns[0].get("reasoning") or "") + "\n\n[repair turn]\n\n" + (turns[1].get("reasoning") or "")
    rec.update(turns=len(turns), first=first, final=final,
               parsed=parsed(final, q["type"]), parsed_first=parsed(first, q["type"]),
               surfaced=surfaced(final["plans"]), surfaced_first=surfaced(first["plans"]))
    return rec


# ---------- stubs (no calls) ----------
def stub(model, key, q, msgs):
    """stub:key plans the bank goal, or its resolve goal where it has one (abstains or declares CONFLICT where the key does); stub:repair first
    calls a predicate the material lacks, then, on the repair turn, behaves as stub:key; stub:plan always plans the
    bank goal, whatever the key (so the engine, not the stub, detects CONFLICT and blocks calls above the layer)."""
    repair_turn = msgs[-1]["role"] == "user" and msgs[-1]["content"].startswith("The engine reports")
    if model == "stub:repair" and not repair_turn:
        o = {"status": "PLAN", "plans": [{"readings": {}, "goal": "no_such_relation(V)"}], "missing": None}
    elif model == "stub:plan":       # always plans the bank goal: engine-detected CONFLICT, blocked calls at low layers
        o = {"status": "PLAN", "plans": [{"readings": {}, "goal": q["goal"]}], "missing": None}
    elif model in ("stub:key", "stub:repair"):
        if key["status"] in ("UNDERDETERMINED", "OUT_OF_SCOPE", "CONFLICT"):
            o = {"status": key["status"], "plans": None, "missing": "stub"}
        else:
            o = {"status": "PLAN", "plans": [{"readings": {}, "goal": q.get("resolve") or q["goal"]}], "missing": None}
    else:
        raise SystemExit(f"unknown compile stub {model}")
    return {"content": "Plan follows.\n" + json.dumps(o), "reasoning": "", "cost": 0.0, "model_served": model}
