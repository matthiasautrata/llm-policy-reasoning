#!/usr/bin/env python3
"""Send a paper draft to several models as reviewer or copy-editor.

    .venv/bin/python paper/v3/review/review.py DRAFT --role reviewer|copyedit --budget USD [--models M ...] [--voice FILE]

The system prompt is <role>.md plus STYLE.md (plus the voice sample, if given). One output file per model:
out/<draft>.<role>.<model>.md, git-ignored. A call is made only if its worst case fits the remaining budget.
Model ids: OpenRouter ids, or openai@<id> for the OpenAI endpoint."""
import argparse, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from harness import openrouter                      # noqa: E402

MODELS = ["openai@gpt-6.2-sol", "z-ai/glm-5.3-prime", "deepseek/deepseek-v4-pro", "moonshotai/kimi-k3.1-pro"]
MAX_TOKENS = {"reviewer": 12000, "copyedit": 12000, "reader": 4000}
CHARS_PER_TOKEN = 3                                 # pessimistic, for the reservation only


def split(model):
    e, _, m = model.partition("@")
    return (e, m) if m else ("openrouter", model)


def price(model):
    """Worst-case USD per token (prompt, completion)."""
    e, m = split(model)
    if e == "openai":
        return openrouter.OPENAI_PRICE[m][:2]
    eps = openrouter.endpoint_prices(m)
    return max(x["prompt"] for x in eps), max(x["completion"] for x in eps)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("draft", type=pathlib.Path)
    ap.add_argument("--role", choices=MAX_TOKENS, required=True)
    ap.add_argument("--budget", type=float, required=True, help="USD cap for this invocation")
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--voice", type=pathlib.Path, help="the author's own unassisted writing, for the copy-editor")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--persona", help="who the reader is (role reader)")
    a = ap.parse_args()

    system = "\n\n".join([(HERE / f"{a.role}.md").read_text()]
                         + ([(HERE / "STYLE.md").read_text()] if a.role != "reader" else [])
                         + ([f"# Voice sample\n\n{a.voice.read_text()}"] if a.voice else [])
                         + ([f"# The reader\n\n{a.persona}"] if a.persona else []))
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": a.draft.read_text()}]
    chars = sum(len(m["content"]) for m in msgs)
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    spent = 0.0
    for model in a.models:
        pin, pout = price(model)
        worst = chars / CHARS_PER_TOKEN * pin + MAX_TOKENS[a.role] * pout
        if spent + worst > a.budget:
            print(f"skip {model}: up to ${worst:.2f}, ${a.budget - spent:.2f} left")
            continue
        e, m = split(model)
        r = openrouter.chat(m, msgs, temperature=None if e == "openai" else 0.7, max_tokens=MAX_TOKENS[a.role],
                            reasoning=a.effort if e == "openai" else {"effort": a.effort}, endpoint=e)
        spent += r["cost"] or worst
        f = out / f"{a.draft.stem}.{a.role}.{model.replace('/', '_').replace('@', '_')}.md"

        f.write_text((f"<!-- persona: {a.persona} -->\n" if a.persona else "") + f"<!-- {r['model_served']} · {r['prompt_tokens']}+{r['completion_tokens']} tokens · "
                     f"${r['cost'] or 0:.4f} · finish {r['finish_reason']} -->\n\n{r['content']}\n")
        print(f"{model}: ${r['cost'] or 0:.4f} -> {f.relative_to(HERE)}")
    print(f"spent ${spent:.4f} of ${a.budget:.2f}")


if __name__ == "__main__":
    main()
