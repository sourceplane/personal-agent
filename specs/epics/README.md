# Epics

Orun-style work programs. Each epic is a folder carrying `epic.yaml` (the
declaration the platform reads: slug, key prefix, milestones with exit
criteria and task keys) beside its doc set. The pull request that adds the
folder is the adoption; the merge creates the epic in the workspace.

| Epic | Cluster | Status | What it is |
|------|---------|--------|------------|
| [`personal-agent/`](./personal-agent/) | **PA** | 🟡 Built and proven offline; `baseline-v1` not yet tagged | A personal AI agent — a chat page answering with Workers AI or the owner's Hugging Face models and Spaces, its memory in a Durable Object — as one Cloudflare Worker, and an Orun baseline that instantiates it in one landing (PA2) |

As-built ≠ intent: what shipped lives in each epic's `IMPLEMENTATION-STATUS.md`.
