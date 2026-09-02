# CortexDB conventions for this project

Read after `AGENTS.md`. Rules 1 and 2 there apply to everything below: look up
exact API syntax rather than reproducing it from memory, and look it up the
moment you are unsure rather than after a failed attempt.

Offline documentation lives in `CortexDB_docs/`. Start at
`CortexDB_docs/00_INDEX.md`, which routes by task. The three you will reach for
most here are `01_MEMORY_SCOPES_AND_RECALL.md` (scopes and views),
`02_DATA_INGESTION_AND_PROCESSING.md` (files and non-text content), and
`04_FULL_REFERENCE.md` (exact signatures, searched not read).

---

## 1. Scopes

Every write and read carries a scope path. Format is `type:id` segments joined by
`/`. Built-in types include `org`, `dept`, `team`, `app`, `user`, `agent`,
`service`, `ws`, `project`, `global`, and `system`, and you can invent your own.
Segment length limits and full semantics are in
`CortexDB_docs/01_MEMORY_SCOPES_AND_RECALL.md`; check there rather than trusting
the summary here.

For this app:

```
app:<slug>                          shared app-level knowledge (rare)
app:<slug>/user:<supabase_user_id>  per-user memory (the default)
```

Use the existing Supabase user ID verbatim as the `user:` segment. Do not mint a
parallel identifier, and do not use email addresses.

Scopes auto-provision on first write. You do not need to register them ahead of
time, though explicit registration via `POST /v1/scopes` is available when
members or policies need setting.

## 2. Recall views

The `view` parameter decides how far a read reaches. This is the main correctness
knob and the main leak risk.

| View | Reads from |
|---|---|
| `raw`, `granular`, `structured` | the named scope only |
| `holistic` | the scope plus its ancestors |
| `descend` | the scope plus its descendants |

`holistic` is the default for `/v1/recall` and `/v1/answer`.

For this app: read at `app:<slug>/user:<id>` with `holistic`. That gives the
user's own memory plus anything shared at the app level, and nothing from any
other user.

**Never read at `app:<slug>` with `descend` in a user-facing path.** That reaches
into every user's memory at once.

## 3. Migrating existing conversation history

The app already has chat history in Supabase. Do this in stages, and stop for
review between each.

**Stage 1: dual write.** Keep writing to Supabase as today. Add a CortexDB write
alongside it. Nothing reads from CortexDB yet. Confirm writes land by recalling
them manually.

**Stage 2: shadow read.** Read from CortexDB in parallel with the existing
retrieval. Log both. Compare quality on real traffic. Do not change what the user
sees.

**Stage 3: cut over reads.** Switch the prompt context to CortexDB recall. Keep
the Supabase writes.

**Stage 4: backfill.** Bulk-load historical conversations via
`POST /v1/experience/bulk`. Set `observed_at` to the original message timestamp,
not to now. If you skip this, every historical message looks like it happened
today and temporal queries break.

**Stage 5: retire.** Drop the Supabase memory tables only after stages 1 to 4
have been stable for a while. Not before.

Do not attempt stages 4 and 5 in the same change as stages 1 to 3.

## 4. Idempotency

Writes take an `idempotency_key`. Always set it, derived from something stable
such as the message ID. Without it, retries and re-runs duplicate memories, which
degrades recall quality quietly rather than failing loudly.

## 5. Timestamps

Always pass an explicit `observed_at` in ISO 8601 UTC. CortexDB is bi-temporal:
it tracks when something was true in the world separately from when it was
ingested. Defaulting to ingest time throws away the first axis and makes
questions like "what did the user prefer last month" unanswerable.

## 6. Deletion

Deletion goes through `POST /v1/forget` with a reason, not by dropping rows. This
keeps the audit trail intact. For user-initiated data deletion requests, preview
first with `POST /v1/erasures/preview` before executing.

## 7. Error handling

Do not wrap CortexDB calls in bare try/except that swallows the error. A failed
recall should degrade visibly (log it, run without memory context) rather than
silently return empty and make the agent look forgetful. Silent memory failure is
the hardest class of bug to notice in this kind of app.

## 8. Non-text content

If the task involves uploading files rather than writing text, read
`CortexDB_docs/02_DATA_INGESTION_AND_PROCESSING.md` first. The essentials:

- Text, markdown, CSV, HTML, JSON, and XML are ingested natively with no
  external dependency.
- PDFs, Office documents, images, audio, and video each require a **server-side
  processor to be enabled**. If it is not, the file uploads successfully, the
  bytes are retained, and it **never becomes searchable**. It fails silently.
- If you already hold an authoritative transcript or extracted text, pass it
  inline on the blob reference so CortexDB skips re-deriving it.
- Do not build a client-side extraction workaround when a processor is not
  enabled. Raise it. That is a deployment setting, not an integration gap.

## 9. LLM configuration is not our concern

CortexDB calls models internally in five places: embedding, entity extraction,
async enrichment, answer generation, and an optional verifier. On the hosted
service all five run server-side with CortexDB's own credentials.

**Do not add `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or any `CORTEX_LLM_*` or
`CORTEX_EMBEDDING_*` variable to this project expecting CortexDB to pick them
up.** Those are read by the CortexDB **server** process, not by the client SDK.
Setting them here does nothing. There is currently no supported way to supply
your own model key to the hosted service, and no per-request key parameter on the
API. If you find yourself designing one, stop and ask.

The app's own model key, whatever powers the chat, is separate. CortexDB neither
needs it nor reads it. Keep the two clearly apart in configuration and in any
documentation you write.

### What this means for expectations

Available without any keys: embedding, synchronous entity extraction on write,
and recall across the lower layers. For remembering what a user said and bringing
it back, this is sufficient.

Not available: **async enrichment is an opt-in server-side job and is off by
default.** It builds the higher-abstraction layers. If recall seems shallower
than the documentation suggests, this is a plausible cause, it is not fixable
from this repo, and it is not a bug in the integration.

Raise it rather than compensating for it in application code. Specifically: do
not build a summarization pass, a fact-extraction step, or a "memory
consolidation" cron in this app to make up for it. That rebuilds by hand exactly
what CortexDB exists to provide, and it will have to be torn out later.

### Data handling

On hosted, text written to CortexDB is processed by third-party model providers
under CortexDB's accounts. Flag anything sensitive to the developer rather than
storing it silently.

## 10. Token expiry

Free-tier tokens have a 7-day TTL. Auth errors after a period of working code
almost always mean expiry, not a code bug. Check `cortexdb auth whoami` before
debugging anything else.

---

## Quick reference: what to look up

| Task | Endpoint |
|---|---|
| Store a memory | `POST /v1/experience` |
| Bulk load | `POST /v1/experience/bulk` |
| Retrieve context pack | `POST /v1/recall` |
| Grounded answer | `POST /v1/answer` |
| Delete with audit | `POST /v1/forget` |
| Auth and reachability check | `GET /v1/auth/whoami` |
| Facts about an entity | `GET /v1/facts` |
| How a value changed over time | `GET /v1/facts/timeline` |

Parameters and SDK syntax: look them up per `AGENTS.md` rule 1. Do not infer
them from this table. Offline, search `CortexDB_docs/04_FULL_REFERENCE.md` for
the specific endpoint. It has a table of contents with per-section anchors at the
top; find the section, then read that section only.
