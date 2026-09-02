# CortexDB documentation: start here

Offline documentation library. **Read this index first, then open only the one
document that matches your task.** Do not read these files end to end. Search
them for the specific endpoint, parameter, or concept you need.

This is a point-in-time snapshot. If it disagrees with a live source
(`cortexdb_docs_search`, `cortexdb.ai/llms.txt`, `cortexdb.ai/docs`), **the live
source wins.**

---

## Route by task

| If your task involves | Open |
|---|---|
| Where to write memory, how to read it back, scope paths, `view` selection, isolation between users, designing a scope schema | `01_MEMORY_SCOPES_AND_RECALL.md` |
| Recall vs Ask, `/v1/recall` vs `/v1/answer`, what a context pack contains | `01_MEMORY_SCOPES_AND_RECALL.md` |
| Uploading files, PDFs, Office docs, images, audio, video, archives, blobs, `derived_text`, why an uploaded file is not showing up in recall | `02_DATA_INGESTION_AND_PROCESSING.md` |
| Backfilling existing data from Slack, Jira, Notion, FreshDesk, TL;DV, Gmail; continuous sync; `cortexdb-sync` | `03_CONNECTORS_AND_DATA_LOADING.md` |
| Exact API signatures, SDK method names, auth, error codes, integrations, the five layers, bi-temporal model, operations, anything not covered above | `04_FULL_REFERENCE.md` |
| Nothing above matches, or the answer contradicts itself | Ask the developer. Do not guess. |

---

## Decision shortcuts

**"How do I store a conversation turn?"**
`01` for the scope and shape, `04` (search `experience`) for the exact signature.

**"How do I retrieve context for a prompt?"**
`01`, the Recall vs Ask section. Then `04` (search `recall`) for parameters.

**"Should this read use holistic or descend?"**
`01`, the Views section. This is the highest-consequence choice in an
integration; get it wrong and you either miss context or leak another user's
memory into the response.

**"A PDF uploaded fine but recall does not find it."**
`02`, section 6. Almost certainly the document processor is not enabled on the
deployment. This is a server-side setting and not fixable from application code.

**"Beliefs and concepts are empty."**
`01`, the five layers section, then `.cortexdb/CONVENTIONS.md` section 9. This may
be enrichment configuration rather than a bug. Raise it rather than building a
summarization pass to compensate.

**"I need to load two years of support tickets."**
`03`. Check `cortexdb-sync list` before writing any custom loader.

**"What is the exact Python/TypeScript method name?"**
`04`. Search the file. Do not infer from another library's API.

---

## Contents of the library

| File | Source | Size |
|---|---|---|
| `01_MEMORY_SCOPES_AND_RECALL.md` | Memory, Scopes & Recall guide, v1, July 2026 | short |
| `02_DATA_INGESTION_AND_PROCESSING.md` | Data Ingestion & Content Processing technical reference, v1, July 2026 | short |
| `03_CONNECTORS_AND_DATA_LOADING.md` | Connector deployment guide, sanitized | short |
| `04_FULL_REFERENCE.md` | Full cortexdb.ai/docs, compiled 2026-07-05, 115 pages, 13 sections | large, search it |
| `CortexDB_Documentation.pdf` | Original PDF of the above | fallback only |

`04` is large. It has a table of contents at the top with per-section anchors.
Find the section first, then read that section. Reading it linearly will consume
the entire context window before you reach the part you need.

---

## Standing rules

1. Never write a CortexDB API call from memory or from how a similar library
   works. The v1 API is not what most models learned. Legacy endpoints such as
   `/v1/remember` and `/v1/admin/health` no longer route and will 404.
2. Prefer live sources. This library is the offline fallback.
3. When two documents disagree, the more specific one wins for its topic, and any
   live source beats both.
4. When nothing here answers the question, say so and ask. Do not guess a
   signature.
