# personal-agent — decisions

The choices that shape this repository, one line each, with where the full
reasoning lives. Superseded decisions stay listed, marked, so the history
reads in order.

| # | Decision | Why | Source |
|---|---|---|---|
| 1 | A plain Worker (`cloudflare-worker-turbo`), one Hono app, the page served by the Worker itself (`src/ui.ts`, no asset, no external script) | One Worker is the whole product; a self-contained page means the browser talks to nothing else, and no Static Assets or wiring to deploy | `specs/epics/personal-agent/design.md` §2 |
| 2 | Workers AI by default (`@cf/moonshotai/kimi-k2.6`, with `@cf/meta/llama-3.3-70b-instruct-fp8-fast`), through the `AI` binding | No key nobody brokers: a fresh agent answers with nothing but its access key; models that call tools (ai-chatbot's and ai-slackbot's default) | design.md §3 |
| 3 | Hugging Face Inference Providers through the router's OpenAI-compatible API (`router.huggingface.co/v1`, `@ai-sdk/openai-compatible` 3.0.80) with the owner's `HF_TOKEN` | One API reaches every provider the Hub routes to — the models HuggingChat runs included — and the AI SDK's tool loop works over it unchanged; the `:policy` suffix is the router's own | design.md §3 |
| 4 | Gradio Spaces through Gradio 5's HTTP API (`/gradio_api/call/<endpoint>`, then its event stream); the URL derived from the id (`<owner>-<name>.hf.space`), never given | A user-supplied URL would send `HF_TOKEN` wherever it pointed; a derived one only ever reaches Hugging Face. `HF_SPACES_URL` is a test-only override | design.md §4 |
| 5 | Memory in one SQLite-backed Durable Object per environment (`AgentMemory`, named `owner`); the conversation in the browser | Facts and added models outlive a chat and need no Terraform (SQLite DOs are on Workers Free); not storing conversations means the Worker keeps nothing of what was said | design.md §5 |
| 6 | Every model told the 30 most recent memories; `remember`, `recall`, `forget`, `currentTime` only for a model marked as calling tools | A model without tools still knows its owner; only a model that can call `remember` is asked to | design.md §5 |
| 7 | One access key (`AGENT_ACCESS_KEY`) as a bearer token on every `/api` route: `503` before it is stored, `401` for a wrong one, SHA-256 digests compared in constant time | A public workers.dev URL would otherwise spend the owner's models on anyone; born locked and saying so, never a 500 | design.md §6 |
| 8 | The agent's keys (`AGENT_ACCESS_KEY`, `HF_TOKEN`, `HF_MODELS`) are optional Orun secrets pushed as Worker secrets after each deploy (`runtimeSecrets`) | A product deploys before its owner has chosen a key; no key reaches a build. Hugging Face is not brokered: its integration is connect-only, so the owner stores the same token | design.md §6 |
| 9 | A Hugging Face model refused with tools (`400` or `422`) is asked once more without them | Tool support varies by provider; the owner should not need to know which, and other errors (a bad token) are not retried | design.md §3 |
| 10 | `generateText`, not streaming; a Space call gives up after 90 s | One JSON answer is simpler to test end to end and to fail cleanly (`502` naming the model); streaming is a later change | design.md §3 |
| 11 | `GET /health` reports access, Hugging Face, model counts and tools by name; the smoke reads it and checks `/api/chat` refuses a request without the key (`401`/`503`) | The deploy proves the environment and that the door is closed, without anyone's key | operations.md |
| 12 | One name seam (`apps/api/src/identity.ts`, `API_NAME`) — the page title, the system prompt and `/health` | The rename has one seam | IMPLEMENTATION-STATUS |
| 13 | The factory (blueprints, rebrand, bootstrap tooling, testing tiers, CI lanes) is ai-slackbot's, renamed | It is proven on the platform's bootstrap; only the product changes | IMPLEMENTATION-STATUS |
