# Onboarding-Packs

Four ways people (and agents) get onto CortexDB. Tracks **1–3** live in this repo. Track **4** (Unified Brain product) is a separate repository.

## Use cases

| # | Use case | Folder / link | Audience | When to use | Hand to |
|---|---|---|---|---|---|
| 1 | **Self-host** a local CortexDB trial | [`01-self-host/`](01-self-host/) | Backend / ops, or an agent with Docker | You want a containerized instance on your machine (Ollama embeddings + optional OpenAI LLM) | Human *or* agent (`CORTEXDB_SETUP_GUIDE.md`) |
| 2 | **Wire CortexDB into an app/repo** | [`02-app-in-repo/`](02-app-in-repo/) | Backend / product engineer + coding agent | Dual-write memory into an existing or new app; keep Postgres/Supabase | Prefer **agent** (`APP-ONBOARDING.md`) |
| 3 | **Attach chat / IDE / Grok** to an existing brain | [`03-harness-attach/`](03-harness-attach/) | Vibe coder / agent operator | Claude Code, Cursor, or Grok Bot should recall/write against a working tenant | Prefer **agent** (per-harness `*-ONBOARDING.md`) |
| 4 | **Unified Brain** product | [Unified-Brain-MVP](https://github.com/vipul-khatana/Unified-Brain-MVP) *(separate)* | Product / personal brain users | Full Unified Brain app experience — **not** folded into this pack | That repo’s own onboarding |

## Honesty (claims)

When describing CortexDB in these packs or downstream copy:

- Integrations: **47** (not 53).
- Do **not** cite LongMemEval **93.8%**.
- Do **not** cite **~742ms** as a latency claim.
- **Raft** is experimental.
- CortexDB is **not** “always-on” without operational setup — say what you actually run.

## Layout

```
Onboarding-Packs/
  README.md                 ← you are here
  01-self-host/             ← Docker trial + cortex.example.env
  02-app-in-repo/           ← AGENTS + CONVENTIONS + docs + APP-ONBOARDING.md
  03-harness-attach/        ← Grokbot / ClaudeCode / Cursor packs
```

Unified Brain stays at https://github.com/vipul-khatana/Unified-Brain-MVP — do not copy it here.

## Security

- Never commit filled `.env` / `cortex.env` files.
- `cortex.example.env` and `env.example` files must stay placeholders only.
- Agents must not print API keys or paste them into chat.
