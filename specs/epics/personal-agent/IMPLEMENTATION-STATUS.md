# personal-agent — implementation status

| Milestone | State | Landed |
|---|---|---|
| PA0 — the spec | ✅ | PA-1 |
| PA1 — the agent on Workers | ✅ | PA-2 |
| PA2 — a baseline | 🟡 built; `baseline-v1` not yet tagged | PA-3 |

## Choices made along the way

There is no upstream template: the agent is original. What follows is every
choice a reader of the code might otherwise have to reconstruct.

| # | What | Why |
|---|---|---|
| 1 | The app lives in `apps/api` of a pnpm workspace (`@app/api`), one Hono app: `/`, `/api/*`, `/health` | ai-slackbot's shape; a plain Worker |
| 2 | Every `/api` route is behind `AGENT_ACCESS_KEY` as a bearer token: `503 access_not_configured` before it is stored, `401` (with `WWW-Authenticate`) for a missing or wrong one; SHA-256 digests compared in constant time | Nobody else spends the owner's models; neither the key's length nor its prefix leaks through timing |
| 3 | The page is one self-contained document served by the Worker (`src/ui.ts`), the name HTML-escaped; the key and the conversation kept in localStorage | The browser talks to nothing else; the Worker stores nothing of what was said |
| 4 | Workers AI built in (`@cf/moonshotai/kimi-k2.6` default, `@cf/meta/llama-3.3-70b-instruct-fp8-fast`), `workers-ai-provider` 4.0.1 over the `AI` binding | No key by default; models that call tools |
| 5 | Hugging Face through `router.huggingface.co/v1` with `@ai-sdk/openai-compatible` 3.0.80 (the same `@ai-sdk/provider` 4.0.34 as `ai` 7.0.155) | One API for every provider; one provider core |
| 6 | A Hugging Face model refused with tools (`400`/`422`) is asked once more without them | Tool support varies by provider |
| 7 | Spaces through Gradio 5's `/gradio_api/call/<endpoint>`, the URL derived from the id, the endpoint `chat` by default, 90 s | The token only reaches Hugging Face |
| 8 | `HF_MODELS`: comma- or newline-separated; `space:<owner>/<name>[#<endpoint>]`; an entry that does not parse is dropped, never guessed at | Offered from the first deploy, validated like the page's |
| 9 | Models added in the page are validated by pattern (Hub id, Space id, endpoint name) and kept in the Durable Object; only those can be removed there | A URL is never a model id; the built-in and the secret's belong to the code and the secret |
| 10 | Memory in the `AgentMemory` Durable Object (SQLite, migration `v1`): the newest 500 facts, 500 characters each, the 30 most recent in every system prompt; `remember`/`recall`/`forget`/`currentTime` for a model that calls tools | Facts outlive a conversation; no Terraform |
| 11 | `generateText`, up to 6 steps, one JSON answer; a provider failure a `502` naming the model, the error logged by model key | Simple and testable; no token in a message |
| 12 | `GET /health`: `status`, `name`, `environment`, `access`, `huggingface`, `models` (default and counts), `tools`, `endpoints` — names only | The deploy's smoke and the bootstrap's probes read it |
| 13 | `src/identity.ts`: `API_NAME = "Personal AI Agent"`, the one rename seam (the page title, the system prompt, `/health`) | One seam |
| 14 | `wrangler.jsonc` (`<repo>-api`, `nodejs_compat`, `AI` and `MEMORY` in every environment, the migration) and `component.yaml` (`cloudflare-worker-turbo`, three optional secrets pushed by `runtimeSecrets`, a smoke over `/health` and the chat door) | The Worker's config and the deploy contract |
| 15 | `LICENSE` (Apache-2.0) and `NOTICE` at the root, both shipped | GitHub and openproduct detect the licence; NOTICE carries the Orunbase attribution (§4(d)) |
| 16 | Tests: `tests/api` (vitest, in-process) — every route, the door, the real `AgentMemory` over Node's SQLite, stand-ins for the AI binding, the router and a Space, the name seam | The Durable Object's SQL is the SQL that runs |

## Verified

- `pnpm typecheck`, `lint`, `test` (tests/api 26) and `build` green; the
  Worker is 225 KiB gzipped (1.24 MiB raw) — Workers Free. The dry run binds
  `env.MEMORY (AgentMemory)`, `env.AI` and `env.ENVIRONMENT`.
- Baseline CI tiers: to be recorded once they pass on the pinned orun.
