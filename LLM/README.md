# NMSDK runtime LLM data

Created automatically by NeuroModeler when `RDK_USE_LLM=ON`:

| Path | Purpose |
|------|---------|
| `audit/` | Append-only audit log (`audit.jsonl`) |
| `sessions/` | Persisted conversation state (`<session_id>.json`) |

Repository keeps empty directories only. User data stays local (gitignored).

Configure the assistant: **AI Assistant → Settings** (provider URL/model) or env `NMSDK_LLM_OLLAMA_BASE_URL`, `NMSDK_LLM_OLLAMA_MODEL`.
