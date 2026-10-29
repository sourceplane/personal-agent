#!/usr/bin/env python3
"""A stand-in for Hugging Face, for testing/e2e.test.sh only.

    fake-hf.py <port> <token>

The agent reaches Hugging Face two ways (apps/api/src/models.ts, spaces.ts):
the Inference Providers router's OpenAI-compatible /v1/chat/completions, and
a Gradio Space's HTTP API, /gradio_api/call/<endpoint> then its event stream.
The e2e points HF_ROUTER_URL at http://127.0.0.1:<port>/v1 and HF_SPACES_URL
at http://127.0.0.1:<port>/spaces, and this answers both deterministically:
the router echoes the last user message as "HF <model>: <text>" and refuses
a wrong token with a 401; a Space answers "<owner>/<name> says: <text>" on
its `chat` endpoint and 404s any other. GET /calls is every call it saw,
with whether it carried the token (never the token itself).
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

port, token = int(sys.argv[1]), sys.argv[2]
calls, jobs = [], {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, body, ctype="application/json"):
        raw = body if isinstance(body, str) else json.dumps(body)
        self.send_response(status)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(raw.encode())))
        self.end_headers()
        self.wfile.write(raw.encode())

    def record(self, body=None):
        calls.append({"method": self.command, "path": self.path, "token": self.headers.get("authorization") == f"Bearer {token}", "body": body})

    def do_GET(self):
        if self.path == "/calls":
            return self.reply(200, calls)
        parts = self.path.strip("/").split("/")
        # spaces/<owner>/<name>/gradio_api/call/<endpoint>/<event_id>
        if len(parts) == 7 and parts[0] == "spaces" and parts[3:5] == ["gradio_api", "call"]:
            self.record()
            answer = jobs.get(parts[6])
            if answer is None:
                return self.reply(404, {"detail": "Not Found"})
            return self.reply(200, f'event: generating\ndata: {json.dumps([answer[:4]])}\n\nevent: complete\ndata: {json.dumps([answer])}\n\n', "text/event-stream")
        self.reply(404, {"error": "no such route"})

    def do_POST(self):
        n = int(self.headers.get("content-length") or 0)
        body = json.loads(self.rfile.read(n) or b"null")
        self.record(body)
        if self.path == "/v1/chat/completions":
            if self.headers.get("authorization") != f"Bearer {token}":
                return self.reply(401, {"error": "Invalid credentials in Authorization header"})
            last = next((m for m in reversed(body.get("messages", [])) if m.get("role") == "user"), {})
            content = last.get("content")
            text = content if isinstance(content, str) else "".join(p.get("text", "") for p in content or [])
            return self.reply(200, {
                "id": "chatcmpl-e2e", "object": "chat.completion", "created": 1, "model": body["model"],
                "choices": [{"index": 0, "message": {"role": "assistant", "content": f"HF {body['model']}: {text}"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 5, "total_tokens": 12},
            })
        parts = self.path.strip("/").split("/")
        if len(parts) == 6 and parts[0] == "spaces" and parts[3:5] == ["gradio_api", "call"]:
            if parts[5] != "chat":
                return self.reply(404, {"detail": "Not Found"})
            event_id = f"ev{len(jobs) + 1}"
            jobs[event_id] = f"{parts[1]}/{parts[2]} says: {body['data'][0]}"
            return self.reply(200, {"event_id": event_id})
        self.reply(404, {"error": "no such route"})


ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
