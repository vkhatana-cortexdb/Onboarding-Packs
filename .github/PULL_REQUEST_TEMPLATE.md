## What this changes

<!-- One or two sentences. Link the issue if there is one: Fixes #123 -->

## Why

<!-- If this corrects a documented step, paste the real terminal output that proves the old
     text was wrong (secrets redacted). That's the fastest possible review. -->

## Checklist

- [ ] No API keys, tokens, or `.env` contents in the diff, the commit messages, or this description
- [ ] Example env files still contain placeholders only
- [ ] No local machine paths (`/Users/...`, `C:\Users\...`) — repo-relative paths or `$PACK_ROOT` instead
- [ ] No new API endpoints invented; anything documented exists in https://cortexdb.ai/docs
- [ ] No unverified claims reintroduced (integrations = 47; no LongMemEval 93.8%; no ~742 ms; Raft is experimental)
- [ ] Links and file paths I touched resolve
- [ ] Diff is focused on one topic

## Verified how

<!-- e.g. "Ran the 01-self-host guide end to end on macOS 15.5 / Docker 27.1.1" — or "docs-only,
     not executed". Both are fine, just say which. -->
