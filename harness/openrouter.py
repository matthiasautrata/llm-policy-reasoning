"""Minimal chat client for OpenAI-compatible endpoints (standard library only).

Endpoints: "openrouter" (the default; v2's request body unchanged), "openai" and "ollama" (local). The API key
comes from OPENROUTER_API_KEY or OPENAI_API_KEY (none for ollama) and is never logged. No identifying headers
are sent. Cost: OpenRouter's charged cost; OpenAI's from tokens and OPENAI_PRICE; ollama 0.
Every call returns what the run record needs: content, reasoning text, served model and provider,
token counts, cost and wall time. With tools (OpenAI-style definitions), the
assistant message is returned as sent ("message", to append to the conversation) with its "tool_calls".
"""
import json, os, random, re, time, urllib.error, urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
ENDPOINTS = {"openrouter": (URL, "OPENROUTER_API_KEY"),
             "openai": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY"),
             "ollama": ("http://localhost:11434/v1/chat/completions", None)}
# OpenAI USD per token (input, output, cached input), Standard tier, short context (<= 272K input); the Batch tier
# is half of each (the page's Batch table agrees). Checked 2026-11-26 against developers.openai.com/api/docs/pricing.
# Not listed: models OpenAI retires on 2026-12-11 (gpt-5, gpt-5-mini, gpt-5-nano, o3; /api/docs/deprecations).
OPENAI_PRICE_CHECKED = "2026-11-26"
OPENAI_PRICE = {"gpt-6.2-sol": (2.00e-6, 10.00e-6, 0.10e-6),
                "gpt-6.1-terra": (1.00e-6, 5.00e-6, 0.05e-6)}
RETRY = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}


class CallError(Exception):
    pass


def body(model, messages, *, temperature, max_tokens, reasoning=None, provider=None, tools=None, endpoint="openrouter"):
    """The request body for an endpoint (also one line of an OpenAI Batch file)."""
    if endpoint == "openai":
        b = {"model": model, "messages": messages, "max_completion_tokens": max_tokens}
        if temperature is not None:
            b["temperature"] = temperature
        if reasoning is not None:
            b["reasoning_effort"] = reasoning
    else:
        b = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        if endpoint == "openrouter":
            b["usage"] = {"include": True}
    if tools:
        b["tools"] = tools
    if endpoint == "openrouter":
        if reasoning is not None:
            b["reasoning"] = reasoning
        if provider is not None:
            b["provider"] = provider
    return b


def openai_cost(model, prompt, completion, cached, batch=False):
    if model not in OPENAI_PRICE:
        raise CallError(f"no OpenAI price for {model}")
    i, o, c = OPENAI_PRICE[model]
    usd = (prompt - cached) * i + cached * c + completion * o
    return usd / 2 if batch else usd


def chat(model, messages, *, temperature, max_tokens, reasoning=None, provider=None, tools=None, timeout=300, tries=5,
         endpoint="openrouter"):
    b = body(model, messages, temperature=temperature, max_tokens=max_tokens, reasoning=reasoning, provider=provider,
             tools=tools, endpoint=endpoint)
    url, env = ENDPOINTS[endpoint]
    headers = {"Content-Type": "application/json"}
    if env:
        key = os.environ.get(env)
        if not key:
            raise CallError(f"{env} is not set")
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=json.dumps(b).encode(), method="POST", headers=headers)
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
                return parse(d, endpoint, round(time.time() - t0, 3), attempt + 1)
        time.sleep(min(60, 2 ** attempt + random.random()))
    raise CallError(f"gave up after {tries} attempts: {last}")


def parse(d, endpoint="openrouter", seconds=None, attempts=1, batch=False):
    """A chat completion response -> the record fields (also for a Batch output line)."""
    c, u = d["choices"][0], d.get("usage") or {}
    m = c.get("message") or {}
    cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
    cost = u.get("cost") if endpoint == "openrouter" else 0.0 if endpoint == "ollama" else openai_cost(
        d.get("model") and _base(d["model"]), u.get("prompt_tokens") or 0, u.get("completion_tokens") or 0, cached or 0, batch)
    return {
        "content": m.get("content") or "",
        "reasoning": m.get("reasoning") or m.get("reasoning_content") or "",
        "finish_reason": c.get("finish_reason"),
        "model_served": d.get("model"),
        "provider": d.get("provider") or (endpoint if endpoint != "openrouter" else None),
        "generation_id": d.get("id"),
        "prompt_tokens": u.get("prompt_tokens"),
        "completion_tokens": u.get("completion_tokens"),
        "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        "cached_tokens": cached,
        "cost": cost,
        "seconds": seconds,
        "attempts": attempts,
        "tool_calls": m.get("tool_calls") or [],
        "message": {k: v for k, v in m.items() if k in ("role", "content", "tool_calls", "reasoning_details")},
    }


def _base(served):
    """OpenAI reports a dated snapshot (gpt-x-2026-01-01); the price table is keyed by the alias."""
    return served if served in OPENAI_PRICE else re.sub(r"-\d{4}-\d{2}-\d{2}$", "", served)
