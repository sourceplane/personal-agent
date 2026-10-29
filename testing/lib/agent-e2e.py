#!/usr/bin/env python3
"""The served agent's routes, for testing/e2e.test.sh.

    agent-e2e.py born      <url> <values.json>
    agent-e2e.py connected <url> <values.json>   (ACCESS_KEY, HF_TOKEN, HF_STANDIN,
                                                  DEV_LOG in the env)

`born` is the Worker as a bootstrap produces it, no key stored: the page and
/health, and the owner's door saying the agent is locked without doing any
work. `connected` is the same Worker with its access key, a Hugging Face
token and HF_MODELS stored, Hugging Face pointed at testing/lib/fake-hf.py:
the door refusing a wrong key, the models it offers, a chat on Workers AI, a
fact remembered through the tool and carried into the next conversation by
the real Durable Object, a Hugging Face model and two Spaces answering, and
what each was asked, read back from the stand-ins. The model is the Workers
AI stand-in (testing/lib/fake-workers-ai.js), whose calls the agent's
wrangler log records.
"""
import json
import os
import sys
import urllib.error
import urllib.request

mode, base, values_path = sys.argv[1], sys.argv[2], sys.argv[3]
name = json.load(open(values_path))["productname"]
problems = []
DEFAULT = "workers-ai:@cf/moonshotai/kimi-k2.6"


def bad(m):
    problems.append(m)


def req(method, path, body=None, key=None, base_url=None):
    headers = {"content-type": "application/json"}
    if key is not None:
        headers["authorization"] = f"Bearer {key}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request((base_url or base) + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode()
            status, hdrs = resp.status, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw, status, hdrs = e.read().decode(), e.code, dict(e.headers)
    try:
        return status, hdrs, json.loads(raw)
    except ValueError:
        return status, hdrs, raw


def finish(summary):
    if problems:
        for p in problems:
            print(f"  ✕ {p}", file=sys.stderr)
        sys.exit(1)
    print(f"   {summary}")


# ── what every mode answers the same way ──────────────────────────────────
s, h, page = req("GET", "/")
# The page escapes the name as apps/api/src/ui.ts does (the fixture's has an
# apostrophe and an ampersand).
title = "".join({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}.get(ch, ch) for ch in name)
if s != 200 or not str(h.get("Content-Type", h.get("content-type", ""))).startswith("text/html") or f"<title>{title}</title>" not in str(page):
    bad(f"/ is not the agent's page: {s} {str(page)[:120]!r}")

s, _, health = req("GET", "/health")
if not isinstance(health, dict):
    health = {}
    bad("/health is not JSON")
if s != 200 or health.get("status") != "ok" or health.get("name") != name:
    bad(f"/health does not name the agent: {s} {json.dumps(health)[:200]}")
if health.get("environment") != "stage":
    bad(f"/health reports environment {health.get('environment')!r}, not 'stage'")
if health.get("tools") != ["remember", "recall", "forget", "currentTime"]:
    bad(f"/health's tools are {health.get('tools')!r}")
if (health.get("models") or {}).get("default") != DEFAULT:
    bad(f"/health's default model is {health.get('models')!r}")

s, _, _ = req("GET", "/no-such-route")
if s != 404:
    bad(f"/no-such-route answered {s}, want 404")

chat_hi = {"messages": [{"role": "user", "content": "hi"}]}

if mode == "born":
    if health.get("access") != "not configured" or health.get("huggingface") != "not connected":
        bad(f"as born, /health reports access {health.get('access')!r}, Hugging Face {health.get('huggingface')!r}")
    for key in (None, "any-key"):
        for method, path, body in (("POST", "/api/chat", chat_hi), ("GET", "/api/models", None), ("GET", "/api/memories", None)):
            s, _, answer = req(method, path, body, key=key)
            if s != 503 or not isinstance(answer, dict) or answer.get("error") != "access_not_configured":
                bad(f"as born, {method} {path} answered {s} {str(answer)[:120]!r}, want 503 access_not_configured")
    finish(f"/ is {name!r}'s page, /health names it in stage, locked, Workers AI the default; an unknown path 404; /api/* 503 access_not_configured")
    sys.exit(0)

# ── connected ─────────────────────────────────────────────────────────────
key, hf_token, standin, dev_log = os.environ["ACCESS_KEY"], os.environ["HF_TOKEN"], os.environ["HF_STANDIN"], os.environ["DEV_LOG"]


def hf_calls():
    return req("GET", "/calls", base_url=standin)[2]


if health.get("access") != "configured" or health.get("huggingface") != "connected" or health["models"].get("configured") != 2:
    bad(f"connected, /health reports {json.dumps(health)[:240]}")
if key in json.dumps(health) or hf_token in json.dumps(health):
    bad("/health printed a secret value")

# 1. The door refuses what is not the key, and does no work.
for k in (None, "wrong-key", key + "x"):
    s, h, answer = req("POST", "/api/chat", chat_hi, key=k)
    if s != 401 or answer.get("error") != "unauthorized":
        bad(f"a request with key {k!r:.12} answered {s} {str(answer)[:80]!r}, want 401")
if hf_calls():
    bad(f"a refused request reached Hugging Face: {json.dumps(hf_calls())[:300]}")

# 2. The models it offers: built in, then HF_MODELS's.
s, _, listed = req("GET", "/api/models", key=key)
keys = [m["key"] for m in listed.get("models", [])] if isinstance(listed, dict) else []
want = [DEFAULT, "workers-ai:@cf/meta/llama-3.3-70b-instruct-fp8-fast", "huggingface:org/model-a", "space:me/my-chat"]
if s != 200 or keys != want or listed.get("huggingface") is not True:
    bad(f"GET /api/models answered {s} {keys}, want {want}")

