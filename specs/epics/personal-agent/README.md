# personal-agent — a personal AI agent with Hugging Face models on Cloudflare Workers

**An owner wants one agent of their own that answers with whatever model
suits the moment — Workers AI with no key, a model Hugging Face's Inference
Providers serve (the ones HuggingChat runs), or their own Gradio Space — and
remembers what they tell it. So it is one Hono app on one plain Cloudflare
Worker: its page, its API behind one access key, a SQLite-backed Durable
Object for memory, deployed by Orun to stage and prod on every merge — and
the baseline that makes a copy of it somebody else's agent in one landing.**

| | |
|---|---|
| Status | 🟡 Built and proven offline in Baseline CI; `baseline-v1` not yet tagged; not yet live (risks PA-A, PA-B) |
| Upstream | none — original code. The baseline machinery is [ai-slackbot](https://github.com/sourceplane/ai-slackbot)'s |
| Reference | ai-slackbot (the plain Worker, its keyless Workers AI default and optional keys, the factory) and hono-api (the frame) |
| Key | `PA` |

## Read in this order

1. [design.md](design.md) — what the agent is, the models, Spaces, memory,
   the owner's door, the repository and the build, and the alternatives
   rejected.
2. [implementation-plan.md](implementation-plan.md) — the milestones and
   what each one lands.
3. [risks-and-open-questions.md](risks-and-open-questions.md) — what is not
   proven, and what was accepted.
4. [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md) — what shipped, and
   every choice made along the way.

## Milestones

| Milestone | What it lands | Task |
|---|---|---|
| PA0 — the spec | the repository, its intent, CI, tooling and spec index; this doc set | PA-1 |
| PA1 — the agent on Workers | the agent in `apps/api` as one plain Worker, its Durable Object, its tests, the README | PA-2 |
| PA2 — a baseline | the console card, the build document, the context pack and the baseline's tests | PA-3 |
