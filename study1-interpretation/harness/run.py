"""Run prompts against models and append run records to a JSONL file for score.py.

  pip install litellm            # one client for Anthropic, OpenAI, OpenRouter, DeepSeek, Ollama, ...
  python harness/run.py --models anthropic/claude-sonnet-4-5 openrouter/deepseek/deepseek-v4-pro \
                        --prompts p07 p08 p09 p10 p11 p12 --reps 3 --out results/runs.jsonl
  python harness/score.py results/runs.jsonl

Oracle arms (p04, p11, p18): each `ASK: pred(args)` line is answered by Soufflé over exactly the
arm's rules and facts, and the model gets another turn. p17: the one clarifying question is
declined. The loop stops at the first reply without ASK lines, or after --max-turns.
"""
import argparse, json, pathlib, re, subprocess, tempfile, time

root = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = json.loads((root / "prompts/manifest.json").read_text())
WORLD = {"A": root / "oracle/small/rules.dl", "B": root / "oracle/large/rules.dl"}
FACTS = {"A": None, "B": root / "oracle/large/facts.dl"}
ASK = re.compile(r"^\s*ASK:\s*(.+?)\s*$", re.M)


def prompt_file(pid):
    m = MANIFEST.get(pid)
    return root / "prompts" / (m["file"] if m else next(p.name for p in (root / "prompts").glob(f"{pid}-*")))


# ---------- Soufflé-backed oracle ----------
def decls(program):
    return {m[1]: [t.split(":")[1].strip() for t in m[2].split(",")]
            for m in re.finditer(r"\.decl\s+(\w+)\(([^)]*)\)", program)}


def ask(phase, query):
    program = WORLD[phase].read_text() + (FACTS[phase].read_text() if FACTS[phase] else "")
    m = re.fullmatch(r"(\w+)\((.*)\)\.?", query.strip())
    types = decls(program).get(m[1]) if m else None
    if not types:
        return f"error: unknown predicate in {query!r}"
    args = [a.strip().strip("'\"") for a in m[2].split(",")] if m[2].strip() else []
    if len(args) != len(types):
        return f"error: {m[1]} takes {len(types)} arguments"
    vars_, terms = [], []
    for a, t in zip(args, types):
        if a == "_" or a[:1].isupper():
            if a != "_" and a not in [v for v, _ in vars_]:
                vars_.append((a, t))
            terms.append(a)
        else:
            terms.append(a if t == "number" else f'"{a}"')
    head = ", ".join(f"{v}:{t}" for v, t in vars_) or "ok:number"
    body = f"{m[1]}({', '.join(terms)})"
    rule = f"ask_q({', '.join(v for v, _ in vars_)}) :- {body}." if vars_ else f"ask_q(1) :- {body}."
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "q.dl").write_text(program + f"\n.decl ask_q({head})\n.output ask_q\n{rule}\n")
        r = subprocess.run(["souffle", "-w", "-D", d, f"{d}/q.dl"], capture_output=True, text=True)
        if r.returncode:
            return "error: " + r.stderr.strip().splitlines()[0]
        rows = [l.split("\t") for l in pathlib.Path(d, "ask_q.csv").read_text().splitlines() if l]
    if not vars_:
        return "true" if rows else "false"
    return "; ".join(", ".join(f"{v}={x}" for (v, _), x in zip(vars_, row)) for row in rows) or "no rows"


def oracle_reply(pid, text):
    qs = ASK.findall(text)
    if pid == "p17":
        return "No clarification is available. Answer every scenario from the material as given."
    return "ORACLE RESULTS\n" + "\n".join(f"ASK: {q}\n=> {ask(MANIFEST[pid]['phase'], q)}" for q in qs) + \
           "\n\nNow give your final answer for every scenario in the required format."


# ---------- model loop ----------
def run_one(model, pid, max_turns, temperature):
    import litellm
    msgs = [{"role": "user", "content": prompt_file(pid).read_text()}]
    turns = []
    for _ in range(max_turns):
        r = litellm.completion(model=model, messages=msgs, temperature=temperature)
        text = r.choices[0].message.content or ""
        turns.append(text)
        if not ASK.search(text) or pid not in ("p04", "p11", "p17", "p18"):
            break
        msgs += [{"role": "assistant", "content": text}, {"role": "user", "content": oracle_reply(pid, text)}]
    return dict(prompt=pid, model=model, run=f"{model}|{pid}|{time.strftime('%Y%m%dT%H%M%S')}",
                text=turns[-1], turns=turns, asks=sum(len(ASK.findall(t)) for t in turns))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--prompts", nargs="+", default=["p07", "p08", "p09", "p10", "p11", "p12",
                                                      "p13", "p14", "p15", "p16", "p17", "p18", "x01"])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--out", default=str(root / "results/runs.jsonl"))
    a = ap.parse_args()
    with open(a.out, "a") as f:
        for model in a.models:
            for pid in a.prompts:
                for i in range(a.reps):
                    rec = run_one(model, pid, a.max_turns, a.temperature)
                    f.write(json.dumps(rec) + "\n"); f.flush()
                    print(model, pid, i + 1, "asks:", rec["asks"])
