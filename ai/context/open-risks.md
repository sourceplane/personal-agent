# personal-agent — open risks

What is not yet proven or not yet decided. The full write-up of every risk,
including the accepted and resolved ones, is
`specs/epics/personal-agent/risks-and-open-questions.md`; this page lists only what
is still live, so it should be short.

| ID | Risk | State | What closes it |
|---|---|---|---|
| PA-A | No live bootstrap yet: the repository created and linked, the deploy token minted, a real `wrangler deploy` creating the Durable Object from its migration, the keys pushed, the smoke and the probes against workers.dev | OPEN | The first bootstrap from `baseline-v1` |
| PA-B | No real model answer: the offline proof stands in for Workers AI, the router and a Space; whether `kimi-k2.6` and `llama-3.3-70b` call `remember`/`recall` reliably on the real binding is unmeasured | OPEN | A live bootstrap, unlocked, with a real chat and a fact remembered |
| PA-C | Hugging Face providers differ on tools: the retry covers a `400`/`422` refusal, but a provider that accepts tools and ignores them, or fails differently, is unhandled | WATCH | Live use across a few router models; a per-model note if it bites |
| PA-D | Spaces differ: the agent assumes a Gradio 5 endpoint taking the message alone (`gr.ChatInterface`'s `chat`); a Space with other inputs, an older Gradio, or a long cold start fails or times out at 90 s | WATCH | Real Spaces; an input template per Space if needed |
| PA-E | No streaming: a long multi-step answer arrives whole, as slow as its slowest step | WATCH | `streamText` once the page can render a stream |
| PA-F | Workers AI is billed in neurons to the Cloudflare account (10,000 a day free); a busy owner exceeds it | WATCH | The account's usage; a cheaper default model |
| PA-G | `workers-ai-provider` is deprecated in favour of `agents/models/ai-sdk`; 4.0.1 is its last AI SDK 7 release | WATCH | A move when the replacement is proven on the binding without a gateway |

Accepted, and worth knowing before you change them: PA-H (one shared access
key per environment — anyone holding it is the owner; rotate by storing a
new one), PA-I (the Durable Object's `v1` migration must never be edited: a
class change is a new tag), PA-J (memory search is a word match, not
semantic), PA-K (a deploy pushes keys and deletes none).
