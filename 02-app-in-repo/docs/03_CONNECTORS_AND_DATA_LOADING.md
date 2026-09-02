# Connectors & Bulk Data Loading

Technical reference for backfilling existing data into CortexDB and keeping it in
sync. **Read this when the task is "get our existing data from X into CortexDB",
as opposed to writing new interactions as they happen.**

Derived from a pilot deployment guide. Customer-specific details, credentials,
and commercial framing have been removed. Confirm the current connector package
version and available connectors against a live source before relying on this.

---

## How ingestion works

Each item from a source (a Slack message, a Jira issue, a support ticket, a
meeting recording, a Notion page, an email thread) becomes an **Event**, stamped
with its real source timestamp so history lands on the correct timeline. From
those events CortexDB derives Facts, Beliefs, Episodes, and Concepts.

Every item carries a stable **idempotency key**, so re-running a sync never
creates duplicates. It only adds what is new. Both backfill and continuous sync
are therefore safe to repeat.

Two phases, same connectors:

- **Backfill**, one-time, pulls history.
- **Continuous sync**, keeps it fresh, roughly 60-second freshness.

Under the hood the connectors use `POST /v1/experience` and
`POST /v1/experience/bulk`.

---

## The connector CLI

The connector package installs a `cortexdb-sync` command. It runs wherever you
run it, reads each source with credentials you supply, normalizes the data, and
pushes the result to your CortexDB instance over the token-gated API.

**Source credentials stay wherever the connector runs.** Only the resulting
memory content reaches CortexDB.

```bash
# point the connectors at your instance (once)
export CORTEXDB_URL=https://api-v1.cortexdb.ai
export CORTEXDB_API_KEY=<your token>
export CORTEXDB_ACTOR=<your actor>

# BACKFILL: pull all history since a date, into a per-source scope
export SLACK_BOT_TOKEN=<your source credential>
cortexdb-sync sync slack \
  --scope org:<you>/source:slack \
  --since 2024-01-01T00:00:00Z \
  --wait-derivation          # blocks until facts/concepts catch up

# CONTINUOUS SYNC: re-check every 60s, picks up anything new since last run.
# No webhooks needed. Closes the gap during and after backfill.
cortexdb-sync watch slack \
  --scope org:<you>/source:slack --interval 60

cortexdb-sync list      # every connector plus the env vars it needs
cortexdb-sync status    # last-synced cursor per connector
```

Run `cortexdb-sync list` rather than trusting any static list of connectors,
including the one below.

---

## Per-source credentials

| Source | Command | Credentials | Optional scoping | Ingests |
|---|---|---|---|---|
| Slack | `sync slack` | `SLACK_BOT_TOKEN` with `channels:history`, `channels:read`, `groups:history`, `users:read` | `SLACK_CHANNELS` | channel messages and threads |
| Jira | `sync jira` | `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` | `JIRA_PROJECT_KEYS` | issues and comments |
| Notion | `sync notion` | `NOTION_TOKEN` (internal integration token) | `NOTION_DATABASES`, `NOTION_PAGES` | pages and database entries |
| FreshDesk | `sync freshdesk` | `FRESHDESK_DOMAIN`, `FRESHDESK_API_KEY` | `FRESHDESK_INCLUDE_CONVERSATIONS` (default on) | tickets and conversations |
| TL;DV | `sync tldv` | `TLDV_API_KEY` | | meetings and speaker-segmented transcripts |
| Gmail / Workspace | `sync google-workspace` | `GW_SERVICE_ACCOUNT_KEY` (service-account JSON with domain-wide delegation, scope `gmail.readonly`), `GW_DELEGATED_USER`, `GW_GMAIL=true` | | email threads for the delegated mailbox |

Use dedicated read-only service accounts wherever the source supports it, rather
than a person's personal login.

---

## Scope design for connector data

Each source normally gets its own lane so you can read across all of them:

```
org:<you>/source:{slack,jira,notion,freshdesk,tldv,gmail}
```

Write each tool's items into its source lane, then read the parent with
`descend` to answer across every tool at once. See
`01_MEMORY_SCOPES_AND_RECALL.md` for view semantics.

If memory is naturally about a person rather than a system, prefer
`.../user:<id>/source:<system>` so a single user's picture merges across sources.

---

## Rules for an agent doing this work

- **Never hardcode a source credential or a CortexDB token** into a script, a
  config file, or a committed `.env`. Read from the environment.
- **Always pass the real source timestamp.** The whole value of the timeline
  depends on it. Do not let ingest time stand in for observed time.
- **Do not write a custom sync loop if a connector exists.** Check
  `cortexdb-sync list` first.
- **Backfill and continuous sync overlap by design.** Idempotency keys handle it.
  Do not build deduplication logic on top.
- **Ask before ingesting anything sensitive.** Email and chat carry the heaviest
  access scopes and the most personal content. Confirm scope and retention with
  the developer before syncing either.
