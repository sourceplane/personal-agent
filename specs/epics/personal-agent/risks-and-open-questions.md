# personal-agent — risks and open questions

| ID | Risk | State | Notes |
|---|---|---|---|
| PA-A | `baseline-v1` is not yet proven live: the repository created and linked, the deploy token minted, a real deploy creating the Durable Object from its migration, the keys pushed by `secrets-live`, the smoke and the probes | OPEN | Proven offline in Baseline CI: the offline bootstrap with the blueprint's own hooks, the stage lane's own steps in a staged job tree, the Worker served as born and unlocked |
| PA-B | No real model answer: Workers AI, the router and Spaces are stood in for | OPEN | The e2e's stand-ins (`testing/lib/fake-workers-ai.js`, `fake-hf.py`) check the token, the payloads and the call order; whether `kimi-k2.6` and `llama-3.3-70b` call `remember` reliably on the real binding is unmeasured |
| PA-C | Hugging Face providers differ on tools | WATCH | A `400`/`422` refusal is retried without tools; a provider that accepts tools and ignores them, or fails another way, is not handled |
| PA-D | Spaces differ: other inputs than the message, an older Gradio, a long cold start | WATCH | Only Gradio 5 and a one-input endpoint are supported; 90 s timeout |
| PA-E | No streaming | WATCH | A long answer arrives whole; `streamText` once the page renders a stream |
| PA-F | Workers AI is billed in neurons to the Cloudflare account | WATCH | 10,000 a day free; a busy owner exceeds it |
| PA-G | `workers-ai-provider` is deprecated (its successor is `agents/models/ai-sdk`); 4.0.1 is its AI SDK 7 release | WATCH | The same package ai-chatbot and ai-slackbot run |
| PA-H | One shared access key per environment | ACCEPTED | Anyone holding it is the owner; rotate by storing a new one and redeploying |
| PA-I | The Durable Object's `v1` migration is history | ACCEPTED | Never edit it; a class change is a new tag after it |
| PA-J | Memory search is a word match | ACCEPTED | Semantic search is Vectorize and an embedding per turn — later, if needed |
| PA-K | A deploy pushes the keys that exist and deletes none | ACCEPTED | `wrangler secret delete` removes one (README) |
