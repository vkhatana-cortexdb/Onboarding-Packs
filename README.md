# CortexDB Onboarding Packs

Official onboarding docs for CortexDB. **One repo, four audiences.** Send this whole repo (or a folder deep-link). Do not fork into three repos — that goes stale.

---

## Pick your path (read this first)

| Priority | Who you are | What to say / do | Open |
|---|---|---|---|
| **1 — top** | **Human** learning CortexDB (coder in the playground) | Read and run the self-host trial yourself | [`01-self-host/`](01-self-host/) → start at `CORTEXDB_SETUP_GUIDE.md` |
| **2** | **Agentic developer** building a **new** app | Tell your agent: *“Build my app with CortexDB”* and point it at this pack | [`02-app-in-repo/APP-ONBOARDING.md`](02-app-in-repo/APP-ONBOARDING.md) (new app / no existing DB required to dual-write later) |
| **3** | **Agentic development** on an **existing** repo | Give the agent this folder and say: *“Implement CortexDB on my current repo”* | Same [`APP-ONBOARDING.md`](02-app-in-repo/APP-ONBOARDING.md) with `PROJECT_DIR` = your repo |
| **4** | Hook tools to a **personal / shared brain** | Attach Claude Code, Cursor, or Grok Bot to a working tenant | [`03-harness-attach/`](03-harness-attach/) |

Agents: also read [`AGENTS.md`](AGENTS.md) (how to execute each path).

---

## 1. Human — playground first

If you are a person who wants to **understand and implement** CortexDB (not hand everything to an agent):

1. Open **[`01-self-host/`](01-self-host/)**.
2. Follow **`CORTEXDB_SETUP_GUIDE.md`** top to bottom (Docker + Ollama embeddings + health check + a test write/recall).
3. Keep `cortex.example.env` next to the guide; copy it to `cortex.env` (gitignored) and fill keys locally.
4. Optional next: skim [`02-app-in-repo/docs/00_INDEX.md`](02-app-in-repo/docs/00_INDEX.md) to learn scopes, recall, and ingestion without wiring an app yet.

This path is the **default** for anyone we email a “start here” link.

---

## 2. Agentic developer — new app

You are building something new and want CortexDB in from day one.

**Human prompt to your coding agent:**

> Build my app with CortexDB. Use the onboarding pack at `02-app-in-repo/`. Follow `APP-ONBOARDING.md`. Dual-write memory; do not invent API paths. Do not print tokens.

**If you are the agent:** open [`AGENTS.md`](AGENTS.md) § Path 2, then execute [`02-app-in-repo/APP-ONBOARDING.md`](02-app-in-repo/APP-ONBOARDING.md).

---

## 3. Agentic development — cortexdbify an existing repo

You already have an app. You want CortexDB alongside the current database.

**Human prompt to your coding agent:**

> Implement CortexDB on my current repo. Pack = `02-app-in-repo/`. `PROJECT_DIR` = this repository. Follow `APP-ONBOARDING.md` end to end. Prefer a shared brain if I already have a working `.env`. Do not replace Postgres/Supabase. Do not mint a new tenant over a working token.

**If you are the agent:** open [`AGENTS.md`](AGENTS.md) § Path 3, then execute the same `APP-ONBOARDING.md` with `PROJECT_DIR` set.

---

## 4. Personal / shared brain — hook harnesses

You already have (or will have) a CortexDB tenant and want Claude Code / Cursor / Grok Bot to recall and write to it.

Open [`03-harness-attach/`](03-harness-attach/):

| Harness | Start |
|---|---|
| Claude Code | `ClaudeCode/CLAUDE-CODE-ONBOARDING.md` (user MCP lives in `~/.claude.json` → `mcpServers`) |
| Cursor | `Cursor/CURSOR-ONBOARDING.md` |
| Grok Bot | `Grokbot/GROKBOT-ONBOARDING.md` |

Product-shaped “Unified Brain” (one-click personal brain) is a **separate** repo: [Unified-Brain-MVP](https://github.com/vipul-khatana/Unified-Brain-MVP). Do not copy it into this pack.

---

## Folder map (stable paths)

```
Onboarding-Packs/
  README.md              ← humans start here (this file)
  AGENTS.md              ← agents start here
  01-self-host/          ← Path 1 (human playground / local trial)
  02-app-in-repo/        ← Paths 2 & 3 (new app or existing repo)
  03-harness-attach/     ← Path 4 (wire IDE/chat to a brain)
```

One GitHub repo is intentional: one source of truth, deep-link the folder that matches the recipient. Splitting into three repos duplicates honesty rules and drifts.

---

## Honesty (claims)

- Integrations: **47** (not 53).
- Do **not** cite LongMemEval **93.8%**.
- Do **not** cite **~742ms** as a latency claim.
- **Raft** is experimental / not marketed as shipped.
- CortexDB is **not** “always-on” without setup — say what you actually run.

## Security

- Never commit filled `.env` / `cortex.env`.
- Example env files stay placeholders only.
- Agents must not print API keys or paste them into chat.
