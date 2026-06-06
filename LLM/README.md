# NMSDK runtime LLM data

Created automatically by NeuroModeler when `RDK_USE_LLM=ON`:

| Path | Purpose |
|------|---------|
| `audit/` | Append-only audit log (`audit.jsonl`) |
| `sessions/` | Persisted conversation state (`<session_id>.json`) |
| `index/` | Optional dev cache for doc/source search (gitignored; see `index/README.md`) |

Repository keeps placeholder dirs and docs only. User/runtime data stays local (gitignored).
Prebuilt search index for builds lives under `Bin/LLM/index/` (from target `llm-index-pack`).

Configure the assistant: **AI Assistant → Settings** (provider URL/model) or env `NMSDK_LLM_OLLAMA_BASE_URL`, `NMSDK_LLM_OLLAMA_MODEL`.
