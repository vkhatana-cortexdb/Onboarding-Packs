# For you (the human) — Cursor pack

Give **this whole folder** to Cursor Agent / Cursor CLI, or to any agent that can edit files on the machine where Cursor runs.

```
Personal-Brain/handoff/Cursor/
```

Optional one-liner:

> Read `CURSOR-ONBOARDING.md` in this folder and run it. CortexDB folder: `<path or omit>`. Share my existing brain: `<yes + path to .env | no, mint new>`.

## What you do

1. Send this `Cursor/` folder (path on disk is enough).
2. Decide identity:
   - **Share an existing CortexDB brain** (recommended if Personal-Brain / Grok / Claude Code already use one): name the folder with a complete `.env`.
   - **Fresh eval brain**: omit the path; agent may mint a 7-day anonymous tenant (a **new** brain).
3. Reload Cursor MCP (Settings → MCP, or restart Cursor) after `~/.cursor/mcp.json` changes.
4. Approve installs if asked.

## What gets installed (basic version)

- `cortexdb-mcp` ≥ 0.6.0 (prefer 0.7.1)
- User-global `~/.cursor/mcp.json` → CortexDB memory tools
- User-global or project `.cursor/rules/cortexdb.mdc` → recall first, act, then `memory_store`
- Optional project `.mcp.json` (gitignored)
- Smoke: health / recall / store / recall

## Do not send

`.env`, tokens, or `secrets/`.

## After it works

In Cursor chat (or Cursor CLI / agent), ask:

> Use CortexDB MCP: `health_check`, then `get_context` for harness:cursor, then `memory_store` a one-liner with harness:cursor.

Sibling packs: `../Grokbot/`, `../ClaudeCode/`.
