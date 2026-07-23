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

Antigravity references the plugin's script by absolute path, so clone it
somewhere stable. Below, `__REPO__` means that clone's absolute path (e.g.
`/Users/you/code/tuckit-plugins`). Claude Code and Codex install from their own
marketplaces and manage their own copy — neither needs `__REPO__`.

```bash
git clone https://github.com/tuck-it/tuckit-plugins.git
cd tuckit-plugins && pwd    # <- this absolute path is your __REPO__
```

---

## Install per agent

### Claude Code

The Claude Code plugin lives in `plugins/claude/`; the repo root holds the
`.claude-plugin/marketplace.json` that points at it. Hooks reference bundled
files via `${CLAUDE_PLUGIN_ROOT}`, so there is **no path to edit**.

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
/reload-plugins
```

On enable, the plugin **prompts you for your tuckit MCP URL and API token** and
wires the MCP connection for you — so there is **no separate `claude mcp add`
step**. The token is stored in your OS keychain, never in this repo. (Find the
URL and token in tuckit under **Settings → API tokens / MCP snippet**.)

- `/plugin marketplace add` also accepts a full git URL or a local path
  (`/plugin marketplace add ./tuckit-plugins`) if you cloned it or it isn't on
  GitHub yet.
- Non-interactive (skips the prompt):
  ```bash
  claude plugin install tuckit@tuckit-plugins --scope user \
    --config mcp_url="<YOUR_MCP_URL>" --config mcp_token="<YOUR_TOKEN>"
  ```
  (`--scope project` writes it into the repo's `.claude/settings.json` for the
  whole team; `--scope local` is just you in this repo.)
- Confirm with `/plugin list`. Hooks activate automatically for the scope you
  installed — there is no separate trust step.
- Already ran `claude mcp add tuckit …` yourself? That keeps working — a manually
  added server takes precedence over the plugin's, so the two never conflict.

You get: the session-start primer, the session-end write-back reminder, the
`tuckit-domain` skill, the `/tuckit-sync` command, **and the tuckit MCP
connection** — all from one install.

### Codex CLI

Install from the marketplace — no path editing:

```
codex plugin marketplace add tuck-it/tuckit-plugins
```

Then in a Codex session open the plugin browser and install `tuckit`:

```
/plugins
```

Select **tuckit**, install, and enable it. This wires a `session_start` hook
(primer) and a `stop` hook (write-back); the plugin bundles the `tuckit-domain`
skill. Optionally paste `plugins/codex/AGENTS.snippet.md` into your `AGENTS.md`
for a standing reinforcement.

> The Codex plugin's hook schema and the `${PLUGIN_ROOT}` path are written to
> Codex's documented plugin format but not yet verified against a live Codex
> install. If the primer/write-back don't fire after install, check your Codex
> version's plugin docs and adjust `plugins/codex/hooks/hooks.json`.

### Antigravity CLI

1. Copy the hook config into your workspace:

   ```bash
   mkdir -p .agents
   cp __REPO__/plugins/antigravity/.agents/hooks.json .agents/hooks.json
   sed -i '' "s|__REPO__|$(cd __REPO__ && pwd)|g" .agents/hooks.json   # macOS; GNU sed drops the ''
   ```

2. Copy the domain skill into your workspace skills:

   ```bash
   mkdir -p .agents/skills
   cp -R __REPO__/plugins/antigravity/skills/tuckit-domain .agents/skills/
   ```

Antigravity has no `SessionStart` event, so the primer is wired on
`PreInvocation` with a first-turn guard (it injects once per session, not every
turn); `Stop` carries the write-back reminder.

> The Antigravity hook schema, `Stop` semantics, and the session-id field name on
> hook stdin here are best-effort from Antigravity's docs. Verify them against
> your version — if the primer repeats every turn or the write-back never fires,
> adjust `plugins/antigravity/.agents/hooks.json` (and, for the session id, the
> key list in `shared/scripts/emit.py`'s `extract_session_id`, then re-run
> `scripts/build.py`).

---

## Connect tuckit (MCP)

tuckit's MCP endpoint is authenticated per user, so no credentials are ever
committed here — you supply your own workspace URL and API token.

- **Claude Code:** already handled — the plugin prompts for the URL and token on
  enable and wires the MCP for you (see [Claude Code](#claude-code) above). Only
  register it manually if you want a different scope or skipped the prompt:
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

### Layout

```
shared/                 authored single source (edit here)
├─ content/*.md         primer / writeback / domain text
├─ scripts/emit.py      the hook emitter
└─ skills/…/SKILL.md    skill body, with a {{ROOT}} path token
plugins/<agent>/        self-contained, installable payload per agent
├─ claude/  codex/  antigravity/
scripts/                dev tooling (not shipped)
├─ build.py             fan shared/ out into each plugins/<agent>/
└─ check_drift.py       content must name only get_project_state
```

Each agent installs a self-contained copy, so `content/`, `scripts/emit.py`, and
the skill under `plugins/<agent>/` are **generated** from `shared/` — never edit
them by hand. The per-agent static files (manifests, hooks, commands, the AGENTS
snippet) are authored in place.

**After editing anything under `shared/`, run the build and commit the result:**

```bash
python3 scripts/build.py         # regenerate all three plugins/<agent>/ payloads
python3 -m pytest                # emitter, build, manifest, and drift-guard tests
python3 scripts/check_drift.py   # verify content names only get_project_state (needs ../tuckit)
```

The build tests fail if any generated payload has drifted from `shared/`, so a
forgotten `build.py` run cannot slip through CI.
