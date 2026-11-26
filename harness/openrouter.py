"""Minimal OpenRouter chat client (standard library only).

The API key comes from OPENROUTER_API_KEY and is never logged. No identifying headers are sent.
Every call returns what the run record needs: content, reasoning text, served model and provider,
token counts, the exact cost OpenRouter charged, and wall time. With tools (OpenAI-style definitions), the
assistant message is returned as sent ("message", to append to the conversation) with its "tool_calls".
"""
import json, os, random, time, urllib.error, urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
RETRY = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}


class CallError(Exception):
    pass


def chat(model, messages, *, temperature, max_tokens, reasoning=None, provider=None, tools=None, timeout=300, tries=5):
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
            "usage": {"include": True}}
    if tools:
        body["tools"] = tools
    if reasoning is not None:
        body["reasoning"] = reasoning
    if provider is not None:
        body["provider"] = provider
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise CallError("OPENROUTER_API_KEY is not set")
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last = None
    for attempt in range(tries):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}"
            if e.code not in RETRY:
                raise CallError(last)
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            last = f"{type(e).__name__}: {e}"
        else:
            if "error" in d:
                last = f"API error: {json.dumps(d['error'])[:300]}"
            elif not d.get("choices"):
                last = "no choices in response"
            else:
                c, u = d["choices"][0], d.get("usage") or {}
                m = c.get("message") or {}
                return {
                    "content": m.get("content") or "",
                    "reasoning": m.get("reasoning") or "",
                    "finish_reason": c.get("finish_reason"),
                    "model_served": d.get("model"),
                    "provider": d.get("provider"),
                    "generation_id": d.get("id"),
                    "prompt_tokens": u.get("prompt_tokens"),
                    "completion_tokens": u.get("completion_tokens"),
                    "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                    "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                    "cost": u.get("cost"),
                    "seconds": round(time.time() - t0, 3),
                    "attempts": attempt + 1,
                    "tool_calls": m.get("tool_calls") or [],
                    "message": {k: v for k, v in m.items() if k in ("role", "content", "tool_calls", "reasoning_details")},
                }
        time.sleep(min(60, 2 ** attempt + random.random()))
    raise CallError(f"gave up after {tries} attempts: {last}")
