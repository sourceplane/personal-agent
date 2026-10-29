// A DETERMINISTIC STAND-IN FOR WORKERS AI, for testing/e2e.test.sh only.
//
// The agent's built-in models are Workers AI through the Worker's `AI`
// binding (apps/api/src/models.ts, via workers-ai-provider): `env.AI.run(model,
// inputs)`. Workers AI has no local mode, so under `wrangler dev` the e2e binds
// `AI` to THIS Worker instead — a service binding to its `FakeAI` entrypoint,
// an RPC method with the binding's own shape — and the agent's code (the real
// AI SDK, the real provider, the real Durable Object) cannot tell the
// difference.
//
// It answers in the OpenAI-compatible chat shape the provider reads:
//   - the last message is a tool result     → text that quotes it
//   - the user wrote  remember: <fact>       → a `remember` tool call with it
//   - anything else                          → "Echo: <the user's text>"
// so the e2e can drive the agent loop through its memory tool, and a plain
// answer, with no network. The system prompt's memories are logged too, so
// the e2e can see a fact reach a later conversation. Each call
// is logged as one `fake-workers-ai {…}` line the e2e reads back.
import { WorkerEntrypoint } from "cloudflare:workers";

const text = (content) =>
  typeof content === "string"
    ? content
    : Array.isArray(content)
      ? content.map((p) => (typeof p === "string" ? p : (p?.text ?? ""))).join("")
      : "";

export class FakeAI extends WorkerEntrypoint {
  async run(model, inputs) {
    const messages = Array.isArray(inputs?.messages) ? inputs.messages : [];
    const tools = Array.isArray(inputs?.tools) ? inputs.tools.map((t) => t?.function?.name ?? t?.name).filter(Boolean) : [];
    const last = messages[messages.length - 1] ?? {};
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    let choice;
    if (last.role === "tool") {
      choice = { message: { role: "assistant", content: `Tool said: ${text(last.content)}` }, finish_reason: "stop" };
    } else {
      const ask = /^remember: (.+)$/.exec(text(lastUser?.content));
      if (ask && tools.includes("remember")) {
        choice = {
          message: {
            role: "assistant",
            content: "",
            tool_calls: [{ id: `call_${messages.length}`, type: "function", function: { name: "remember", arguments: JSON.stringify({ fact: ask[1] }) } }],
          },
          finish_reason: "tool_calls",
        };
      } else {
        choice = { message: { role: "assistant", content: `Echo: ${text(lastUser?.content)}` }, finish_reason: "stop" };
      }
    }
    const system = text(messages.find((m) => m.role === "system")?.content);
    console.log(`fake-workers-ai ${JSON.stringify({ model, tools, roles: messages.map((m) => m.role), remembers: system.split("\n").filter((l) => l.startsWith("- [")), reply: choice.finish_reason })}`);
    return { choices: [choice], usage: { prompt_tokens: 7, completion_tokens: 5, total_tokens: 12 } };
  }
}

export default {
  fetch() {
    return new Response("fake-workers-ai: reached only through the agent's AI service binding\n");
  },
};
