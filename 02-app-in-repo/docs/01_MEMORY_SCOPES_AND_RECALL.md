# Memory, Scopes & Recall

Converted from the CortexDB Product & Sales Guide, v1, July 2026.
**Read this first for anything involving where memory is written or how it is
read back.** Scope and view design is the highest-consequence decision in a
CortexDB integration and the easiest to get wrong.

---

## The mental model

CortexDB is a memory. You do two things with it.

**Write.** Save experiences (a ticket, a chat, a CRM note) into an address.

**Read.** Either Recall ("give me the relevant memories") or Ask ("answer this
question from memory, with sources").

Every read has two dials:

- **Dial 1, WHERE to look** = the scope (which address) plus the view (how far to
  reach: just here, up to parents, or down to children).
- **Dial 2, WHAT to look for** = your query or question, in plain language.

Everything CortexDB does is a combination of those two.

---

## Scopes: the address system

A scope is an address written like a folder path. Each segment is a `type:id`
pair.

```
org:acme / dept:support / user:priya
```

Rules:

- One or more `type:id` segments joined by `/`.
- Types and ids are lowercase-friendly, no spaces, up to 128 characters.
  Use `-` or `_`, for example `user:cust-8813`.
- Deeper means more specific. `org:acme` is the whole company;
  `org:acme/dept:support/category:billing` is one narrow corner.

Built-in types: `org`, `dept`, `team`, `app`, `user`, `agent`, `service`,
`ws` (workspace), `project`, `global`, `system`.

You can invent any type you need: `customer:`, `source:` (slack/jira/...),
`category:`, `region:`, `device:`, `campaign:`. The type is a label that keeps
ids meaningful and prevents collisions, so `user:priya` will not clash with
`category:priya`.

### Why scopes matter

1. **Isolation.** One customer's or team's memory never leaks into another's.
2. **Organization.** Data has a natural home.
3. **Reach control.** The scope you name plus the view you pick decide exactly
   how much memory a query sees. This third one is the important one.

### The family tree

```
org:acme                          <- root, shared, company-wide
├── dept:support
│   ├── user:priya
│   ├── category:billing
│   └── category:vpn
└── dept:sales
    └── user:rahul
```

**Ancestors** are the scopes above a given scope (walk up).
**Descendants** are the scopes below it (walk down).

---

## Writing memory

```
POST /v1/experience
{
  "scope": "org:acme/dept:support/category:billing",
  "modality": "conversation",
  "content": { "text": "Customer couldn't see their invoice; resolved by resending it." },
  "context": {
    "observed_at": "2026-05-02T10:00:00Z",
    "labels": ["category:billing", "status:resolved"]
  }
}
```

Only `scope`, `modality`, and `content.text` are required. Everything else is
optional and makes memory richer.

### Actor and subject

Two optional roles can be tagged on a write:

- `observed_actor` : who did or said it (for example, the agent).
- `subject` : who it is about (for example, the customer).

This lets you later ask "what do we know about customer X" regardless of which
agent handled them. If unset, CortexDB treats the writer as both, which is fine
for most cases.

---

## The five layers

You write raw text; CortexDB derives five layers from it.

| Layer | Plain English | From the billing example |
|---|---|---|
| Events | The raw thing that happened | "Customer couldn't see invoice; resolved by resending." |
| Facts | Atomic extracted statements, with dates | `invoice-not-visible -> resolved-by -> resend` |
| Episodes | Related events grouped into a session or thread | The whole billing conversation as one episode |
| Beliefs | Reconciled current understanding across many facts | "The usual fix for invisible-invoice tickets is to resend the invoice." |
| Concepts | Higher-order themes across beliefs | "Billing-visibility is a recurring issue class." |

Facts appear within seconds of a write. Beliefs, episodes, and concepts are
rebuilt automatically in the background within a minute or two.

Note for implementers: if beliefs and concepts are not appearing, this may be a
server-side enrichment configuration matter rather than an integration bug.
See `AGENTS.md` and `.cortexdb/CONVENTIONS.md` section 9 before working around it.

---

## Reading: Recall vs Ask

| | Recall `/v1/recall` | Ask `/v1/answer` |
|---|---|---|
| You get | Relevant memories: a ready-to-use text block, the layers, and sources | A written answer grounded in memory, with citations |
| Use when | Your app or your own model will use the memories | You want CortexDB to compose the answer |
| Example | "Give me everything relevant to this new billing ticket." | "What's the likely fix for this billing ticket?" |

```
POST /v1/recall
{ "scope":"org:acme/dept:support", "query":"invoice not visible", "view":"descend" }

POST /v1/answer
{ "scope":"org:acme/dept:support", "view":"descend",
  "question":"A customer says they can't see their invoice. What should the agent do?" }
```

Recall returns a StratifiedPack: a `context_block` (clean text you can drop
straight into a prompt), the layers, and provenance. Ask returns answer text plus
sources.

---

## Views: the most important concept

The view decides how far from the named scope CortexDB reaches.

| View | Reach | Plain English |
|---|---|---|
| `granular` (alias `local`) | exactly this scope | Only what is in this folder. All five layers, this scope only. |
| `holistic` (default) | this scope plus ancestors | This folder plus shared knowledge inherited from parent folders. Adds a ready-to-use context block. |
| `descend` | this scope plus all descendants | This folder and everything in all its sub-folders, rolled up. |
| `raw` | exactly this scope | Just raw events, no derived layers. For debugging and exact audit. |
| `structured` | knowledge-graph view | Entities and relationships graph. Advanced and integrations. |

### Worked example

Given shared billing policy written at `org:acme`, and tickets under each
category:

| Recall on | View | Result |
|---|---|---|
| `.../category:billing` | `granular` | Only the billing tickets. Not the shared policy, not VPN. |
| `.../category:billing` | `holistic` | Billing tickets plus the shared refund policy inherited from `org:acme`. |
| `dept:support` | `descend` | Everything under support, billing and VPN rolled up. |
| `org:acme` | `descend` | The entire company's memory. Widest possible. |

**The intuition.** `holistic` reaches up so a narrow scope inherits shared
knowledge without duplicating it. `descend` reaches down so a broad scope rolls
up everything beneath it. `granular` stays put.

**Leak warning.** In any user-facing read path, do not read at a shared parent
scope with `descend`. That reaches into every user's memory at once.

---

## Query styles (automatic)

Your query or question is plain language. CortexDB blends several search styles
automatically; you do not pick one.

| Style | What it catches | Example |
|---|---|---|
| Semantic | Same meaning, different words | "can't reach the network" finds "VPN won't connect" |
| Keyword | Exact terms, names, codes | "error 403" finds tickets mentioning 403 |
| Relationship | Connected people and things via the graph | tickets linked to the same customer or product |

---

## Patterns you will actually use

**Similarity recall.** Find past items like this new one.
`recall{scope, query:"<new ticket text>", view:"descend"}`

**Grounded answer.** Answer this, with sources.
`answer{scope, question:"...", view:"descend"}`

**Inherited-context answer.** Narrow scope, but honor company rules.
`answer{scope:".../category:billing", view:"holistic", question:"can we refund this?"}`

**Time-aware question.** A question can carry a reference date; stale facts are
retired automatically.
`answer{scope, question:"what's our current refund policy?", question_date:"2026-07-01"}`

**Direct layer reads.** List derived knowledge without a search.
`GET /v1/facts?scope=...` and likewise `/v1/beliefs`, `/v1/episodes`,
`/v1/events`, `/v1/understanding`.

---

## Designing a scope schema

Three principles, in priority order:

1. **Isolate first.** Put the thing that must never mix at the top. For a
   platform serving many companies that is `customer:`. For one company it is
   `org:`.
2. **Organize by the natural owner.** Team, department, or the entity the memory
   is about.
3. **Add a category only if it sharpens recall.** If items span very different
   topics, a `category:` level makes similarity matching tighter. If not, skip it.

### Decision guide

| Ask yourself | Then |
|---|---|
| Do we serve multiple end-customers whose data must never mix? | Top level is `customer:<x>` or `org:` |
| Is memory naturally about a person or customer? | Add `user:<id>`, read with `descend` for their full picture |
| Are there shared rules everyone should honor? | Write them high at `org:`, read child scopes with `holistic` |
| Do items fall into distinct topics? | Add `category:<topic>` |
| Multiple data sources feeding one brain? | Add `source:<system>` lanes, read the parent with `descend` |

### Three ready-made schemas

```
# 1) Support ticket auto-resolution
org:acme/customer:<c>/dept:{it,hr}/category:<topic>
write: each closed ticket at its dept/category
read : answer{ dept/category, view:descend, question:"<new ticket>" }

# 2) Customer-360 / next-best-action
org:acme/customer:<c>/user:<id>/source:{app,crm,sales,support}
write: each department writes what it knows into its source lane
read : recall{ user, view:descend } -> one merged profile

# 3) Cross-source company knowledge
org:acme/source:{slack,jira,notion,freshdesk}
write: each tool's items into its source lane
read : answer{ org:acme, view:descend, question:"..." }
```

For a consumer app with per-user memory, the simplest correct schema is
`app:<slug>/user:<user_id>`, read with `holistic`.

---

## Quick reference

| Want to | Scope + view |
|---|---|
| Look at exactly one corner | that scope, `granular` |
| Honor shared rules from above | the specific scope, `holistic` |
| Search across everything beneath a scope | the parent scope, `descend` |
| Get relevant memories for my app to use | Recall |
| Answer a question with sources | Ask (`/v1/answer`) |
| List derived knowledge directly | `GET /v1/{facts,beliefs,episodes,events,understanding}?scope=...` |
| Keep customers or teams from mixing | put the isolation type at the top of the scope |
