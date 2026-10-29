# personal-agent

A **personal AI agent** — a chat page that answers with Workers AI or with
its owner's Hugging Face models (any model Hugging Face's Inference
Providers serve, the models HuggingChat runs included, and Gradio Spaces),
and remembers what it is told — running natively as a **Cloudflare Worker**,
and packaged as an **Orun baseline**: one command takes a new agent from
nothing to live on stage and prod, in its own repository, under its own name
— in ONE landing.

One [Hono](https://hono.dev) app is the whole Worker: its page at `/`, its
API under `/api`, and `/health`. The built-in models are Workers AI through
the Worker's own `AI` binding, so a fresh agent needs no AI key; Hugging
Face models are reached through the Inference Providers router with the
owner's token, and a Space through its Gradio API, at a URL derived from its
id so the token only goes to Hugging Face. What the agent remembers, and the
models added in its page, live in a SQLite-backed Durable Object; the
conversation stays in the owner's browser. The agent is born **locked**: it
deploys and every `/api` route says so until its owner stores an access
key. The factory around it — the blueprints, the rename, the bootstrap
helpers, the testing tiers — is
[ai-slackbot](https://github.com/sourceplane/ai-slackbot)'s, built the way
[cirrus-baseline](https://github.com/sourceplane/cirrus-baseline) is. See
[`specs/epics/personal-agent`](specs/epics/personal-agent/README.md) for the
design, the milestones and the as-built status.

## Instantiating a product

```bash
git clone --depth 1 --branch <baseline-tag> https://github.com/sourceplane/personal-agent
cd personal-agent
orun new --blueprint repo-blueprint.yaml --out ~/agents/adas-agent --run-hooks --resume \
  --set reponame=adas-agent --set productname="Ada's Agent" \
  --set githuborg=acme-inc --set subdomain=<workers-dev-subdomain>
```

Or, once the platform's registry lists it, from the Orun console (Baselines →
`personal-agent` → Build). Two phases — `01-product` (the repository, its CI and
the whole agent in one pull request, deployed to stage and prod by one
convergence, smoke-tested) and `02-docs` (the live deployment recorded) —
each landing one pull request in the new repository.
**[BOOTSTRAP.md](BOOTSTRAP.md)** is the operator guide;
[docs/phases/](docs/phases/README.md) has a page per phase.

The new repository receives the **agent only** — the Worker, its tests, its
CI, its tooling, a README of its own, its operating contract and its licence
— renamed throughout to the agent's name, repository and Cloudflare Worker.
None of this repository's machinery ships, and nothing that ships names it.

| What makes it a baseline | Where |
|---|---|
| The console card (inputs, secrets, programme) | `blueprint.yaml` |
| The build document (modules, phases, hooks) | `repo-blueprint.yaml` |
| This tree's identity, and the bootstrap's task contracts | `.baseline/` |
| The rename engine | `tooling/rebrand/rebrand.mjs` |
| The bootstrap's helpers (deferrals, redeploy marker, work-tree strip) | `tooling/bootstrap/` |
| The deployment-record renderer | `hooks/render-deployment-docs.sh` |
| The agent's README and context pack | `.baseline/product/README.md`, `ai/context/` |
| The baseline's tests: contract, leak, offline bootstrap, end to end | `testing/`, `.github/workflows/baseline.yml` |
| Cutting a `baseline-vN` tag | `.github/workflows/tag.yml` |

## What is here (the product)

| Surface | Where |
|---|---|
| The routes, and the owner's door (`503` before a key is stored, `401` for a wrong one) | `apps/api/src/index.ts`, `apps/api/src/auth.ts` |
| The page — chat, model picker, added models, memories | `apps/api/src/ui.ts` |
| The agent: system prompt, tools, the no-tools retry | `apps/api/src/agent.ts` |
| The models: Workers AI built in, `HF_MODELS`, the page's | `apps/api/src/models.ts` |
| Calling a Gradio Space | `apps/api/src/spaces.ts` |
| Memory and added models (the Durable Object) | `apps/api/src/memory.ts` |
| The agent's name (the rename's seam; its page, prompt and `/health`) | `apps/api/src/identity.ts` |
| The licence (Apache-2.0) and its attribution notice | `LICENSE`, `NOTICE` (both ship to every product, at its root) |
| Worker config (name, Workers AI and Durable Object bindings, its migration, per-environment vars) | `apps/api/wrangler.jsonc` |
| Deploy contract (and the keys it pushes as Worker secrets) | `apps/api/component.yaml` (`cloudflare-worker-turbo`) |
| Tests | `tests/api` (vitest: every route in-process, the real Durable Object over Node's SQLite, Workers AI and Hugging Face stood in for) |

## Getting started

```bash
pnpm install
pnpm typecheck
pnpm lint
pnpm test
pnpm build            # wrangler deploy --dry-run → apps/api/dist (the bundle, no upload)
```

Run the Worker locally under workerd (Workers AI has no local mode, so
`wrangler dev` needs `wrangler login`; the Durable Object runs locally; the
keys go in `apps/api/.dev.vars`):

```bash
printf 'AGENT_ACCESS_KEY=dev-key\n' > apps/api/.dev.vars
pnpm --filter @app/api dev        # http://localhost:8787 — enter dev-key
curl http://localhost:8787/health # {"status":"ok","name":"Personal AI Agent","environment":"local","access":"configured",…}
```

The product README (`.baseline/product/README.md`) says how to unlock the
agent and add Hugging Face models.

## The pieces, and why

| Need | Here |
|---|---|
| A model with no key | Workers AI through the `AI` binding: `@cf/moonshotai/kimi-k2.6` (the default) and `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, both calling tools |
| The owner's Hugging Face models | The Inference Providers router (`router.huggingface.co/v1`, OpenAI-compatible) through `@ai-sdk/openai-compatible`, with `HF_TOKEN`; an id may carry `:fastest`, `:cheapest` or a provider's name. A provider that refuses tools (`400`/`422`) is asked again without them |
| The owner's Spaces | Gradio 5's `/gradio_api/call/<endpoint>` and its event stream, at `https://<owner>-<name>.hf.space` — derived, never given, so the token reaches only Hugging Face |
| Memory | One SQLite-backed Durable Object per environment, created by the `v1` migration in `wrangler.jsonc` — no Terraform, on Workers Free. The conversation stays in the browser |
| Not spending the owner's models on anyone | One access key as a bearer token on every `/api` route, digests compared in constant time |
| Keys | Orun secrets per environment, pushed to the Worker as Worker secrets after each deploy (`runtimeSecrets`); none needed to deploy |
| Deploy on push | Orun deploys `<repo>-api-{stage,prod}` on merge to `main` and smoke-tests `/health` and the locked chat door (`apps/api/component.yaml`) |
| A copy of it for somebody else | `orun new --blueprint repo-blueprint.yaml` — a new repository, branded, deployed |

## CI

| Workflow | What it runs | Ships to an agent |
|---|---|---|
| `ci.yml` | the Orun pipeline, and the only workflow an agent carries: `orun plan --changed`, then one job per lane. A pull request runs the verify lanes (the Worker built, type-checked and dry-deployed per environment; the tests' `quick-check` lane installs and checks the package, it does not run them), except the bootstrap's own landings (`orun/BASE-*`), where `plan` alone is the check; a merge deploys stage → prod. It plans nothing while `intent.yaml` names the placeholder workspace `ws_CHANGE_ME`, as this repository does. A manual run (Orunbase's Deploy button, or Run workflow on `main`) plans the environment and components it names under the push-to-main trigger, so they deploy as a merge deploys them | yes |
| `baseline.yml` | the baseline's own tiers: contract tests, the blueprint read by the pinned orun, the leak gate, the offline bootstrap, the agent built, dry-deployed, served as born and unlocked, and driven against stand-ins for Workers AI and Hugging Face | no |
| `tag.yml` | cuts a `baseline-vN` tag (manual) | no |

## Licence

The agent is original code written for this baseline, licensed Apache-2.0 (`LICENSE`). Every product built from it carries `LICENSE` and `NOTICE` at its root, so GitHub (and openproduct) detects the licence, and NOTICE's "created with Orunbase" attribution travels with every redistribution (Apache-2.0 §4(d)).
