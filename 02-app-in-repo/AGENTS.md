# Agent rules: CortexDB in this repo

This project uses **CortexDB** for long-term memory. The existing database
(Supabase / Postgres) stays. CortexDB is added alongside it, not instead of it.

## Hard rules

1. **Never write a CortexDB API call from memory or from training data.**
   The v1 API is not what most models learned. Legacy endpoints such as
   `/v1/remember` and `/v1/admin/health` no longer route and will 404. Do not
   infer a signature from how a similar memory library works.

   Before writing any CortexDB call, work down this chain and stop at the first
   source that answers the question:

   1. The `cortexdb_docs_search` MCP tool, if it is connected.
   2. https://cortexdb.ai/llms.txt, then follow the relevant link.
   3. https://cortexdb.ai/docs, browsed directly.
   4. **`CortexDB_docs/00_INDEX.md` in this repo.** Offline documentation
      library. Works with no network and no MCP. Read the index, let it route
      you to the right document, then search that document. Do not read the
      documents linearly.
   5. Ask the developer to paste the relevant section.

   If every one of these is unavailable, **stop and say so.**

   Sources 1 to 3 are live and authoritative. Source 4 is a point-in-time
   snapshot, so if it contradicts a live source, the live source wins.

2. **Consult the docs as soon as you are unsure, not after a failed attempt.**
   Uncertainty about a parameter name, a view value, a scope format, or whether
   a capability exists at all is itself the trigger. Looking it up costs one
   tool call. Guessing costs a debugging session, and a wrong scope leaks user
   data.

3. **Verify auth before writing integration code.**
   ```bash
   cortexdb auth whoami
   ```
   If this fails, stop. The usual cause is `CORTEXDB_ACTOR` not matching the
   token's `sub` claim. Do not work around auth failures with try/except.

4. **Never use a flat scope.** Every write and every read carries a scope path.
   Use `app:<slug>/user:<user_id>` where `<user_id>` is the existing Supabase
   user ID. This is the isolation boundary. Getting it wrong leaks one user's
   memory into another user's conversation. Read
   `CortexDB_docs/01_MEMORY_SCOPES_AND_RECALL.md` before choosing a scope or a
   `view`.

5. **Do not migrate data without an explicit go-ahead.** Propose a plan, show
   it, wait for approval.

6. **Never commit tokens.** Not in `.cursor/mcp.json`, not in `.env`, not in
   example code, not in test fixtures.

7. **Do not wire model API keys into this app for CortexDB's benefit.**
   CortexDB's internal model calls are configured server-side. Setting
   `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or any `CORTEX_LLM_*`,
   `CORTEX_EMBEDDING_*`, or `CORTEX_DOCUMENT_*` variable in this project does
   nothing for CortexDB. The app's own model key, whatever powers the chat, is
   separate and stays where it is. See `.cortexdb/CONVENTIONS.md` section 9.

8. **Do not rebuild by hand what CortexDB provides.** If recall seems shallow, a
   file does not appear in search, or a derived layer looks empty, that is
   usually a server-side configuration matter, not a gap to fill in application
   code. Do not add a summarization pass, an embedding pipeline, a
   memory-consolidation cron, or a client-side text extractor. Raise it instead.
   See `.cortexdb/CONVENTIONS.md` section 9 and
   `CortexDB_docs/02_DATA_INGESTION_AND_PROCESSING.md` section 6.

## Where data goes

> If you would put a unique index on it, it goes in Postgres.
> If you would put it in a prompt, it goes in CortexDB.

Stays in Postgres: users, auth, sessions, billing, anything with a foreign key,
anything with a uniqueness constraint, anything that must be exactly right on the
first read.

Moves to CortexDB: conversation turns, user preferences and stated intent,
anything retrieved by meaning rather than by ID, anything that gets more useful
as it accumulates.

When unsure which side something falls on, ask. Do not decide silently.

## The two calls you will use most

Store a turn: `POST /v1/experience`
Retrieve context: `POST /v1/recall`

Exact signatures, parameters, and SDK syntax: look them up per rule 1. Do not
reproduce them from this file, because this file will go stale.

## Documentation map

| Question | Go to |
|---|---|
| Anything, first stop | `CortexDB_docs/00_INDEX.md` |
| Scopes, views, recall vs ask, isolation | `CortexDB_docs/01_MEMORY_SCOPES_AND_RECALL.md` |
| Files, PDFs, images, audio, blobs | `CortexDB_docs/02_DATA_INGESTION_AND_PROCESSING.md` |
| Backfilling from Slack, Jira, Notion, email | `CortexDB_docs/03_CONNECTORS_AND_DATA_LOADING.md` |
| Exact API and SDK reference | `CortexDB_docs/04_FULL_REFERENCE.md` |
| This project's conventions and migration plan | `.cortexdb/CONVENTIONS.md` |

Live docs: https://cortexdb.ai/docs
