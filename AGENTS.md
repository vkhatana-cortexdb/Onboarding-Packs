# AGENTS.md — how to use Onboarding-Packs

You are a coding agent. Read the human README for routing, then execute exactly one path. Do not invent API signatures. Do not print tokens. Do not mint a new tenant over a working shared brain.

`PACK_ROOT` = this repository root.

---

## Path 1 — Cloud / free trial (default brain)

Trigger: *free trial*, *cloud keys*, *hosted*, *api-v1*, *get me a brain*, *try CortexDB*.

1. Execute `$PACK_ROOT/00-cloud-trial/CLOUD-TRIAL.md`.
2. Prefer existing `.env` (mode B). Only signup (mode A) if no working credentials.
3. Confirm whoami + smoke write/answer. Report actor/scope/expiry only — never the bearer.
4. If they also asked to build an app, continue to Path 3/4 with `SHARE_BRAIN=true` and `CORTEX_ENV_FILE=$PACK_ROOT/00-cloud-trial/.env`.

---

## Path 2 — Docker self-host

`$PACK_ROOT/01-self-host/CORTEXDB_SETUP_GUIDE.md`. Only when they asked for local Docker.

---

## Path 3 — New app (“Build my app with CortexDB”)

1. Prefer Path 1 brain first (`00-cloud-trial/.env`).
2. Execute `$PACK_ROOT/02-app-in-repo/APP-ONBOARDING.md` with `SHARE_BRAIN=true` when `.env` exists.
3. Dual-write alongside any primary DB. Never invent `/v1/remember`.
4. Standing rule: recall → act → write.

---

## Path 4 — Existing repo (“Implement CortexDB on my current repo”)

1. `PROJECT_DIR` = their app root (required).
2. `SHARE_BRAIN=true` + `CORTEX_ENV_FILE` when cloud/self-host `.env` exists.
3. Execute `APP-ONBOARDING.md`. Merge AGENTS.md; do not wipe project rules.
4. Smoke whoami + write + recall. No secrets in output.

---

## Path 5 — Harness attach

`$PACK_ROOT/03-harness-attach/` — Claude Code uses **`~/.claude.json` → `mcpServers`**, not `~/.claude/mcp.json`.

---

## Honesty + security

- Integrations **47**. No 93.8% LongMemEval. No ~742ms claim. Raft experimental.
- Never commit filled env files. Never paste API keys into chat, commits, or issue bodies.
