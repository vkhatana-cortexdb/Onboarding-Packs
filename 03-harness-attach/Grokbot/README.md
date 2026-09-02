# For you (the human) — Grok Bot pack

Give your Grok Bot **this whole folder**. That is the complete pack.

```
Personal-Brain/handoff/Grokbot/
```

Optional one-liner to the bot:

> Read `GROKBOT-ONBOARDING.md` in this folder and run it. CortexDB folder: `<path or omit>`.

## What you do

1. Send Grok Bot this `Grokbot/` folder (or tell it the path on disk).
2. Optionally name an existing CortexDB folder. If you skip this, the bot creates `~/CortexDB-Personal`.
3. If Auto-review shows an approval card for a shell command, tap allow. That is the only tap that may be required.

You do **not** create `.env` by hand unless you already have a CortexDB token you want to keep.

## What the bot does

- Folder already has a working `.env` (`CORTEXDB_URL`, `CORTEXDB_API_KEY`, `CORTEXDB_ACTOR`, `CORTEXDB_SCOPE`) → use it. No new tenant.
- Folder exists but no token → mint a 7-day anonymous CortexDB tenant (`POST /v1/auth/signup`) into that folder’s `.env`.
- No folder named → create `~/CortexDB-Personal` and mint.
- Makes CortexDB memory of record on every Grok Bot (recall/answer first, write after), including bots they create later.
- Proves it with a recall → write → recall loop.

## Do not send

`.env`, `.signup.json`, tokens, or `secrets/`. Those stay on the machine.

## After it works

Independent check (from the CortexDB folder):

```bash
set -a && source .env && set +a
cortexdb recall --filter labels=harness:grokbot "What did Grok Bot do last?"
```

Anonymous tokens last 7 days. A new signup is a **new** tenant (old data is not visible). A persistent token on the same actor does not need re-ingest.

Sibling pack for Claude Code: `../ClaudeCode/`.
