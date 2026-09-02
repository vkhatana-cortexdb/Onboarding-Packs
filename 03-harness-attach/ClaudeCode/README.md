# For you (the human) — Claude Code pack

Give **this whole folder** to Claude Code, or to any agent that can edit files where Claude Code runs.

```
Personal-Brain/handoff/ClaudeCode/
```

One-liner:

> Read `CLAUDE-CODE-ONBOARDING.md` in this folder and run it. CortexDB folder: `<path or omit>`. Share existing brain: `<yes + .env path | no, mint new>`.

## What you do

1. Send this `ClaudeCode/` folder.
2. Share an existing CortexDB `.env` brain, or allow a new 7-day anonymous tenant (new brain, not a merge).
3. Restart Claude Code after MCP changes.
4. Approve installs if asked.

## Basic install

- `cortexdb-mcp` >= 0.6.0 (prefer 0.7.1)
- `~/.claude.json` `mcpServers` memory MCP (not ~/.claude/mcp.json)
- `~/.claude/CLAUDE.md` recall → act → memory_store
- Smoke: health_check, store, recall

## Do not send

`.env`, tokens, or `secrets/`.

## After

Ask Claude Code to call `health_check`, `get_context` for harness:claude-code, then `memory_store` a one-liner.

Sibling: `../Grokbot/`.
