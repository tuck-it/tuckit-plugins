# tuckit-plugins

Domain-knowledge plugins that make AI coding agents treat **tuckit** as your
project's single source of truth: they orient the agent on tuckit at session
start and remind it to write its work — and any "do it next" decisions — back to
the board at session end.

Supported agents: **Claude Code**, **Codex CLI**, **Antigravity CLI**.

## Requirements

- **Python 3** on your `PATH` — the hooks run a small, dependency-free script
  (standard library only, nothing to `pip install`).
- tuckit's **MCP endpoint** registered with your agent (see
  [Connect tuckit (MCP)](#connect-tuckit-mcp)).

## Get the repo

Codex and Antigravity reference the plugin's script by absolute path, so clone it
somewhere stable. Below, `__REPO__` means that clone's absolute path (e.g.
`/Users/you/code/tuckit-plugins`). Claude Code manages its own copy and does not
need `__REPO__`.

```bash
git clone https://github.com/tuck-it/tuckit-plugins.git
cd tuckit-plugins && pwd    # <- this absolute path is your __REPO__
```

---

## Install per agent

### Claude Code

The repo is a Claude Code plugin (its root holds `.claude-plugin/plugin.json` and
a `.claude-plugin/marketplace.json`). Hooks reference bundled files via
`${CLAUDE_PLUGIN_ROOT}`, so there is **no path to edit**.

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
/reload-plugins
```

- `/plugin marketplace add` also accepts a full git URL or a local path
  (`/plugin marketplace add ./tuckit-plugins`) if you cloned it or it isn't on
  GitHub yet.
- Non-interactive equivalent: `claude plugin install tuckit@tuckit-plugins --scope user`
  (`--scope project` writes it into the repo's `.claude/settings.json` for the
  whole team; `--scope local` is just you in this repo).
- Confirm with `/plugin list`. The plugin's hooks activate automatically for the
  scope you installed — there is no separate trust step.

You get: the session-start primer, the session-end write-back reminder, the
`tuckit-domain` skill, and the `/tuckit-sync` command.

### Codex CLI

1. Copy the hook config into your project (or merge it into `~/.codex/config.toml`
   under a `[hooks]` table for all projects):

   ```bash
   mkdir -p .codex
   cp __REPO__/codex/hooks.json .codex/hooks.json
   ```

2. Replace the `__REPO__` placeholder inside it with your clone's absolute path:

   ```bash
   sed -i '' "s|__REPO__|$(cd __REPO__ && pwd)|g" .codex/hooks.json   # macOS
   # GNU sed: sed -i "s|__REPO__|/abs/path/tuckit-plugins|g" .codex/hooks.json
   ```

3. (Optional) Paste `__REPO__/codex/AGENTS.snippet.md` into your project's
   `AGENTS.md` for a standing reinforcement of the same guidance.

This wires a `SessionStart` hook (primer) and a `Stop` hook (write-back).

> The Codex hook-config schema and `Stop` payload fields here are written to
> Codex's documented format. If your Codex version ignores the file or the
> write-back doesn't surface, check its hooks docs and adjust `codex/hooks.json`
> accordingly.

### Antigravity CLI

1. Copy the hook config into your workspace:

   ```bash
   mkdir -p .agents
   cp __REPO__/antigravity/.agents/hooks.json .agents/hooks.json
   sed -i '' "s|__REPO__|$(cd __REPO__ && pwd)|g" .agents/hooks.json   # macOS; GNU sed drops the ''
   ```

2. Copy the domain skill into your workspace skills:

   ```bash
   mkdir -p .agents/skills
   cp -R __REPO__/antigravity/skills/tuckit-domain .agents/skills/
   ```

Antigravity has no `SessionStart` event, so the primer is wired on
`PreInvocation` with a first-turn guard (it injects once per session, not every
turn); `Stop` carries the write-back reminder.

> The Antigravity hook schema, `Stop` semantics, and the session-id field name on
> hook stdin here are best-effort from Antigravity's docs. Verify them against
> your version — if the primer repeats every turn or the write-back never fires,
> adjust `antigravity/.agents/hooks.json` (and, for the session id, the key list
> in `scripts/emit.py`'s `extract_session_id`).

---

## Connect tuckit (MCP)

tuckit's MCP endpoint is authenticated per user — register it yourself with your
own workspace URL and API token. This plugin never bundles credentials.

- **Claude Code:**
  ```bash
  claude mcp add --transport http tuckit <YOUR_MCP_URL> \
    --header "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Codex:** add tuckit under `[mcp_servers]` in `~/.codex/config.toml`:
  ```toml
  [mcp_servers.tuckit]
  url = "<YOUR_MCP_URL>"
  headers = { Authorization = "Bearer <YOUR_TOKEN>" }
  ```
- **Antigravity:** add tuckit to your `mcp_config.json`:
  ```json
  { "mcpServers": { "tuckit": { "serverUrl": "<YOUR_MCP_URL>",
      "headers": { "Authorization": "Bearer <YOUR_TOKEN>" } } } }
  ```

Find your workspace's MCP URL and token in tuckit under **Settings → API tokens /
MCP snippet**.

---

## What it does

- **Session start** — injects a short primer: read state via `get_project_state`
  (not git), the Area/Slice/Plan/Bite/Ticket shape, and "reconcile with the board
  before you start."
- **Session end** — reminds once per session to write back: capture next/deferred
  decisions as planned Slices or Tickets, file follow-ups, check off Bites, leave
  notes, advance finished slices.
- **On demand** — a `tuckit-domain` skill (deep-dive) and, on Claude Code, a
  `/tuckit-sync` command to reconcile the board mid-session.

## Development

```bash
python3 -m pytest                # emitter, manifest, and drift-guard tests
python3 scripts/check_drift.py   # verify content names only get_project_state (needs ../tuckit)
```
