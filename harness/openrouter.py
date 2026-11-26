"""Minimal chat client for OpenAI-compatible endpoints (standard library only).

Endpoints: "openrouter" (the default; v2's request body unchanged), "openai" and "ollama" (local). The API key
comes from OPENROUTER_API_KEY or OPENAI_API_KEY (none for ollama), set in the environment or in the
git-ignored .env at the repo root (load_env; the environment wins), and is never logged. No identifying headers
are sent. Cost: OpenRouter's charged cost; OpenAI's from tokens and OPENAI_PRICE; ollama 0.
Every call returns what the run record needs: content, reasoning text, served model and provider,
token counts, cost and wall time. With tools (OpenAI-style definitions; tool_choice "none" forbids calling them), the
assistant message is returned as sent ("message", to append to the conversation) with its "tool_calls".
OpenAI with tools goes through the Responses API (Chat Completions refuses function tools with reasoning effort
for its reasoning models): the chat messages and tools are converted, the call is stateless (store false), and the
output items, encrypted reasoning included, ride on the assistant message ("output_items") and are sent back
verbatim on the next call, so the model keeps its reasoning across tool calls. The result has the chat fields.
"""
import hashlib
import json, os, random, re, time, urllib.error, urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
ENDPOINTS = {"openrouter": (URL, "OPENROUTER_API_KEY"),
             "openai": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY"),
             "openai-responses": ("https://api.openai.com/v1/responses", "OPENAI_API_KEY"),
             "ollama": ("http://localhost:11434/v1/chat/completions", None)}
# OpenAI USD per token (input, output, cached input), Standard tier, short context (<= 272K input); the Batch tier
# is half of each (the page's Batch table agrees). Checked 2026-11-26 against developers.openai.com/api/docs/pricing.
# Not listed: models OpenAI retires on 2026-12-11 (gpt-5, gpt-5-mini, gpt-5-nano, o3; /api/docs/deprecations).
OPENAI_PRICE_CHECKED = "2026-11-26"
OPENAI_PRICE = {"gpt-6.2-sol": (2.00e-6, 10.00e-6, 0.10e-6),
                "gpt-6.1-terra": (1.00e-6, 5.00e-6, 0.05e-6)}
RETRY = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}


class CallError(Exception):
    """refused: every attempt was answered with an HTTP error status, so the endpoint did no work and charged
    nothing (PLAN-v3-bench-full §3f.1). Any other failure (timeout, dropped connection, an error in a 200 body)
    may have been charged."""
    def __init__(self, msg, refused=False):
        super().__init__(msg)
        self.refused = refused


ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def load_env(path=ENV_FILE):
    """Read KEY=VALUE lines from the repo's .env into os.environ; variables already set win.

    Refuses (CallError) unless git ignores the file and only its owner can read it. No value is ever put in a
    message, log or record."""
    if not os.path.exists(path):
        return
    import subprocess
    if subprocess.run(["git", "check-ignore", "-q", path], cwd=os.path.dirname(path), capture_output=True).returncode != 0:
        raise CallError(f"{path} is not git-ignored; refusing to read it")
    if os.stat(path).st_mode & 0o077:
        raise CallError(f"{path} is readable by group or others; run chmod 600 {path}")
    with open(path) as f:
        for line in f:
            k, sep, v = line.strip().partition("=")
            if sep and k and not k.startswith("#") and v.strip():
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def body(model, messages, *, temperature, max_tokens, reasoning=None, provider=None, tools=None, tool_choice=None,
         endpoint="openrouter"):
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
        if tool_choice is not None:
            b["tool_choice"] = tool_choice
    if endpoint == "openrouter":
        if reasoning is not None:
            b["reasoning"] = reasoning
        if provider is not None:
            b["provider"] = provider
    return b


def responses_body(model, messages, *, temperature, max_tokens, reasoning=None, tools=None, tool_choice=None):
    """Chat messages and tools -> a stateless Responses API request. The prompt cache key is the system prompt's
    hash, so calls sharing that prefix are routed to the same cache."""
    items = []
    for m in messages:
        if m["role"] == "tool":
            items.append({"type": "function_call_output", "call_id": m["tool_call_id"], "output": m["content"]})
        elif m["role"] == "assistant" and m.get("output_items"):
            items.extend(m["output_items"])
        elif m["role"] == "assistant":
            if m.get("content"):
                items.append({"role": "assistant", "content": m["content"]})
            items.extend({"type": "function_call", "call_id": tc["id"], "name": tc["function"]["name"],
                          "arguments": tc["function"]["arguments"]} for tc in m.get("tool_calls") or [])
        else:
            items.append({"role": m["role"], "content": m["content"]})
    b = {"model": model, "input": items, "max_output_tokens": max_tokens, "store": False,
         "include": ["reasoning.encrypted_content"]}
    sys_ = next((m["content"] for m in messages if m["role"] == "system"), "")
    b["prompt_cache_key"] = hashlib.sha256(sys_.encode()).hexdigest()[:32]
    if temperature is not None:
        b["temperature"] = temperature
    if reasoning is not None:
        b["reasoning"] = {"effort": reasoning}
    if tools:
        b["tools"] = [{"type": "function", "name": t["function"]["name"], "description": t["function"].get("description", ""),
                       "parameters": t["function"]["parameters"], "strict": False} for t in tools]
        if tool_choice is not None:
            b["tool_choice"] = tool_choice
    return b


