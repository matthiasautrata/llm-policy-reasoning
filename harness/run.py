"""Run read-mode questions against a model and append one JSONL record per call.

  python harness/run.py --layer 0 --worlds S-s1 S-s2 --repr text structured formal --n 3 \\
      --model deepseek/deepseek-v4.1-flash --out results/m2-read-L0.jsonl --budget 2.00

--config decided (default) shows the layer with its decisions; open shows every fork of the layer
with all its readings and no decision (keys from keys.json "open").
--prompt base (default, the M2 prompt) or assume (adds a required assumptions list to the JSON).
Resumable: a record already in --out (same world, layer, config, prompt, repr, model, question, rep, no error)
is not run again. --budget caps the summed OpenRouter cost of the whole file, earlier runs included.
Stub models make no calls and cost nothing:
  stub:key      answers with the decided key (scoring must give 100%)
  stub:abstain  always UNDERDETERMINED
  stub:garbage  never emits JSON (exercises the parse-failure path)
  stub:answer   always ANSWER with the type's zero value (overreach on every UNDERDETERMINED key)
"""
import argparse, concurrent.futures as cf, json, pathlib, sys, threading, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness import openrouter, read      # noqa: E402


def cell(r):
    return (r["world"], r["layer"], r.get("cfg", "decided"), r.get("prompt", "base"), r["repr"], r["model"], r["qid"], r["rep"])


def stub(model, key):
    if model == "stub:key":
        o = {"status": key["status"], "value": key.get("value"), "readings": key.get("readings"), "missing": None,
             "assumptions": []}
    elif model == "stub:abstain":
        o = {"status": "UNDERDETERMINED", "value": None, "readings": None, "missing": "everything"}
    elif model == "stub:answer":
        o = {"status": "ANSWER", "value": key.get("value", 0), "readings": None, "missing": None,
             "assumptions": ["the obvious reading"]}
    elif model == "stub:garbage":
        return "I cannot say."
    else:
        raise SystemExit(f"unknown stub {model}")
    return "Reasoning omitted.\n" + json.dumps(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", type=int, required=True)
    ap.add_argument("--config", choices=["decided", "open"], default="decided")
    ap.add_argument("--prompt", choices=list(read.PROMPTS), default="base")
    ap.add_argument("--worlds", nargs="+", required=True)
    ap.add_argument("--repr", nargs="+", default=["text", "structured", "formal"], choices=list(read.FILES))
    ap.add_argument("--n", type=int, default=3, help="repetitions per cell")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=float, default=1.0, help="USD cap on the summed cost in --out")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--reasoning-effort", default=None, help="low | medium | high; omitted = provider default")
    ap.add_argument("--quantization", default="fp8", help="provider quantization filter; 'any' to disable")
    ap.add_argument("--only-provider", nargs="+", help="serve from these providers only (cheapest available first, "
                    "falling back within the list); failed calls are recorded as errors and retried on resume")
    ap.add_argument("--templates", nargs="*", help="only these templates (e.g. Q01 Q12)")
    ap.add_argument("--limit", type=int, help="at most this many new calls")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done, spent = set(), 0.0
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            spent += r.get("cost") or 0.0
            if not r.get("error"):
                done.add(cell(r))

    reasoning = {"effort": a.reasoning_effort} if a.reasoning_effort else None
    provider = None if a.quantization == "any" else {"quantizations": [a.quantization], "sort": "price"}
    if a.only_provider:
        provider = dict(provider or {}, only=a.only_provider)   # allow_fallbacks=false would try the first one only
    config = {"temperature": a.temperature, "max_tokens": a.max_tokens, "reasoning": reasoning, "provider": provider}

    jobs = []
    for w in a.worlds:
        d = ROOT / "worlds" / w
        qs = json.loads((d / "questions.json").read_text())
        keys = json.loads((d / "keys.json").read_text())[a.config]
        for rep in a.repr:
            for q in qs:
                if a.templates and q["template"] not in a.templates:
                    continue
                for i in range(a.n):
                    base = {"world": w, "layer": a.layer, "cfg": a.config, "prompt": a.prompt, "repr": rep, "mode": "read", "model": a.model,
                            "qid": q["id"], "template": q["template"], "type": q["type"], "rep": i}
                    if cell(base) not in done:
                        jobs.append((d, q, keys[q["id"]][f"L{a.layer}"], base))
    if a.limit is not None:
        jobs = jobs[:a.limit]
    print(f"{len(done)} cells already done, {len(jobs)} to run; spent so far ${spent:.4f} of ${a.budget:.2f}")

    lock, stop = threading.Lock(), threading.Event()
    stats = {"spent": spent, "ok": 0, "err": 0}

    def run(job):
        d, q, key, base = job
        if stop.is_set():
            return
        msgs = read.messages(d, a.layer, base["repr"], q, a.config, a.prompt)
        rec = dict(base, params=q["params"], config=config, ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
        try:
            if a.model.startswith("stub:"):
                res = {"content": stub(a.model, key), "reasoning": "", "cost": 0.0, "model_served": a.model}
            else:
                res = openrouter.chat(a.model, msgs, temperature=a.temperature, max_tokens=a.max_tokens,
                                      reasoning=reasoning, provider=provider)
            rec.update(res, error=None, tool_calls=0)
            rec["parsed"] = read.parse(res["content"], q["type"])
        except openrouter.CallError as e:
            rec.update(error=str(e), cost=0.0)
        with lock:
            with out.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            stats["spent"] += rec.get("cost") or 0.0
            stats["err" if rec["error"] else "ok"] += 1
            n = stats["ok"] + stats["err"]
            if n % 25 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)}  ok {stats['ok']}  err {stats['err']}  ${stats['spent']:.4f}", flush=True)
            if stats["spent"] >= a.budget and not stop.is_set():
                stop.set()
                print(f"budget ${a.budget:.2f} reached; stopping", flush=True)

    if stats["spent"] >= a.budget:
        print("budget already reached"); sys.exit(1)
    with cf.ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(run, jobs))
    print(f"done: ok {stats['ok']}, errors {stats['err']}, total spent ${stats['spent']:.4f}")
    sys.exit(1 if stop.is_set() or stats["err"] else 0)


if __name__ == "__main__":
    main()
