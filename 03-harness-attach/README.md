# 03 — Attach chat / IDE / Grok to an existing brain

Point Claude Code, Cursor, or Grok Bot at a **working** CortexDB identity (shared Personal-Brain preferred). No new product UI — harness packs only.

## Packs

| Folder | Harness | Entry |
|---|---|---|
| **`Grokbot/`** | Grok Bot (HTTP helper) | `GROKBOT-ONBOARDING.md` |
| **`ClaudeCode/`** | Claude Code MCP | `CLAUDE-CODE-ONBOARDING.md` |
| **`Cursor/`** | Cursor MCP + rules | `CURSOR-ONBOARDING.md` |

## Claude Code note

User-global MCP is **`~/.claude.json`** → `mcpServers` (not `~/.claude/mcp.json`). Prefer `type=stdio` with `/opt/homebrew/bin/python3` and `args` for `cortexdb-mcp` / `-m cortexdb_mcp` or a traced wrapper.

## Audience

- **Vibe coders** and **agent operators** who already have a brain and want recall/write in the tools they live in.
- Prefer shared brain; never mint over a working token.

For app dual-write into a product repo, use `02-app-in-repo/` instead.
