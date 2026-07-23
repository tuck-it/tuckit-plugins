# tuckit-plugins

Domain-knowledge plugins that make AI coding agents treat **tuckit** as your
project's single source of truth: they orient the agent on tuckit at session
start and remind it to write its work — and any "do it next" decisions — back to
the board at session end.

Supported agents: **Claude Code**, **Codex CLI**, **Antigravity CLI**.

## Requirements

- Python 3 on your PATH (the hooks run a small, dependency-free script).
- tuckit's MCP endpoint registered with your agent (see "Connect tuckit (MCP)").

## Install

Clone this repo somewhere stable and note its path (referred to below as
`__REPO__`):

```bash
git clone https://github.com/tuck-it/tuckit-plugins.git
```

### Claude Code

The repo root is a Claude Code plugin. Add it to a marketplace / plugin config
so `.claude-plugin/plugin.json` is loaded. Hooks reference bundled files via
`${CLAUDE_PLUGIN_ROOT}`, so no path editing is needed.

### Codex CLI

Copy `codex/hooks.json` into your project's `.codex/hooks.json` (or merge into
`~/.codex/config.toml` `[hooks]`), and replace `__REPO__` with the absolute
clone path. Optionally paste `codex/AGENTS.snippet.md` into your `AGENTS.md`.

### Antigravity CLI

Copy `antigravity/.agents/hooks.json` into your project's `.agents/hooks.json`
and replace `__REPO__` with the absolute clone path. Copy
`antigravity/skills/tuckit-domain/` into your `.agents/skills/`.

## Connect tuckit (MCP)

tuckit's MCP endpoint is authenticated per user — register it yourself; this
plugin never bundles credentials.

- Claude Code: `claude mcp add --transport http tuckit <YOUR_MCP_URL> --header "Authorization: Bearer <TOKEN>"`
- Codex: add tuckit under `[mcp_servers]` in `~/.codex/config.toml`.
- Antigravity: add tuckit to `mcp_config.json`.

## What it does

- **Session start** — injects a short primer: read state via `get_project_state`
  (not git), the Area/Slice/Plan/Bite/Ticket shape, and "reconcile with the
  board before you start."
- **Session end** — reminds once per session to write back: capture next/deferred
  decisions as planned Slices or Tickets, file follow-ups, check off Bites, leave
  notes, advance finished slices.
- **On demand** — a `tuckit-domain` skill (deep-dive) and, on Claude Code, a
  `/tuckit-sync` command to reconcile the board mid-session.

## Development

```bash
python -m pytest              # unit tests for the emitter, manifests, drift guard
python3 scripts/check_drift.py  # verify content names only get_project_state (needs ../tuckit)
```
