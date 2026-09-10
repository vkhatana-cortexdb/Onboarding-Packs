# Claude Desktop x CortexDB onboarding (execute this)

You are an agent with shell and file access. The user gave you this pack (`handoff/ClaudeDesktop/`). Execute every step for the basic CortexDB integration in **Claude Desktop** (the macOS app). Do not print tokens. Do not commit secrets.

`PACK` = the folder that contains this file.

Goal: Claude Desktop sessions on this machine can and should recall CortexDB before acting and write durable actions back (`harness:claude-desktop`).

## 0. Inputs

- `CORTEX_DIR`: path the user named with CortexDB config; else Personal-Brain path; else `~/CortexDB-Personal`
- `SHARE_BRAIN`: true if that dir (or `personal-brain-demo/`) has a complete `.env` with CORTEXDB_URL, CORTEXDB_API_KEY, CORTEXDB_ACTOR, CORTEXDB_SCOPE
- This pack is **not** Claude Code. Claude Code uses `~/.claude.json`. Desktop uses `~/Library/Application Support/Claude/claude_desktop_config.json`.

## 1. Prerequisites

Python 3.10+, Claude Desktop installed (macOS), network to https://api-v1.cortexdb.ai

## 2. Install MCP package

Install and pin a current v1 server. Legacy 0.2.x / early 0.3.x 404 on tools.

Use: `python3.11 -m pip install -U 'cortexdb-mcp>=0.6.0'` then `cortexdb-mcp --version` (expect >= 0.6.0, ideally 0.7.1+).

Confirm the binary exists at `/opt/homebrew/bin/cortexdb-mcp` (or `which cortexdb-mcp`). Prefer that absolute path in Desktop config.

Also read: https://cortexdb.ai/agent/manifest.json , https://cortexdb.ai/agent/SKILL.md , https://cortexdb.ai/docs/sdks/mcp-server

## 3. Identity

### 3a. Shared brain (SHARE_BRAIN=true)

Source the complete `.env` (or personal-brain-demo/.env). Do not signup. Do not use zero-config MCP without env (that mints a different identity).
Run `cortexdb auth whoami` and report caller/expiry only. Never print the API key.

### 3b. New eval brain (SHARE_BRAIN=false)

Only if the user accepted a new brain: create CORTEX_DIR, install cortexdb-cli>=0.5.0, run `cortexdb init`, write `.env` mode 0600 with URL/API_KEY/ACTOR/SCOPE.
Never mint on top of a working shared token.

## 4. Wire Claude Desktop MCP

Config file (macOS):

**`~/Library/Application Support/Claude/claude_desktop_config.json`**

Merge a `mcpServers.cortexdb` block. Prefer **direct stdio binary** — do **not** use traced Python wrappers (`python -m cortexdb_mcp` with wrappers, or shell wrappers that wrap stdout). Those have wedged Claude Desktop.

Recommended shape (see `mcpServers.json.example` in this pack):

```json
{
  "mcpServers": {
    "cortexdb": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/cortexdb-mcp",
      "args": [],
      "env": {
        "CORTEXDB_URL": "https://api-v1.cortexdb.ai",
        "CORTEXDB_API_KEY": "<from .env - do not commit>",
        "CORTEXDB_ACTOR": "<from .env>",
        "CORTEXDB_SCOPE": "<from .env>",
        "CORTEXDB_HARNESS": "claude-desktop",
        "CORTEXDB_TIMEOUT": "45",
        "CORTEXDB_WAIT": "indexed",
        "CORTEXDB_MCP_BIN": "/opt/homebrew/bin/cortexdb-mcp",
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

For a shared brain, put env from `.env` into the cortexdb server block. Generate JSON with a local script that reads `.env` — do not echo values to chat. Keep the Desktop config mode 0600 if it holds secrets.

If the file already has other `mcpServers`, merge; do not wipe unrelated servers.

## 5. Labels and lanes

- Claude Desktop: MCP memory_store / get_context / memory_search — label **`harness:claude-desktop`**
- Claude Code (sibling pack): label `harness:claude-code` — different config path
- Grok Bot (sibling pack): HTTP scripts/harness.py — label `harness:grokbot`
- Cursor (sibling pack): label `harness:cursor`

Default read: broad recall (no label filter). Optionally filter by harness label when looking for one harness.

Hard rules for the agent using Desktop (state in the first Desktop chat if helpful):
1. CortexDB is memory of record (not chat history).
2. On tasks that need memory: MCP get_context / memory_search before acting.
3. After durable work: MCP memory_store including harness:claude-desktop.
4. Never invent REST signatures; use llms.txt / manifest / docs.
5. Never signup over a working shared identity.
6. Never print tokens.

## 6. Reload Desktop (required)

Claude Desktop does not hot-reload MCP config.

1. **Cmd+Q** Claude Desktop (fully quit — not just close the window).
2. Reopen Claude Desktop.
3. Start a **new chat**.
4. Enable the **cortexdb** connector / MCP server for that chat if the UI asks.

## 7. Prove it (basic smoke)

1. In the new Desktop chat with cortexdb enabled: call health_check; memory_store an onboard one-liner that includes harness:claude-desktop; then get_context or memory_search for that line.
2. Optional shell check after sourcing the shared env file: cortexdb recall filtered by labels=harness:claude-desktop for the onboard text.

Report: Desktop config path; command used (direct binary path); shared vs minted; whoami caller (no token); smoke summary.

## 8. Out of basic scope

- Forced interceptor (rules are soft)
- Separate docs-search MCP not shipped
- Dedicated answer MCP tool is REST-only today
- Full customer AGENTS.md app pack
- Past Claude Desktop transcript ingest
- Project-scoped Desktop MCP (Desktop is user-global config only)

## Do not

- Put secrets in chat, git, or replies
- Mint a new identity when SHARE_BRAIN is true
- Use the wrong public package name for the SDK
- Keep a legacy MCP build that 404s on tools
- Point Desktop at `~/.claude.json` (that is Claude Code)
- Prefer traced Python wrappers for Desktop — they wedge the app
- Claim recall works without the smoke

## Sibling

Claude Code pack lives next door in ClaudeCode with CLAUDE-CODE-ONBOARDING.md. Cursor and Grokbot packs are siblings too.
