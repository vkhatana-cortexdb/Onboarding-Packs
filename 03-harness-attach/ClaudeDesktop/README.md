# For you (the human) — Claude Desktop pack

Give **this whole folder** to an agent that can edit files on the Mac where Claude Desktop runs.

```
Personal-Brain/handoff/ClaudeDesktop/
```

One-liner:

> Read `CLAUDE-DESKTOP-ONBOARDING.md` in this folder and run it. CortexDB folder: `<path or omit>`. Share existing brain: `<yes + .env path | no, mint new>`.

## What you do

1. Send this `ClaudeDesktop/` folder.
2. Share an existing CortexDB `.env` brain, or allow a new 7-day anonymous tenant (new brain, not a merge).
3. After config edit: **Cmd+Q** Claude Desktop fully, reopen, start a **new chat**, enable the `cortexdb` connector.
4. Approve installs if asked.

## Basic install

- `cortexdb-mcp` >= 0.6.0 (prefer 0.7.1), on PATH as `/opt/homebrew/bin/cortexdb-mcp`
- Config: `~/Library/Application Support/Claude/claude_desktop_config.json` → `mcpServers`
- Prefer **direct binary** (`command` = `/opt/homebrew/bin/cortexdb-mcp`, `args` = `[]`). Traced Python wrappers have wedged Desktop.
- Smoke: health_check, store, recall — label `harness:claude-desktop`

## Not Claude Code

Claude **Code** uses `~/.claude.json` `mcpServers`. Claude **Desktop** uses `claude_desktop_config.json`. Do not mix them.

## Do not send

`.env`, tokens, or `secrets/`.

## After

Ask Claude Desktop (new chat, connector on) to call `health_check`, `get_context` for harness:claude-desktop, then `memory_store` a one-liner.

Sibling: `../ClaudeCode/`, `../Cursor/`, `../Grokbot/`.
