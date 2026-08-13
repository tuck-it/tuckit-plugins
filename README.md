# tuckit-plugins

**Make your AI coding agent treat tuckit as the single source of truth for your
project — so your board never goes stale.**

Once installed, the plugin quietly does two things every session:

- **At the start**, it orients your agent on tuckit — "read the live project
  state with `get_project_state`, not git, and reconcile with the board before
  you begin."
- **At the end**, it nudges the agent to *write back*: turn "let's do X next"
  decisions into Slices (filed into an Area, or left in the Inbox), check off
  finished work, and leave notes — so nothing important lives only in a chat
  log.

Works with **Claude Code**, **Codex CLI**, and **Antigravity CLI**.

---

## At a glance

| Agent | How you install | MCP connection |
|---|---|---|
| **Claude Code** | 2 slash commands | ✅ **Automatic** — URL is prefilled; you authorize once in your browser (OAuth), no token to paste |
| **Codex CLI** | Marketplace add + `/plugins` | ✅ **Automatic** — bundled; you just set one env var |
| **Antigravity CLI** | Copy 2 files | ⚙️ **Manual** — add tuckit to your MCP config (auto-bundling is coming) |

Everyone gets: the **session-start primer**, the **session-end write-back
reminder**, the **`tuckit-domain` skill**, and the **workflow skills**
below. Claude Code also gets a **`/tuckit-sync`** command to reconcile the board
mid-session.

---

## Before you start

1. **Python 3** on your `PATH`. The hooks run a tiny, dependency-free script —
   nothing to `pip install`.
2. **Your tuckit MCP URL** — only if you self-host. On tuckit Cloud the URL is
   already the default (`https://app.tuckit.dev/mcp`), so you need nothing here.
   - **Claude Code** authorizes in your browser (OAuth) on first use — no token
     to prepare or paste.
   - **Codex** still reads a token from an env var; grab it in tuckit under
     **Settings → API tokens / MCP snippet**.

---

## Install

### Claude Code — fully automatic 🎉

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
```

When the plugin enables, it **wires up the MCP connection for you** — **no
separate `claude mcp add` needed**. The URL is prefilled to tuckit Cloud (just
press Enter; self-hosters type their own). On first tool use, Claude Code opens
your browser to **authorize once via OAuth** — there's no token to paste, and
the credential is stored in your OS keychain and auto-refreshed.

That's it. From this one install you get the primer, the write-back reminder,
the `tuckit-domain` skill, the `/tuckit-sync` command, **and a live tuckit MCP
connection**.

<details>
<summary>Options &amp; troubleshooting</summary>

- **Not on GitHub / working from a clone?** `/plugin marketplace add` also takes
  a git URL or a local path, e.g. `/plugin marketplace add ./tuckit-plugins`.
- **Scripted / no prompt?** On tuckit Cloud you need nothing extra — the URL
  defaults in and OAuth runs on first use. Self-hosters pass their URL:
  ```bash
  claude plugin install tuckit@tuckit-plugins --scope user \
    --config mcp_url="<YOUR_MCP_URL>"
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

## The workflow skills

The hooks are ambient — they orient the agent and nudge it to write back. The
workflow skills are the other half: they make one unit of work move through
tuckit end to end, so nothing about it ever lives only in a chat log.

### The pipeline skills

The slice's `stage` names the skill to use next, so there is nothing to choose.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`designing-a-slice`** | An idea, before any code | Resolves or creates the slice, then writes the approved design into its **spec** |
| **`breaking-down-a-slice`** | The spec is approved (`needs_steps`) | The **constraints**, then an ordered **bite** checklist |
| **`executing-a-slice`** | There are bites to do (`executing`) | Each bite's status as it happens; deferrals become new slices |
| **`delegating-a-slice`** | Same, but the bites are mostly independent and you have subagents | Same, driven by a fresh implementer and reviewer per bite |
| **`shipping-a-slice`** | The checklist is empty (`ready_to_ship`) | A note with what shipped, and — after asking — `status: shipped` |

### The service skills

