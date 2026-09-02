> **Pack track:** `00-cloud-trial` — get a hosted CortexDB brain (free trial or your cloud keys), prove write/recall, then build an app with it.

# Cloud / free-trial brain

**Default human playground** if you do not want Docker.

Get credentials for hosted CortexDB at `https://api-v1.cortexdb.ai`, smoke-test them yourself, then point `02-app-in-repo/` (or your agent) at the same `.env` to build the app.

| File | What it is |
|---|---|
| **`CLOUD-TRIAL.md`** | Step-by-step. Start here. |
| **`env.example`** | Env template. Copy to `.env` (gitignored). |
| **`README.md`** | This file. |

## Two ways in

1. **Free trial (anonymous signup)** — `POST /v1/auth/signup` with `{}`. No email, no card. **7-day** token.
2. **Your cloud keys** — paste existing `CORTEXDB_*` into `.env`. Do **not** mint over a working tenant.

Self-host Docker: [`../01-self-host/`](../01-self-host/).

## After keys work

1. Follow `CLOUD-TRIAL.md` smoke test.
2. Build / cortexdbify: [`../02-app-in-repo/APP-ONBOARDING.md`](../02-app-in-repo/APP-ONBOARDING.md) with `SHARE_BRAIN=true` and `CORTEX_ENV_FILE` = this folder’s `.env`.
3. Optional harnesses: [`../03-harness-attach/`](../03-harness-attach/).
