# CortexDB — Cloud free trial / hosted keys

Follow as a **human**, or hand to a coding agent. Do not print tokens. Do not commit `.env`.

`PACK` = this folder (`00-cloud-trial/`).

Official cold-start: https://cortexdb.ai/docs/sdks/rest-api

---

## 0. Pick a mode

| Mode | When | What you do |
|---|---|---|
| **A — Free trial signup** | You have nothing yet | Mint anonymous 7-day token (section 1A) |
| **B — Existing cloud keys** | Dashboard / teammate / prior trial still valid | Paste into `.env` only (section 1B). **Never** call signup. |

If a working `.env` already exists in `PACK`, use it (mode B). Never mint over a working token.

---

## 1A. Free trial — mint keys

Needs `curl` and `jq`.

```bash
cd "$PACK"
cp env.example .env
chmod 600 .env

SIGNUP=$(curl -sfS -X POST https://api-v1.cortexdb.ai/v1/auth/signup \
  -H 'Content-Type: application/json' -d '{}')

# Show metadata only (no token)
echo "$SIGNUP" | jq '{user_id, scope, expires_at}'

# Write .env without printing the bearer
python3 -c "
import json, os, pathlib
s = json.loads('''$SIGNUP''')
p = pathlib.Path('.env')
p.write_text(
    'CORTEXDB_URL=https://api-v1.cortexdb.ai\n'
    f\"CORTEXDB_API_KEY={s['token']}\n\"
    f\"CORTEXDB_ACTOR={s['user_id']}\n\"
    f\"CORTEXDB_SCOPE={s['scope']}\n\"
    + (f\"# CORTEXDB_EXPIRES_AT={s.get('expires_at','')}\n\" if s.get('expires_at') else '')
    + '# SOURCE=free-tier-signup\n'
)
p.chmod(0o600)
print('wrote .env mode 0600')
print('actor:', s['user_id'])
print('scope:', s['scope'])
print('expires_at:', s.get('expires_at'))
"
```

Free-tier TTL is **7 days**. Re-signup mints a **new** empty tenant. Prefer durable dashboard keys for anything you want to keep.

---

## 1B. Existing cloud keys

```bash
cd "$PACK"
cp -n env.example .env
chmod 600 .env
```

Edit `.env`:

- `CORTEXDB_URL=https://api-v1.cortexdb.ai`
- `CORTEXDB_API_KEY=` Bearer / PASETO
- `CORTEXDB_ACTOR=` must match the token subject
- `CORTEXDB_SCOPE=` your default scope

Dashboard `cx_live_…` keys are for dashboard/MCP BFF flows. For this REST smoke test you need a **Bearer** token. Do not invent exchange endpoints.

---

## 2. whoami

```bash
set -a && source .env && set +a

curl -sfS https://api-v1.cortexdb.ai/v1/auth/whoami \
  -H "Authorization: Bearer $CORTEXDB_API_KEY" \
  -H "X-Cortex-Actor: $CORTEXDB_ACTOR"
```

If you see `actor_mismatch`, fix `CORTEXDB_ACTOR`. Do not print the bearer.

---

## 3. Smoke: write + answer

```bash
set -a && source .env && set +a
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
IDEM="cloud-trial-smoke-$(date +%s)"

curl -sfS -X POST "https://api-v1.cortexdb.ai/v1/experience" \
  -H "Authorization: Bearer $CORTEXDB_API_KEY" \
  -H "X-Cortex-Actor: $CORTEXDB_ACTOR" \
  -H 'Content-Type: application/json' \
  -d "{
    \"scope\": \"$CORTEXDB_SCOPE\",
    \"modality\": \"conversation\",
    \"content\": { \"kind\": \"message\", \"role\": \"user\",
                   \"text\": \"Onboarding smoke: Q3 revenue exceeded 2.4M, up 34% YoY\" },
    \"context\": { \"observed_at\": \"$NOW\" },
    \"idempotency_key\": \"$IDEM\"
  }"

curl -sfS -X POST "https://api-v1.cortexdb.ai/v1/answer" \
  -H "Authorization: Bearer $CORTEXDB_API_KEY" \
  -H "X-Cortex-Actor: $CORTEXDB_ACTOR" \
  -H 'Content-Type: application/json' \
  -d "{
    \"scope\": \"$CORTEXDB_SCOPE\",
    \"question\": \"What was Q3 revenue?\",
    \"view\": \"holistic\",
    \"diagnostics\": \"none\"
  }"
```

Success = whoami works and answer mentions the smoke write. You have a working cloud brain.

---

## 4. Next: build the app (same keys)

Skip `01-self-host` unless you want Docker.

### New app

> Build my app with CortexDB. Shared brain at `00-cloud-trial/.env`. Follow `02-app-in-repo/APP-ONBOARDING.md`. `SHARE_BRAIN=true`. Do not mint a new tenant. Do not print tokens.

### Existing repo

> Implement CortexDB on my current repo. `CORTEX_ENV_FILE` = absolute path to `00-cloud-trial/.env`. `SHARE_BRAIN=true`. Follow `APP-ONBOARDING.md`. Dual-write only.

Optional: same `.env` → `03-harness-attach/` for Claude / Cursor / Grok.

Standing rule once wired: recall → act → write. Look up APIs from docs; never invent `/v1/remember`.

---

## Honesty + security

- Integrations: **47**. No fake LongMemEval / latency claims. Raft experimental.
- Free trial ≠ permanent account. 7-day tokens expire; re-signup = new empty tenant.
- Never commit `.env`. Never paste `CORTEXDB_API_KEY` into chat, tickets, or email.