These have no stage of their own: the review pair is *called* by a pipeline
skill when it needs a reviewer, while the other three govern *how* you carry
out a step you're already in — and you can call any of them directly too.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`requesting-a-review`** | Work needs a reviewer's eyes — one bite, a whole branch before merge, or any range you ask about | Nothing directly; it produces findings |
| **`receiving-a-review`** | Review feedback has arrived, before you implement any of it | Deferred findings become Inbox slices; rulings become a note; landmines become constraints |
| **`writing-tests-first`** | Before writing implementation code for a feature or a fix | An agreed exception becomes a line in the slice's constraints |
| **`verifying-before-claiming`** | Before saying anything is done — including before ticking a bite | Nothing new; it decides whether the tick is honest |
| **`debugging-systematically`** | A bug, a test failure, anything unexpected — before proposing a fix | The rule becomes a constraint, the session becomes one note, an unrelated bug becomes an Inbox slice, and after three failed fixes the architecture conclusion becomes its own slice |

`delegating-a-slice` is where the board pays off twice: a dispatched subagent
gets a slice ref and a bite id and reads its own requirements, so there is no
brief file to drift from the board — and bite status *is* the progress ledger,
so a controller that lost its place after a compaction reads the board instead
of re-dispatching work that is already done.

Each one ends by naming the next, so the chain runs itself. The payoff is
**resumption**: a new session reads the slice's stage and knows where the work
is, instead of hunting for the markdown file the last session left behind.

### Relationship to Superpowers

These are forks of ten [Superpowers](https://github.com/obra/superpowers)
skills (MIT — see [NOTICE](NOTICE)): `brainstorming`, `writing-plans`,
`executing-plans`, `subagent-driven-development`,
`finishing-a-development-branch`, `requesting-code-review`,
`receiving-code-review`, `test-driven-development`, `systematic-debugging` and
`verification-before-completion`. They keep upstream's form — the checklists you must
materialise as tasks, the task template, the placeholder ban, the self-reviews,
the fix loop and its breaker, the rationalization tables — and change one thing: **every artifact lands on the board instead of in `docs/`.**
No design file, no plan file, no task briefs, no progress ledger.

**They are a replacement, not a supplement.** Run this plugin *instead of*
Superpowers, not alongside it: with both enabled, `designing-a-slice` and
`brainstorming` compete for the same trigger, and whichever wins decides
whether your design ends up somewhere the next session can find it.

The trade is honest, so here it is plainly: Superpowers still ships two layers
this plugin does not have — using-git-worktrees and dispatching-parallel-agents.
Those are being forked next; everything else Superpowers covers, this plugin
now covers too.

---

## Connecting the MCP by hand

Claude Code and Codex wire the MCP for you (above). Use these only for
Antigravity, for self-hosting, or if you'd rather set it up yourself. Claude
Code authorizes via browser OAuth (no token); for Codex and Antigravity your
workspace token lives in tuckit under **Settings → API tokens / MCP snippet** —
no credentials are ever committed to this repo.

- **Claude Code** — OAuth is auto-detected; no token needed:
  ```bash
  claude mcp add --transport http tuckit <YOUR_MCP_URL>
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
and the skills are generated.

Two guards pull in opposite directions on purpose: `content/` may name **only**
`get_project_state`, because that prose has to survive the tool catalog
changing, while the skills name tools outright — a skill that says "discover the
tools yourself" cannot drive a pipeline. `tests/test_skill_tools.py` is the
trade: every tool a skill names is checked against the live catalog in
`../tuckit`, and adding a new one means listing it there first.

**After editing anything in `shared/`, rebuild and verify:**

```bash
python3 scripts/build.py         # regenerate all three plugins/<agent>/ payloads
python3 -m pytest                # emitter, build, manifest, and drift-guard tests
python3 scripts/check_drift.py   # content must name only get_project_state (needs ../tuckit)
```

The build tests fail if any generated payload drifts from `shared/`, so a
forgotten `build.py` run can't slip through.

## License

MIT — see [LICENSE](LICENSE). The plugins are deliberately permissive so they
can be vendored into any agent toolchain.

The tuckit server they talk to is a separate project under the
[Business Source License 1.1](https://github.com/tuck-it/tuckit/blob/main/LICENSE).
BSL is source-available rather than OSI open source: you can read the code and
run it in production, including self-hosting it for your own organisation. The
one thing it withholds is offering tuckit to third parties as a hosted or
managed service. On 2030-07-10 it converts to Apache 2.0.