def parse_responses(d, seconds=None, attempts=1):
    """A Responses API response -> the record fields of parse()."""
    out, u = d.get("output") or [], d.get("usage") or {}
    text = "".join(c.get("text", "") for o in out if o.get("type") == "message" for c in o.get("content") or []
                   if c.get("type") == "output_text")
    tcs = [{"id": o["call_id"], "type": "function", "function": {"name": o["name"], "arguments": o["arguments"]}}
           for o in out if o.get("type") == "function_call"]
    cached = (u.get("input_tokens_details") or {}).get("cached_tokens") or 0
    inc = (d.get("incomplete_details") or {}).get("reason")
    return {
        "content": text,
        "reasoning": "",
        "finish_reason": "tool_calls" if tcs else "length" if inc == "max_output_tokens" else inc or "stop",
        "model_served": d.get("model"),
        "provider": "openai",
        "generation_id": d.get("id"),
        "prompt_tokens": u.get("input_tokens"),
        "completion_tokens": u.get("output_tokens"),
        "reasoning_tokens": (u.get("output_tokens_details") or {}).get("reasoning_tokens"),
        "effort": (d.get("reasoning") or {}).get("effort"),           # as served
        "cached_tokens": cached,
        "cost": openai_cost(d.get("model") and _base(d["model"]), u.get("input_tokens") or 0, u.get("output_tokens") or 0, cached),
        "seconds": seconds,
        "attempts": attempts,
        "tool_calls": tcs,
        "message": {"role": "assistant", "content": text or None, "tool_calls": tcs, "output_items": out},
    }


def endpoint_prices(model, timeout=30):
    """OpenRouter's public endpoints list for a model (no key) -> [{provider, quantization, prompt, completion,
    cache_read}], USD per token (cache_read None where not listed)."""
    url = f"https://openrouter.ai/api/v1/models/{model}/endpoints"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=timeout) as r:
        eps = json.loads(r.read())["data"]["endpoints"]
    f = lambda v: float(v) if v not in (None, "") else None
    return [{"provider": e.get("provider_name"), "quantization": e.get("quantization"), "prompt": f(e["pricing"].get("prompt")),
             "completion": f(e["pricing"].get("completion")), "cache_read": f(e["pricing"].get("input_cache_read"))}
            for e in eps]


def openai_cost(model, prompt, completion, cached, batch=False):
    if model not in OPENAI_PRICE:
        raise CallError(f"no OpenAI price for {model}")
    i, o, c = OPENAI_PRICE[model]
    usd = (prompt - cached) * i + cached * c + completion * o
    return usd / 2 if batch else usd


def chat(model, messages, *, temperature, max_tokens, reasoning=None, provider=None, tools=None, tool_choice=None,
         timeout=300, tries=5, endpoint="openrouter"):
    if endpoint == "openai" and tools:
        endpoint = "openai-responses"
        b = responses_body(model, messages, temperature=temperature, max_tokens=max_tokens, reasoning=reasoning,
                           tools=tools, tool_choice=tool_choice)
    else:
        b = body(model, messages, temperature=temperature, max_tokens=max_tokens, reasoning=reasoning, provider=provider,
                 tools=tools, tool_choice=tool_choice, endpoint=endpoint)
    url, env = ENDPOINTS[endpoint]
    headers = {"Content-Type": "application/json"}
    if env:
        load_env()
        key = os.environ.get(env)
        if not key:
            raise CallError(f"{env} is not set")
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=json.dumps(b).encode(), method="POST", headers=headers)
    last, refused = None, True
    for attempt in range(tries):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}"
            if e.code not in RETRY:
                raise CallError(last, refused)
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            last, refused = f"{type(e).__name__}: {e}", False
        else:
            if d.get("error"):
                last, refused = f"API error: {json.dumps(d['error'])[:300]}", False
            elif endpoint == "openai-responses":
                return parse_responses(d, round(time.time() - t0, 3), attempt + 1)
            elif not d.get("choices"):
                last = "no choices in response"
            else:
                return parse(d, endpoint, round(time.time() - t0, 3), attempt + 1)
        time.sleep(min(60, 2 ** attempt + random.random()))
    raise CallError(f"gave up after {tries} attempts: {last}", refused)


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
