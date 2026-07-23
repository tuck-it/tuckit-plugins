# tuckit-plugins

**Make your AI coding agent treat tuckit as the single source of truth for your
project — so your board never goes stale.**

Once installed, the plugin quietly does two things every session:

- **At the start**, it orients your agent on tuckit — "read the live project
  state with `get_project_state`, not git, and reconcile with the board before
  you begin."
- **At the end**, it nudges the agent to *write back*: turn "let's do X next"
  decisions into planned Slices or Tickets, check off finished work, and leave
  notes — so nothing important lives only in a chat log.

Works with **Claude Code**, **Codex CLI**, and **Antigravity CLI**.

---

## At a glance

| Agent | How you install | MCP connection |
|---|---|---|
| **Claude Code** | 2 slash commands | ✅ **Automatic** — prompts for your URL + token, stores the token in your OS keychain |
| **Codex CLI** | Marketplace add + `/plugins` | ✅ **Automatic** — bundled; you just set one env var |
| **Antigravity CLI** | Copy 2 files | ⚙️ **Manual** — add tuckit to your MCP config (auto-bundling is coming) |

Everyone gets: the **session-start primer**, the **session-end write-back
reminder**, and the **`tuckit-domain` skill**. Claude Code also gets a
**`/tuckit-sync`** command to reconcile the board mid-session.

---

## Before you start

1. **Python 3** on your `PATH`. The hooks run a tiny, dependency-free script —
   nothing to `pip install`.
2. **Your tuckit MCP URL and API token.** Find both in tuckit under
   **Settings → API tokens / MCP snippet**. You'll paste them in during install
   (Claude Code) or set them as an env var (Codex).

---

## Install

