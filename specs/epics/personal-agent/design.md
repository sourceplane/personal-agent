# personal-agent — design

## 1. The agent

One owner, one agent. It answers in its own page at `/` (`src/ui.ts`) and
over `POST /api/chat`, with a model the owner picks per conversation:
Workers AI built in, a Hugging Face Inference Providers model, or a Gradio
Space. It remembers facts about its owner across conversations, and the
owner adds and removes models in the page without a redeploy. It is not a
port of a template: the product is original, and the repository machinery
around it — blueprints, rename, bootstrap helpers, the testing tiers — is
ai-slackbot's, renamed.

## 2. Where it runs

One plain Cloudflare Worker (`cloudflare-worker-turbo`): a Hono app whose
default export is the module handler, serving its page (one self-contained
document — no script, style or font from anywhere else), its API and
`/health`. Two bindings, neither wired: the account's Workers AI (`AI`) and
the agent's own Durable Object (`MEMORY`, class `AgentMemory`), created by
wrangler from the `v1` migration in `wrangler.jsonc`. No Terraform, no
Static Assets.

**Rejected:** Static Assets for the page (a second thing to deploy for one
document); D1 or KV for memory (Terraform roots and wiring for what one
object per environment holds); a separate frontend Worker.

## 3. The models

`src/models.ts` lists every model the agent offers, and `/api/chat` refuses
any other:

- **Workers AI**, through the `AI` binding via `workers-ai-provider` —
  `@cf/moonshotai/kimi-k2.6` (the default; ai-chatbot's and ai-slackbot's)
  and `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, both calling tools. No
  key, so a fresh agent answers with nothing but its access key.
- **Hugging Face Inference Providers**, through the router's
  OpenAI-compatible API (`https://router.huggingface.co/v1`) via
  `@ai-sdk/openai-compatible`, with the owner's `HF_TOKEN`. One API reaches
  every provider the Hub routes to — the models HuggingChat runs included —
  and the AI SDK's tool loop works over it unchanged. An id may carry the
  router's own `:fastest`, `:cheapest` or `:<provider>` suffix. Tool support
  varies by provider, so a request refused with tools (`400` or `422`) is
  asked once more without them; any other failure is not retried. Without
  `HF_TOKEN` such a model is a `409` before anything is called.
- **Gradio Spaces** (§4).

Hugging Face models come from `HF_MODELS` (a secret, offered from the first
deploy) and from the page (kept in the Durable Object). Keys are unique; the
built-in list wins, then the secret's, then the page's.

The agent runs `generateText` — up to 6 steps — and answers once, as JSON
(`{text, model, tools}`); a provider failure is a `502` naming the model.

**Rejected:** streaming for now (one JSON answer is simpler to test end to
end and to fail cleanly — risk PA-E); AI SDK 7's string model ids (they
route through Vercel's AI Gateway); brokering the token from the
workspace's Hugging Face integration (it is connect-only: it has no secret
template to mint from).

## 4. Spaces

A Space is called through Gradio 5's HTTP API: `POST
<space>/gradio_api/call/<endpoint>` with `{"data": [<message>]}` returns an
`event_id`; `GET …/<event_id>` is an event stream ending in `complete` (the
outputs) or `error`. The endpoint defaults to `chat` — what
`gr.ChatInterface` exposes — and takes the message alone, so the agent sends
the owner's last message and reads the first output back as text (a string,
a message's `content`, or a history's last assistant turn). 90 s, then it
gives up.

**The URL is derived, never given**: `<owner>/<name>` is
`https://<owner>-<name>.hf.space`, so the owner's `HF_TOKEN` — sent so a
private Space answers — only ever reaches Hugging Face. `HF_SPACES_URL` (and
`HF_ROUTER_URL`) are test-only overrides for the stand-ins.

**Rejected:** a user-supplied Space URL (it would send the token wherever it
pointed); `@gradio/client` (a heavier dependency for two requests).

## 5. Memory

One SQLite-backed Durable Object per environment, named `owner`
(`src/memory.ts`), reached over RPC. Two tables: `memories` (the newest 500,
500 characters each) and `models` (the page's, at most 50). Every model is
told the 30 most recent memories in its system prompt; a model that calls
tools also gets `remember`, `recall` (a word match), `forget` and
`currentTime`. A Space sees only the message. The conversation itself is
NOT stored: it lives in the owner's browser (localStorage), so the Worker
keeps nothing of what was said.

**Rejected:** storing conversations server-side (more to secure, nothing the
owner asked for); semantic memory search (Vectorize is wiring and an
embedding call per turn — later, if word match falls short).

## 6. The owner's door and the keys

Every `/api` route needs `Authorization: Bearer <AGENT_ACCESS_KEY>` (SHA-256
digests compared in constant time, `src/auth.ts`). With no key stored the
route answers `503 access_not_configured` and does nothing; a missing or
wrong key is a `401`. A public workers.dev URL would otherwise spend the
owner's Workers AI and Hugging Face credit on anyone. `/` and `/health` are
open; the page shows nothing of the owner's until the key is entered.

The agent's keys — `AGENT_ACCESS_KEY`, `HF_TOKEN`, `HF_MODELS` — are the
owner's Orun secrets per environment, declared in `optionalSecretEnv` and
pushed to the Worker as Worker secrets after each deploy by the
composition's `secrets-live` step (`runtimeSecrets`). None reaches a build.
The agent is therefore born locked and says so.

The repository is ai-slackbot's (hono-api's shape): `apps/api`, `tests/api`,
the shared tooling, two phases. `/health` reports access, Hugging Face, the
model counts and the tools by name, and the deploy's smoke checks it and
that `/api/chat` refuses a request without the key — the one check that
needs nobody's key.
