# Claude Code x CortexDB onboarding (execute this)

You are an agent (Claude Code itself, or another agent with shell and file access). The user gave you this pack (`handoff/ClaudeCode/`). Execute every step for the basic CortexDB integration in Claude Code. Do not print tokens. Do not commit secrets.

`PACK` = the folder that contains this file.

Goal: every Claude Code session on this machine can and should recall CortexDB before acting and write durable actions back (`harness:claude-code`).

## 0. Inputs

- `CORTEX_DIR`: path the user named with CortexDB config; else Personal-Brain path; else `~/CortexDB-Personal`
- `SHARE_BRAIN`: true if that dir (or `personal-brain-demo/`) has a complete `.env` with CORTEXDB_URL, CORTEXDB_API_KEY, CORTEXDB_ACTOR, CORTEXDB_SCOPE
- `PROJECT_DIR`: optional repo for project-level CLAUDE.md / .mcp.json

## 1. Prerequisites

Python 3.10+, Claude Code installed, network to https://api-v1.cortexdb.ai

## 2. Install MCP package

Install and pin a current v1 server. Legacy 0.2.x / early 0.3.x 404 on tools.

Use: `python3.11 -m pip install -U 'cortexdb-mcp>=0.6.0'` then `cortexdb-mcp --version` (expect >= 0.6.0, ideally 0.7.1+).

Also read: https://cortexdb.ai/agent/manifest.json , https://cortexdb.ai/agent/SKILL.md , https://cortexdb.ai/docs/sdks/mcp-server

## 3. Identity

### 3a. Shared brain (SHARE_BRAIN=true)

Source the complete `.env` (or personal-brain-demo/.env). Do not signup. Do not use zero-config MCP without env (that mints a different identity).
Run `cortexdb auth whoami` and report caller/expiry only. Never print the API key.

### 3b. New eval brain (SHARE_BRAIN=false)

Only if the user accepted a new brain: create CORTEX_DIR, install cortexdb-cli>=0.5.0, run `cortexdb init`, write `.env` mode 0600 with URL/API_KEY/ACTOR/SCOPE.
Zero-config alternative: omit env in mcp.json so cortexdb-mcp signups on first launch (~/.config/cortexdb-mcp/state.json). Tell the user this is a NEW 7-day tenant.
Never mint on top of a working shared token.

## 4. Wire Claude Code MCP (user-global)

User-global MCP lives in **`~/.claude.json`** under the top-level `mcpServers` key — **not** `~/.claude/mcp.json` (that path is wrong for current Claude Code).

Prefer stdio with an absolute Python and the package entrypoint (or a traced wrapper):

```json
{
  "mcpServers": {
    "cortexdb": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/python3",
      "args": ["-m", "cortexdb_mcp"],
      "env": {
        "CORTEXDB_URL": "https://api-v1.cortexdb.ai",
        "CORTEXDB_API_KEY": "<from .env - do not commit>",
        "CORTEXDB_ACTOR": "<from .env>",
        "CORTEXDB_SCOPE": "<from .env>"
      }
    }
  }
}
```

If `cortexdb-mcp` is on PATH after install, `args` can be a single path to that script / a traced wrapper instead of `-m cortexdb_mcp`. See `mcp.json.example` in this pack for a minimal shape — merge that block into `~/.claude.json` `mcpServers`.

For a shared brain, put env from `.env` into the cortexdb server block. Generate JSON with a local script that reads `.env` — do not echo values to chat. Keep `~/.claude.json` mode 0600 if it holds secrets.

Optional: same block in `~/.cursor/mcp.json`. If PROJECT_DIR is set, optional `PROJECT_DIR/.mcp.json` and gitignore it.

## 5. Wire recall then act then write rules

Copy `CLAUDE.md.template` to `~/.claude/CLAUDE.md` (merge if a file already exists; keep unrelated user text).
If PROJECT_DIR is set, also write `PROJECT_DIR/CLAUDE.md` pointing at global rules and lane harness:claude-code.

Hard rules that must be present:
1. CortexDB is memory of record (not chat history).
2. On tasks that need memory: MCP get_context / memory_search before acting.
3. After durable work: MCP memory_store including harness:claude-code.
4. Never invent REST signatures; use llms.txt / manifest / docs.
5. Never signup over a working shared identity.
6. Never print tokens.

## 6. Labels and lanes

- Claude Code: MCP memory_store / get_context / memory_search — label harness:claude-code
- Grok Bot (sibling pack): HTTP scripts/harness.py — label harness:grokbot

Default read: broad recall (no label filter). Optionally filter by harness label when looking for one harness.

## 7. Prove it (basic smoke)

1. Tell the user to restart Claude Code so MCP reloads.
2. In Claude Code: call health_check; memory_store an onboard one-liner that includes harness:claude-code; then get_context or memory_search for that line.
3. Optional shell check after sourcing the shared env file: cortexdb recall filtered by labels=harness:claude-code for the onboard text.

Report: MCP path; CLAUDE.md path; shared vs minted; whoami caller (no token); smoke summary.

## 8. Out of basic scope

- Forced interceptor (rules are soft)
- Separate docs-search MCP not shipped
- Dedicated answer MCP tool is REST-only today
- Full customer AGENTS.md app pack
- Past Claude transcript ingest

## Do not

- Put secrets in chat, git, or replies
- Mint a new identity when SHARE_BRAIN is true
- Use the wrong public package name for the SDK
- Keep a legacy MCP build that 404s on tools
- Claim recall works without the smoke

## Sibling

Grok Bot HTTP helper pack lives next door in Grokbot with GROKBOT-ONBOARDING.md.