### Claude Code — fully automatic 🎉

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
```

When the plugin enables, it **asks you for your tuckit MCP URL and API token**,
then wires up the MCP connection for you — **no separate `claude mcp add`
needed**. Your token goes straight into your OS keychain, never into this repo.

That's it. From this one install you get the primer, the write-back reminder,
the `tuckit-domain` skill, the `/tuckit-sync` command, **and a live tuckit MCP
connection**.

<details>
<summary>Options &amp; troubleshooting</summary>

- **Not on GitHub / working from a clone?** `/plugin marketplace add` also takes
  a git URL or a local path, e.g. `/plugin marketplace add ./tuckit-plugins`.
- **Scripted / no prompt?** Pass the values on the command line:
  ```bash
  claude plugin install tuckit@tuckit-plugins --scope user \
    --config mcp_url="<YOUR_MCP_URL>" --config mcp_token="<YOUR_TOKEN>"
  ```
  (`--scope project` shares it with your team via `.claude/settings.json`;
  `--scope local` keeps it to just you in this repo.)
- **Didn't pick up right away?** Run `/reload-plugins`, and confirm with
  `/plugin list`.
- **Already ran `claude mcp add tuckit …` yourself?** No problem — a manually
  added server takes precedence over the plugin's, so the two never conflict.
</details>

### Codex CLI — automatic, with one env var

Add the marketplace, then install `tuckit` from the in-session browser:

```
codex plugin marketplace add tuck-it/tuckit-plugins
```
```
/plugins      → select "tuckit" → install → enable
```

This wires the primer, the write-back reminder, the `tuckit-domain` skill,
**and the tuckit MCP server** — **no `~/.codex/config.toml` edit needed**.

Codex doesn't prompt during install, so give it your token through the
environment variable the bundled server reads:

```bash
export TUCKIT_MCP_TOKEN="<YOUR_TOKEN>"    # add to your shell profile to keep it
```

<details>
<summary>Options &amp; troubleshooting</summary>

- **Self-hosting tuckit?** The bundled URL defaults to the hosted app
  (`https://app.tuckit.dev/mcp`). Point it at your own server by editing `url`
  in `plugins/codex/.mcp.json`, or configure it manually (see
  [Connecting the MCP by hand](#connecting-the-mcp-by-hand)).
- Your token is never committed — Codex reads it from `TUCKIT_MCP_TOKEN` each
  time it connects.
- Want a standing nudge in every session? Paste `plugins/codex/AGENTS.snippet.md`
  into your `AGENTS.md`.

> **Heads-up:** the Codex plugin (hooks + bundled `.mcp.json`) follows Codex's
> documented format but hasn't been verified against a live Codex install yet.
> If the primer, write-back, or MCP don't come up, double-check your Codex
> version's docs and tweak `plugins/codex/hooks/hooks.json` or
> `plugins/codex/.mcp.json`.
</details>

### Antigravity CLI — manual copy

Antigravity references the plugin by absolute path, so first clone this repo
somewhere stable:

```bash
git clone https://github.com/tuck-it/tuckit-plugins.git
cd tuckit-plugins && pwd    # ← copy this absolute path; it's your __REPO__ below
```

Then, in your Antigravity workspace:

```bash
# 1) Hooks (primer + write-back)
mkdir -p .agents
cp __REPO__/plugins/antigravity/.agents/hooks.json .agents/hooks.json
sed -i '' "s|__REPO__|$(cd __REPO__ && pwd)|g" .agents/hooks.json   # macOS; GNU sed: drop the ''

# 2) The tuckit-domain skill
mkdir -p .agents/skills
cp -R __REPO__/plugins/antigravity/skills/tuckit-domain .agents/skills/
```

Antigravity has no `SessionStart` event, so the primer rides on `PreInvocation`
with a first-turn guard (it injects once per session, not every turn); `Stop`
carries the write-back reminder.

**MCP is manual on Antigravity for now** — add tuckit to your MCP config as
shown in [Connecting the MCP by hand](#connecting-the-mcp-by-hand). (Automatic
bundling like Claude Code and Codex is planned, pending live verification that
Antigravity auto-registers a plugin's MCP config.)

<details>
<summary>Heads-up on hook behavior</summary>

> The Antigravity hook schema, `Stop` semantics, and the session-id field name on
> hook stdin are best-effort from Antigravity's docs and not yet verified live.
> If the primer repeats every turn or the write-back never fires, adjust
> `plugins/antigravity/.agents/hooks.json` — and, for the session id, the key
> list in `shared/scripts/emit.py`'s `extract_session_id` (then re-run
> `python3 scripts/build.py`).
</details>

---

## Connecting the MCP by hand

Claude Code and Codex wire the MCP for you (above). Use these only for
Antigravity, for self-hosting, or if you'd rather set it up yourself. Your
workspace URL and token live in tuckit under **Settings → API tokens / MCP
snippet** — no credentials are ever committed to this repo.

- **Claude Code**
  ```bash
  claude mcp add --transport http tuckit <YOUR_MCP_URL> \
    --header "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Codex** — add to `~/.codex/config.toml`, keeping the token in an env var:
  ```toml
  [mcp_servers.tuckit]
  url = "<YOUR_MCP_URL>"
  bearer_token_env_var = "TUCKIT_MCP_TOKEN"
  ```
- **Antigravity** — add to your `mcp_config.json`:
  ```json
  { "mcpServers": { "tuckit": { "serverUrl": "<YOUR_MCP_URL>",
      "headers": { "Authorization": "Bearer <YOUR_TOKEN>" } } } }
  ```

---

## For contributors

`shared/` is the **one place you edit**. Each agent installs a self-contained
copy, so the per-agent payloads are generated from it — never hand-edit the
generated files.

```
shared/                 authored single source (edit here)
├─ content/*.md         primer / writeback / domain text
├─ scripts/emit.py      the hook emitter
└─ skills/…/SKILL.md    skill body, with a {{ROOT}} path token
plugins/<agent>/        self-contained, installable payload per agent
├─ claude/  codex/  antigravity/
scripts/                dev tooling (not shipped in any plugin)
├─ build.py             fan shared/ out into each plugins/<agent>/
└─ check_drift.py       content must name only get_project_state
```

The manifests, hooks, commands, and the AGENTS snippet under each
`plugins/<agent>/` are authored in place; only `content/`, `scripts/emit.py`,
and the skill are generated.

**After editing anything in `shared/`, rebuild and verify:**

```bash
python3 scripts/build.py         # regenerate all three plugins/<agent>/ payloads
python3 -m pytest                # emitter, build, manifest, and drift-guard tests
python3 scripts/check_drift.py   # content must name only get_project_state (needs ../tuckit)
```

The build tests fail if any generated payload drifts from `shared/`, so a
forgotten `build.py` run can't slip through.
