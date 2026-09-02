# Cursor x CortexDB onboarding (execute this)

You are an agent (Cursor Agent, Cursor CLI, or another agent with shell and file access). The user gave you this pack (`handoff/Cursor/`). Execute every step for the basic CortexDB integration in Cursor. Do not print tokens. Do not commit secrets.

`PACK` = the folder that contains this file.

Goal: every Cursor session on this machine can and should recall CortexDB before acting and write durable actions back (`harness:cursor`).

## 0. Inputs

- `CORTEX_DIR`: path the user named with CortexDB config; else Personal-Brain path; else `~/CortexDB-Personal`
- `SHARE_BRAIN`: true if that dir (or `personal-brain-demo/`) has a complete `.env` with CORTEXDB_URL, CORTEXDB_API_KEY, CORTEXDB_ACTOR, CORTEXDB_SCOPE
- `PROJECT_DIR`: optional repo for project-level `.cursor/rules/cortexdb.mdc` and optional `.mcp.json`

## 1. Prerequisites

Python 3.10+, Cursor installed, network to https://api-v1.cortexdb.ai
Optional: Cursor CLI / agent CLI on PATH for headless prompts.

## 2. Install MCP package

Install and pin a current v1 server. Legacy builds 404 on tools.
Use python3.11 -m pip install -U with cortexdb-mcp at least 0.6.0, then cortexdb-mcp --version (ideally 0.7.1+).
Also read: https://cortexdb.ai/agent/manifest.json , https://cortexdb.ai/agent/SKILL.md , https://cortexdb.ai/docs/sdks/mcp-server

## 3. Identity

### 3a. Shared brain (SHARE_BRAIN=true)

Source the complete `.env` (or personal-brain-demo/.env). Do not signup. Do not use zero-config MCP without env.
Run cortexdb auth whoami and report caller/expiry only. Never print the API key.

### 3b. New eval brain (SHARE_BRAIN=false)

Only if the user accepted a new brain: create CORTEX_DIR, install cortexdb-cli at least 0.5.0, run cortexdb init, write `.env` mode 0600.
Zero-config alternative: omit env in mcp.json so cortexdb-mcp signups on first launch. Tell the user this is a NEW 7-day tenant.
Never mint on top of a working shared token.

## 4. Wire Cursor MCP (user-global)

Write `~/.cursor/mcp.json` mode 0600. For a shared brain, put env from `.env` into the cortexdb server block (command: cortexdb-mcp). See mcp.json.example.
Generate JSON with a local script that reads `.env` — do not echo values to chat.
If PROJECT_DIR is set, optional PROJECT_DIR/.cursor/mcp.json or PROJECT_DIR/.mcp.json and gitignore secrets.
Tell the user to reload MCP in Cursor Settings after writing the file.

## 5. Wire recall then act then write rules

Copy cortexdb.mdc.template to `~/.cursor/rules/cortexdb.mdc` if user-global rules are supported, and/or to `PROJECT_DIR/.cursor/rules/cortexdb.mdc`.
Create parent directories as needed. Merge carefully if a cortexdb rule already exists.

Hard rules that must be present:
1. CortexDB is memory of record (not chat history).
2. On tasks that need memory: MCP get_context / memory_search before acting.
3. After durable work: MCP memory_store including harness:cursor.
4. Never invent REST signatures; use llms.txt / manifest / docs.
5. Never signup over a working shared identity.
6. Never print tokens.

## 6. Labels and lanes

- Cursor: MCP memory_store / get_context / memory_search — label harness:cursor
- Claude Code: label harness:claude-code
- Grok Bot: HTTP harness.py — label harness:grokbot

Default read: broad recall. Optionally filter by harness label.

## 7. Prove it (basic smoke)

1. Reload Cursor MCP / restart Cursor.
2. In Cursor chat or Cursor CLI/agent: health_check; memory_store an onboard one-liner with harness:cursor; get_context or memory_search for that line.
3. Optional shell check after sourcing shared env: cortexdb recall filtered by labels=harness:cursor.

Report: MCP path; rules path; shared vs minted; whoami caller (no token); smoke summary.

## 8. Out of basic scope

- Forced interceptor (rules are soft)
- Separate docs-search MCP not shipped
- Dedicated answer MCP tool is REST-only today
- Full customer AGENTS.md app pack

## Do not

- Put secrets in chat, git, or replies
- Mint a new identity when SHARE_BRAIN is true
- Keep a legacy MCP build that 404s on tools
- Claim recall works without the smoke

## Sibling

Grok Bot pack: ../Grokbot/. Claude Code pack: ../ClaudeCode/.

