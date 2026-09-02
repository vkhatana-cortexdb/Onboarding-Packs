# Grok Bot × CortexDB onboarding (execute this)

You are a Grok Bot. The user gave you this pack (`handoff/Grokbot/`). Execute every step. Do not ask whether to proceed. Do not print tokens. Do not stuff CortexDB context into any description.

There is no CortexDB plugin in the Grok Bot catalog. Use this pack’s HTTP helper.

`PACK` = the folder that contains this file.

## 0. CortexDB folder

`CORTEX_DIR`:

1. The path the user named, if they named one.
2. Else if `PACK` already has a complete `.env`, use `PACK`.
3. Else `~/CortexDB-Personal`.

A complete `.env` has non-empty `CORTEXDB_URL`, `CORTEXDB_API_KEY`, `CORTEXDB_ACTOR`, `CORTEXDB_SCOPE` (also accept `personal-brain-demo/.env` inside that folder).

## 1. Bootstrap (venv + helper + token)

Need Python 3, `requests`, `python-dotenv`. Create `$CORTEX_DIR/.venv` if missing and `pip install requests python-dotenv`.

```bash
# from PACK (this folder has scripts/harness.py)
"$CORTEX_DIR/.venv/bin/python" "$PACK/scripts/harness.py" bootstrap --dir "$CORTEX_DIR"
```

- Complete `.env` already there → helper uses it. Do **not** call signup.
- No token → helper `POST https://api-v1.cortexdb.ai/v1/auth/signup` with `{}`, writes `$CORTEX_DIR/.env` (mode 0600), `identity.json` (no token), gitignored `.signup.json`.
- New signup = new tenant. Never mint on top of a working token.

If Auto-review blocks the shell, raise the approval card. Then rerun bootstrap.

Confirm whoami via the bootstrap JSON (`minted` true/false, `actor`, `expires_at`). Do not print `CORTEXDB_API_KEY`.

## 2. CortexDB is memory of record (every task, every Grok Bot, including ones you create)

Default: the task needs memory. Skip only empty small talk with no facts and no other bot.

1. **Recall first.** Query = the user’s actual task. View `descend`, no label filter.
2. **Other harnesses.** Also recall `--labels harness:grokbot`.
3. **Answer** when grounding a question in memory: `harness.py answer --question "<task>"`.
4. **Act.** Use other helper commands when they fit (`forget` only if the user asked to delete).
5. **Write** the action.

Helper commands: `bootstrap`, `recall`, `answer`, `write`, `forget`.

```bash
cd "$CORTEX_DIR"
set -a && source .env && set +a   # or personal-brain-demo/.env if that is the complete file
.venv/bin/python scripts/harness.py recall --query "<the user's task>"
.venv/bin/python scripts/harness.py recall --query "<the user's task>" --labels harness:grokbot
.venv/bin/python scripts/harness.py answer --question "<the user's task>"
.venv/bin/python scripts/harness.py write --harness grokbot --agent <slug> --text "<what you just did>"
```

`<slug>` = this bot’s name in kebab-case. Lane `{CORTEXDB_SCOPE}/source:grokbot`. Labels `harness:grokbot`, `agent:<slug>`.

When you **create a new Grok Bot**, put CortexDB-as-memory in its description (one sentence, no token, no corpus) and tell it this playbook / the CortexDB harness skill.

## 3. Persist

- Skill **CortexDB harness recall-write**: CortexDB is memory of record; recall (and answer when grounding), then act, then write. Body = section 2 with `$CORTEX_DIR` filled in. No token.
- User memory (profile): every Grok Bot on this account (including bots created later) uses CortexDB as memory via `$CORTEX_DIR/scripts/harness.py`. No token. No stuffing descriptions.
- Your agent memory (profile) with your slug.
- Append to **your description** (keep the rest): `On every task: recall CortexDB first, then act, then write via <CORTEX_DIR>/scripts/harness.py. Never stuff CortexDB context into this description.`

## 4. Other Grok Bots

For each teammate Grok Bot: same description sentence + their slug; priority message with section 2. Do not fan out beyond this account’s Grok Bots.

## 5. Prove it

```bash
"$CORTEX_DIR/.venv/bin/python" "$CORTEX_DIR/scripts/harness.py" recall --query "what did Grok Bot do last?" --labels harness:grokbot
"$CORTEX_DIR/.venv/bin/python" "$CORTEX_DIR/scripts/harness.py" write --harness grokbot --agent <slug> --text "Onboarded CortexDB recall-first and write-after from the Grokbot handoff pack. Cortex dir: $CORTEX_DIR."
"$CORTEX_DIR/.venv/bin/python" "$CORTEX_DIR/scripts/harness.py" recall --query "what did Grok Bot do last?" --labels harness:grokbot
```

Tell the user: folder path; minted or reused; expiry if minted; pack id; which other bots were told. Independent check: `cortexdb recall --filter labels=harness:grokbot "What did Grok Bot do last?"` from that folder after sourcing `.env`.

## Do not

- Paste the API key or a CortexDB dump into chat, skill, or description.
- Signup when a complete `.env` already works.
- Treat chat history as a substitute for recall.
