# personal-agent — where this repository stands

The entry page for anyone (or any agent) picking this repository up. It is
this repository's own state and does not ship to an agent built from it; the
two pages that do are [operations.md](operations.md) and
[deployment.md](deployment.md).

## What it is

A personal AI agent — a chat page and `/api/chat` answered with Workers AI
or the owner's Hugging Face models (Inference Providers, the models
HuggingChat runs included) and Gradio Spaces, remembering what it is told in
a SQLite-backed Durable Object — as one Cloudflare Worker, packaged as an
Orun baseline: `orun new --blueprint repo-blueprint.yaml` builds a new agent
in its own repository and takes it to live on stage and prod in one landing
(`01-product`), then records what went live (`02-docs`). The agent is born
locked; its owner stores an access key, and optionally a Hugging Face token
and models, afterwards. The factory around it (blueprints, rebrand,
bootstrap tooling, the testing tiers) is ai-slackbot's, carried over
unchanged in shape.

## Release

| | |
|---|---|
| Latest tag | none yet — `baseline-v1` is cut by PA2 (the baseline) |
| Proven live | No. Everything short of the platform is proven offline in Baseline CI — the staged Worker served by `wrangler dev`, as born and unlocked, its Durable Object run by miniflare, against stand-ins for Workers AI and Hugging Face's router and Spaces; a live bootstrap from a tag, a real Workers AI answer and a real Hugging Face call are still to come (risks PA-A, PA-B) |

## Where to read

| Question | Page |
|---|---|
| What shipped, and every choice made along the way | `specs/epics/personal-agent/IMPLEMENTATION-STATUS.md` |
| Why it is built this way | [decisions.md](decisions.md), then `specs/epics/personal-agent/design.md` |
| What could still go wrong | [open-risks.md](open-risks.md), then `specs/epics/personal-agent/risks-and-open-questions.md` |
| How to instantiate it | `BOOTSTRAP.md`, `docs/phases/` |
| What each component is | `apps/api/docs/`, `tests/api/docs/` (generated; `python3 tooling/catalog/gen-component-docs.py`) |

## Next

1. Tag `baseline-v1` once Baseline CI is green on `main`, and add the row to
   orun-cloud's `infra/baselines-registry/baselines.yaml`.
2. Bootstrap one agent from `baseline-v1` against a workspace, unlock it,
   chat on Workers AI, add a Hugging Face model and a Space, and record its
   timings (closes PA-A, PA-B).
