"""Convert the recovered Hermes transcripts into run records for score.py."""
import hashlib, json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
by_md5 = {v["md5"]: k for k, v in json.loads((root / "prompts/manifest.json").read_text()).items()}
out = []
for line in (root / "transcripts/hermes_sessions_20260831.jsonl").read_text().splitlines():
    s = json.loads(line)
    msgs = s["messages"]
    user = next(m["content"] for m in msgs if m["role"] == "user")
    final = [m["content"] for m in msgs if m["role"] == "assistant" and m["content"]]
    out.append(dict(prompt=by_md5[hashlib.md5(user.encode()).hexdigest()], model=s["session"]["model"],
                    run=s["session"]["id"], tool_calls=s["session"]["tool_call_count"],
                    text=final[-1] if final else ""))
dst = root / "results/original-20260831.jsonl"
dst.write_text("".join(json.dumps(r) + "\n" for r in out))
print(len(out), "runs ->", dst)
