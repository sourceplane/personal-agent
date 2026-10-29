# personal-agent — implementation plan

Three milestones, one task each, each landed as one pull request.

## PA0 — the spec (PA-1)

The repository is born with ai-slackbot's frame — `intent.yaml` (dev
verify-only, stage, prod after stage; the placeholder workspace
`ws_CHANGE_ME`, so CI plans nothing until it is linked), `ci.yml` as
ai-slackbot carries it, the shared TypeScript and ESLint configuration, the
wrangler renderer, the pnpm workspace and turbo pipeline, and the spec index
— and this doc set and the three task contracts land on it.

## PA1 — the agent on Workers (PA-2)

- `apps/api/src/index.ts`: the routes — `/` (the page, `src/ui.ts`),
  `/api/chat`, `/api/models`, `/api/memories` behind the owner's door
  (`src/auth.ts`), `/health`; `src/identity.ts` holds `API_NAME`.
- `src/models.ts` (Workers AI built in, `HF_MODELS`, the page's; the router
  through `@ai-sdk/openai-compatible`), `src/spaces.ts` (Gradio 5's HTTP API,
  the URL derived from the id), `src/agent.ts` (the system prompt with the
  owner's memories, the four tools, the no-tools retry), `src/memory.ts` (the
  `AgentMemory` Durable Object).
- `wrangler.jsonc` (the `AI` and `MEMORY` bindings in every environment, the
  `v1` SQLite migration) and `component.yaml` (`cloudflare-worker-turbo`, the
  three keys as optional secrets pushed by `runtimeSecrets`, a smoke over
  `/health` and the chat door). `LICENSE` (Apache-2.0) and `NOTICE` at the root.
- `tests/api`: vitest — every route in-process; the real `AgentMemory` over
  Node's SQLite (a `cloudflare:workers` stub for its base class); stand-ins
  for the AI binding, the router (one model that refuses tools) and a Gradio
  Space; the door's 503 and 401s; the name seam.
- The README: unlock it, add Hugging Face models, run, test, deploy.

Done when typecheck, lint, test and build are green, and `wrangler dev`
answers the page, the locked door and a chat against the stand-ins.

## PA2 — a baseline (PA-3)

ai-slackbot's baseline machinery, renamed and adapted: the console card
(`blueprint.yaml`) and the build document (`repo-blueprint.yaml`) — two
phases, `01-product` in one landing and `02-docs` recording what went live —
the rename engine with its one seam (`API_NAME`), the context pack, the
deployment-record hook probing `/health` and the chat door, and the
baseline's tests: contract, leak, placement, and the end-to-end tier serving
the staged Worker as born and unlocked (its Durable Object under miniflare),
driving chats on Workers AI, a Hugging Face model and two Spaces through the
stand-ins (`testing/lib/fake-workers-ai.js`, `fake-hf.py`, `agent-e2e.py`).
