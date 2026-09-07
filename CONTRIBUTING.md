# Contributing to Onboarding-Packs

**Issues and PRs are very welcome.** This repo is the official onboarding documentation for
CortexDB, so the bar is *accuracy*, not polish: if a command in here didn't work on your
machine, that's a bug worth filing.

---

## The fastest way to help

| You found | Do this |
|---|---|
| A command/endpoint in the docs that fails | Open a **Docs bug** issue with the exact command and the real output |
| A claim that looks wrong or overstated | Open a **Docs bug** and quote the line — see [Honesty rules](#honesty-rules) |
| A missing step that blocked you | Open a **Docs improvement** issue describing where you got stuck |
| A typo or a one-line fix | Just send the PR, no issue needed |

You don't need to be a CortexDB employee, and you don't need permission to open an issue.

---

## Sending a pull request

`main` is protected — nobody pushes to it directly, including maintainers. Everything lands
through a reviewed PR.

1. **Fork** this repository (the green *Fork* button). External contributors cannot push
   branches to this repo; that's expected.
2. Create a branch: `git checkout -b fix/self-host-port-typo`
3. Make the change. Keep the diff focused — one topic per PR reviews much faster than a
   sweeping rewrite of several packs.
4. Run the [local checks](#local-checks) below.
5. Open the PR against `main` and fill in the template.

A maintainer will review. CI must be green and one maintainer must approve before merge.

### What gets merged quickly

- Corrections backed by real terminal output ("I ran X, got Y, docs say Z")
- Clarified prerequisites, versions, and platform caveats
- Fixing broken links, stale paths, wrong ports, wrong file locations

### What needs a discussion first

Open an issue before writing the code if your PR would:

- Restructure the pack layout (`00-` … `03-` folders) or move files between packs
- Add a new onboarding path or a new harness under `03-harness-attach/`
- Change the routing tables in [`README.md`](README.md) or [`AGENTS.md`](AGENTS.md)
- Add a dependency to any script

Large unannounced rewrites are the one thing likely to sit unmerged, so please ask first —
it's not a rejection, it's just cheaper for both of us.

---

## Ground rules

### Never commit credentials

This is the one hard rule.

- `.env`, `cortex.env`, and `.signup.json` are gitignored. Keep it that way.
- `env.example` / `cortex.example.env` hold **placeholders only** — empty values or
  `<YOUR_OPENAI_API_KEY>`-style markers. Never paste a real value "just to show the format".
- Never paste an API key, bearer token, or tenant token into an issue, a PR body, a commit
  message, or a screenshot. Redact them from any log output you attach.
- If you believe a secret has been committed anywhere, do **not** open a public issue —
  follow [SECURITY.md](SECURITY.md).

### Don't leak local machine paths

Docs must be portable. Use repo-relative paths (`02-app-in-repo/docs/00_INDEX.md`) or a
documented variable (`$PACK_ROOT`, `PROJECT_DIR`). Never `/Users/<you>/...` or `C:\Users\...`.

### Honesty rules

The docs deliberately avoid unverified marketing claims. Please don't reintroduce them:

- Integrations count is **47** (not 53).
- Do **not** cite LongMemEval **93.8%**.
- Do **not** cite **~742 ms** as a latency claim.
- **Raft** is experimental, not shipped.
- CortexDB is **not** "always-on" without setup.
- Free-tier anonymous tokens expire (~7 days); re-signup creates a new, empty tenant.

If you have measurements that would justify a number, put them in the PR description so a
maintainer can verify before it goes into the docs.

### Don't invent API surface

Every endpoint in these docs must exist. `/v1/remember` is a legacy path that 404s — it is
the canonical example of a hallucinated call. Verify against
<https://cortexdb.ai/docs> or `02-app-in-repo/docs/00_INDEX.md` before documenting a call.

### Style

- Markdown, one sentence per line is not required — write naturally.
- Prefer copy-pasteable fenced blocks over prose descriptions of commands.
- Say which platform a command targets when it differs (macOS / Linux / Windows).
- Keep the agent-facing files (`AGENTS.md`, `*.template`) imperative and unambiguous;
  they are read by coding agents, not just humans.

---

## Local checks

```bash
git grep -nE 'sk-[A-Za-z0-9]{16,}|eyJ[A-Za-z0-9_-]{20,}|BEGIN [A-Z ]*PRIVATE KEY'
```

```bash
git grep -n '/Users/'
```

Both should print nothing. CI runs the same checks plus a secret scan on every PR.

---

## Code of Conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).
