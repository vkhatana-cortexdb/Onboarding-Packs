# App × CortexDB onboarding (execute this)

You are a coding agent. The user gave you this pack (`02-app-in-repo/`). Execute every step to drop CortexDB into an existing or new app repo. Do not ask whether to proceed. Do not print tokens. Do not invent API signatures.

`PACK` = the folder that contains this file (`02-app-in-repo/`).

Goal: CortexDB runs **alongside** the app’s existing database (dual-write). Do not replace Postgres/Supabase/etc.

## 0. Inputs

Resolve before writing files:

| Input | Meaning |
|---|---|
| `PROJECT_DIR` | Absolute path to the target app repo (required). |
| `SHARE_BRAIN` | `true` if the user already has a working CortexDB `.env` (Personal-Brain / shared tenant). Prefer shared brain. |
| `CORTEX_ENV_FILE` | Path to complete `.env` with `CORTEXDB_URL`, `CORTEXDB_API_KEY`, `CORTEXDB_ACTOR`, `CORTEXDB_SCOPE` when `SHARE_BRAIN=true`. |
| `STACK` | Language/stack hints (e.g. Node/Next, Python/FastAPI). Used only to choose SDK vs HTTP examples — still look up live docs. |
| `APP_SLUG` | Short app id for scopes (`app:<slug>/user:<id>`). Ask once if unclear. |

If `PROJECT_DIR` is missing, stop and ask for it. Never mint a new tenant over a working shared token.

## 1. Copy agent docs into the repo

From `PACK` into `PROJECT_DIR`:

```bash
cp "$PACK/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
mkdir -p "$PROJECT_DIR/.cortexdb"
cp "$PACK/CONVENTIONS.md" "$PROJECT_DIR/.cortexdb/CONVENTIONS.md"
mkdir -p "$PROJECT_DIR/CortexDB_docs"
cp -R "$PACK/docs/." "$PROJECT_DIR/CortexDB_docs/"
```

- Keep existing `AGENTS.md` content if present: merge CortexDB hard rules; do not wipe unrelated project rules.
- `04_FULL_REFERENCE.md` in this pack may be a **pointer** to the Documentation tree. If so, either leave the pointer or copy the real file from the path named inside it when offline agents need the full blob.
- Confirm `CortexDB_docs/00_INDEX.md` exists. Agents route from the index — never dump the full reference linearly.

## 2. Env (shared brain preferred)

Required client vars (never commit filled values):

- `CORTEXDB_URL`
- `CORTEXDB_API_KEY`
- `CORTEXDB_ACTOR`
- `CORTEXDB_SCOPE`

### Shared brain (`SHARE_BRAIN=true`)

1. Source `CORTEX_ENV_FILE` (or Personal-Brain `personal-brain-demo/.env`).
2. Copy **names only** into the app’s local env template (`.env.example` / `.env.local.example`) with placeholders.
3. Put real values only in gitignored `.env` / `.env.local` (mode 0600).
4. Run `cortexdb auth whoami` (or equivalent HTTP) and report caller/expiry only.
5. **Do not** call signup. **Do not** mint over a working token.

### New tenant (`SHARE_BRAIN=false`)

Only if the user explicitly accepted a new brain: create credentials via documented signup/init, write gitignored `.env` mode 0600, tell the user this is a **new** tenant. Never print the key.

Add to `.gitignore` if missing: `.env`, `.env.local`, `cortex.env`, `**/.env`.

## 3. Dual-write SDK or HTTP (do not replace the existing DB)

1. Open `CortexDB_docs/00_INDEX.md` and route to the right doc for write/recall/scopes.
2. Add CortexDB **alongside** the existing DB:
   - Keep primary persistence where it is today.
   - On meaningful user/agent actions, also write an experience/memory to CortexDB with a correct scope (`app:<APP_SLUG>/user:<existing_user_id>`).
   - On reads that need long-term memory, recall from CortexDB (view from docs — do not guess).
3. Prefer the official SDK for `STACK` when documented; otherwise HTTP against the live docs / `00_INDEX` routing.
4. **Hard rule:** never invent endpoints, field names, or views from training memory. Legacy paths like `/v1/remember` are wrong.

If docs MCP is available (`cortexdb_docs_search`), use it first; else live https://cortexdb.ai/llms.txt / docs; else offline `CortexDB_docs/`.

## 4. Optional: wire coding-agent MCP

If the user wants Claude Code / Cursor / Grok on this same brain:

- Point them (or execute) **`../03-harness-attach/`**:
  - Claude Code → `ClaudeCode/CLAUDE-CODE-ONBOARDING.md` (user-global MCP is `~/.claude.json` `mcpServers`)
  - Cursor → `Cursor/CURSOR-ONBOARDING.md`
  - Grok Bot → `Grokbot/GROKBOT-ONBOARDING.md`
- Reuse the same `CORTEXDB_*` identity. Do not mint a second tenant.

Skip this section if they only want app dual-write.

## 5. Smoke

After wiring (no tokens in output):

1. **whoami** — auth matches `CORTEXDB_ACTOR`.
2. **experience write** — one short test memory under `app:<APP_SLUG>/...` (or the scope from CONVENTIONS).
3. **recall** — same query retrieves that write.

If any step fails, stop and report the actual error. Do not claim success.

## 6. Hard rules

1. Never invent CortexDB API from memory — use `00_INDEX` routing → live docs → ask.
2. Never put tokens/API keys in git, chat, PR descriptions, or AGENTS.md.
3. Never replace the existing app database; CortexDB is additive dual-write.
4. Never use a flat scope; always `type:id` paths.
5. Never mint over a working shared-brain token.
6. Prefer honesty: integrations are **47** (not 53); no LongMemEval 93.8%; no ~742ms latency claims; Raft is experimental; CortexDB is not always-on without ops.

## 7. Report

Tell the user:

- `PROJECT_DIR`
- Files copied (`AGENTS.md`, `.cortexdb/CONVENTIONS.md`, `CortexDB_docs/`)
- Shared vs minted identity (no key)
- Dual-write touchpoints added (files/modules)
- Whether MCP harness attach was done
- Smoke: whoami / write / recall pass or fail
