"""OpenAI Batch API (standard library only): submit chat-completion requests as one batch, collect the results.

The key comes from OPENAI_API_KEY (environment, or .env via openrouter.load_env) and is never logged. Each result line is parsed with openrouter.parse(...,
"openai", batch=True), so its record has the same fields as a synchronous call and its cost is the Batch price
(half of Standard, openrouter.OPENAI_PRICE).
"""
import json, os, urllib.request, uuid

from harness import openrouter

API = "https://api.openai.com/v1"


def _req(method, path, data=None, ctype="application/json", raw=False, timeout=120):
    openrouter.load_env()
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise openrouter.CallError("OPENAI_API_KEY is not set")
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}", **({"Content-Type": ctype} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read()
    except urllib.error.HTTPError as e:
        raise openrouter.CallError(f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}")
    return b if raw else json.loads(b)


def lines(requests, model, max_tokens, reasoning=None):
    """requests: [(custom_id, messages)] -> the JSONL text of a Batch input file"""
    return "".join(json.dumps({"custom_id": cid, "method": "POST", "url": "/v1/chat/completions",
                               "body": openrouter.body(model, msgs, temperature=None, max_tokens=max_tokens,
                                                       reasoning=reasoning, endpoint="openai")}) + "\n"
                   for cid, msgs in requests)


def submit(jsonl, window="24h"):
    """Upload the input file and create the batch. -> the batch object (id, status, input_file_id, ...)"""
    bnd = uuid.uuid4().hex
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\nbatch\r\n"
            f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"batch.jsonl\"\r\n"
            f"Content-Type: application/jsonl\r\n\r\n").encode() + jsonl.encode() + f"\r\n--{bnd}--\r\n".encode()
    f = _req("POST", "/files", body, f"multipart/form-data; boundary={bnd}")
    return _req("POST", "/batches", json.dumps({"input_file_id": f["id"], "endpoint": "/v1/chat/completions",
                                                "completion_window": window}).encode())


def status(batch_id):
    return _req("GET", f"/batches/{batch_id}")


def results(batch):
    """A completed batch -> {custom_id: record fields, or {"error": ...}}"""
    out = {}
    for fid in (batch.get("output_file_id"), batch.get("error_file_id")):
        if fid:
            for line in _req("GET", f"/files/{fid}/content", raw=True).decode().splitlines():
                if line.strip():
                    out.update(parse_line(json.loads(line)))
    return out


def parse_line(o):
    r = o.get("response") or {}
    if o.get("error") or r.get("status_code") != 200:
        return {o["custom_id"]: {"error": json.dumps(o.get("error") or r.get("body"))[:600]}}
    return {o["custom_id"]: openrouter.parse(r["body"], "openai", batch=True)}