# 3. Workers AI answers; a fact is remembered by the tool and survives into
#    the next conversation, through the real Durable Object.
s, _, answer = req("POST", "/api/chat", chat_hi, key=key)
if s != 200 or answer.get("text") != "Echo: hi" or answer.get("model") != DEFAULT:
    bad(f"a chat on the default model answered {s} {str(answer)[:160]!r}")
s, _, answer = req("POST", "/api/chat", {"messages": [{"role": "user", "content": "remember: Prefers tea to coffee."}]}, key=key)
if s != 200 or answer.get("tools") != ["remember"] or "Prefers tea to coffee." not in answer.get("text", ""):
    bad(f"remembering answered {s} {str(answer)[:200]!r}")
s, _, mem = req("GET", "/api/memories", key=key)
facts = [m["text"] for m in mem.get("memories", [])] if isinstance(mem, dict) else []
if facts != ["Prefers tea to coffee."]:
    bad(f"the agent's memory holds {facts!r}")
req("POST", "/api/chat", {"model": "workers-ai:@cf/meta/llama-3.3-70b-instruct-fp8-fast", "messages": [{"role": "user", "content": "what do I drink?"}]}, key=key)

# 4. Hugging Face: a model from HF_MODELS through the router, with the token.
s, _, answer = req("POST", "/api/chat", {"model": "huggingface:org/model-a", "messages": [{"role": "user", "content": "hello hub"}]}, key=key)
if s != 200 or answer.get("text") != "HF org/model-a: hello hub":
    bad(f"the Hugging Face model answered {s} {str(answer)[:200]!r}")

# 5. Spaces: one from HF_MODELS, one added in the page, then removed.
s, _, answer = req("POST", "/api/chat", {"model": "space:me/my-chat", "messages": [{"role": "user", "content": "first"}, {"role": "assistant", "content": "ok"}, {"role": "user", "content": "hello space"}]}, key=key)
if s != 200 or answer.get("text") != "me/my-chat says: hello space":
    bad(f"the configured Space answered {s} {str(answer)[:200]!r}")
s, _, added = req("POST", "/api/models", {"provider": "space", "id": "me/other-space", "label": "Other"}, key=key)
if s != 201 or added.get("model", {}).get("key") != "space:me/other-space":
    bad(f"adding a Space answered {s} {str(added)[:200]!r}")
s, _, answer = req("POST", "/api/chat", {"model": "space:me/other-space", "messages": [{"role": "user", "content": "hi"}]}, key=key)
if s != 200 or answer.get("text") != "me/other-space says: hi":
    bad(f"the added Space answered {s} {str(answer)[:200]!r}")
s, _, _ = req("DELETE", "/api/models/space/me/other-space", key=key)
s2, _, answer = req("POST", "/api/chat", {"model": "space:me/other-space", "messages": [{"role": "user", "content": "hi"}]}, key=key)
if s != 200 or s2 != 400 or answer.get("error") != "unknown_model":
    bad(f"a removed Space answered {s}/{s2} {str(answer)[:160]!r}")
s, _, answer = req("POST", "/api/models", {"provider": "huggingface", "id": "https://evil.example/v1"}, key=key)
if s != 400:
    bad(f"adding a URL as a model answered {s}, want 400")

# 6. What Hugging Face saw: the router and the Spaces, every call with the token.
calls = hf_calls()
paths = [f"{c['method']} {c['path'].rsplit('/', 1)[0] if c['method'] == 'GET' else c['path']}" for c in calls]
want_paths = [
    "POST /v1/chat/completions",
    "POST /spaces/me/my-chat/gradio_api/call/chat",
    "GET /spaces/me/my-chat/gradio_api/call/chat",
    "POST /spaces/me/other-space/gradio_api/call/chat",
    "GET /spaces/me/other-space/gradio_api/call/chat",
]
if paths != want_paths:
    bad(f"Hugging Face saw {paths}, want {want_paths}")
if not all(c["token"] for c in calls):
    bad("a call to Hugging Face did not carry the owner's token")
router = next((c["body"] for c in calls if c["path"] == "/v1/chat/completions"), {})
if router.get("model") != "org/model-a" or [t["function"]["name"] for t in router.get("tools", [])] != ["remember", "recall", "forget", "currentTime"]:
    bad(f"the router was asked {json.dumps(router)[:300]}")

# 7. What Workers AI was asked: the built-in models, the tools, and the
#    remembered fact in the conversation after it was saved.
log = open(dev_log, encoding="utf-8", errors="replace").read()
asked = [json.loads(line.split("fake-workers-ai ", 1)[1]) for line in log.splitlines() if "fake-workers-ai {" in line]
models = [a["model"] for a in asked]
if models[:3] != ["@cf/moonshotai/kimi-k2.6"] * 3 or models[3:] != ["@cf/meta/llama-3.3-70b-instruct-fp8-fast"]:
    bad(f"Workers AI was asked {models}")
if not any(a["roles"][-1:] == ["tool"] for a in asked):
    bad("no model call carried a tool's result back")
if not asked or asked[-1]["remembers"] != ["- [1] Prefers tea to coffee."]:
    bad(f"the next conversation was not told the remembered fact: {asked[-1:] }")

# 8. The owner can forget it.
s, _, _ = req("DELETE", "/api/memories/1", key=key)
s2, _, mem = req("GET", "/api/memories", key=key)
if s != 200 or mem.get("memories") != []:
    bad(f"forgetting answered {s}, and the memory holds {mem!r}")

finish(f"refused 3 wrong keys with no call made; 4 models offered; Workers AI answered and remembered through the Durable Object; a Hugging Face model and 2 Spaces answered with the token — {len(asked)} Workers AI calls, {len(calls)} Hugging Face calls")
