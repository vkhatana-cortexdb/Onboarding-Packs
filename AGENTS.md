# AGENTS.md — how to use Onboarding-Packs

You are a coding agent. This repo is the CortexDB onboarding pack. **Read the human README first** for audience routing, then execute exactly one path below. Do not invent CortexDB API signatures. Do not print tokens. Do not mint a new tenant over a working shared brain.

`PACK_ROOT` = this repository root (the folder that contains this file).

---

## Path 1 — Human playground (support only)

If the user is learning themselves, **do not take over**. Point them to:

- `$PACK_ROOT/01-self-host/CORTEXDB_SETUP_GUIDE.md`
- `$PACK_ROOT/01-self-host/cortex.example.env`

Help only when asked (Docker errors, health checks). Prefer them completing §1–§6 of the setup guide by hand.

---

## Path 2 — New app (“Build my app with CortexDB”)

Trigger phrases: *build my app with CortexDB*, *greenfield*, *new project with memory*.

1. Confirm `PROJECT_DIR` (where the new app will live or already was scaffolded).
2. Execute `$PACK_ROOT/02-app-in-repo/APP-ONBOARDING.md` end to end.
3. Dual-write: CortexDB **alongside** any primary DB you create; never CortexDB-only unless the user said so.
4. Copy `AGENTS.md`, `.cortexdb/CONVENTIONS.md`, and `docs/` into the app as that file instructs.
5. Prefer shared brain if the user already has `CORTEXDB_*` credentials; otherwise create a new tenant only with explicit OK.
6. After wiring, offer Path 4 if they want Claude/Cursor/Grok on the same brain.

Standing rule once live: **recall → act → write**. Look up calls in `CortexDB_docs/00_INDEX.md` (or docs MCP); never from training memory.

---

## Path 3 — Existing repo (“Implement CortexDB on my current repo”)

Trigger phrases: *implement CortexDB on my current repo*, *cortexdbify*, *add memory to this codebase*.

1. Set `PROJECT_DIR` = the user’s existing app root (required).
2. Execute `$PACK_ROOT/02-app-in-repo/APP-ONBOARDING.md` end to end.
3. **Do not** replace Postgres/Supabase/etc. Dual-write only.
4. Merge into existing `AGENTS.md` if present; do not wipe project rules.
5. Prefer `SHARE_BRAIN=true` when a working `.env` exists.
6. Smoke: whoami + one write + one recall; report success without printing secrets.

Same standing rule: recall → act → write; look up APIs.

---

## Path 4 — Personal / shared brain (harness attach)

Trigger phrases: *hook Claude/Cursor/Grok to my brain*, *attach harness*, *Personal Brain*.

1. Confirm a working tenant (`CORTEXDB_URL`, `CORTEXDB_API_KEY`, actor, scope).
2. Open `$PACK_ROOT/03-harness-attach/README.md` and run the matching harness pack:
   - Claude Code → `ClaudeCode/CLAUDE-CODE-ONBOARDING.md`  
     User-global MCP is **`~/.claude.json` → `mcpServers`** (not `~/.claude/mcp.json`).
   - Cursor → `Cursor/CURSOR-ONBOARDING.md`
   - Grok Bot → `Grokbot/GROKBOT-ONBOARDING.md`
3. Verify with a health/whoami style check and a tiny recall/write. Never print the key.
4. Unified Brain product UX is **out of scope** here — see https://github.com/vipul-khatana/Unified-Brain-MVP

---

## Honesty + security (all paths)

- Integrations count: **47**. No 93.8% LongMemEval. No ~742ms latency claim. Raft = experimental. Not “always-on” by magic.
- Never commit filled env files. Never paste API keys into chat, commits, or issue bodies.
