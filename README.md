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
| **Antigravity CLI** | 1 command | ✅ **Automatic** — bundled; you authorize once in your browser (OAuth), no token to paste |

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
   - **Claude Code** and **Antigravity** authorize in your browser (OAuth) on
     first use — no token to prepare or paste.
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

### Antigravity CLI — one command

```bash
agy plugin install https://github.com/tuck-it/tuckit-plugins/tree/main/plugins/antigravity
```

That installs the skills, the hooks, **and the tuckit MCP server** — no
`mcp_config.json` edit needed. On first tool use Antigravity opens your browser
to **authorize once via OAuth**; there's no token to paste.

> **Point at the plugin directory, not the repository root.** `agy plugin
> install <repo URL>` treats `plugins/` as a bulk directory and installs the
> Claude Code plugin too. Both declare the name `tuckit`, so they land in the
> same directory and their `hooks.json` files are *merged* — and the merged
> file is rejected whole, leaving you with no hooks at all.

Antigravity has no `SessionStart` event, so the primer rides on `PreInvocation`
with a first-turn guard (it injects once per session, not every turn); `Stop`
carries the write-back reminder, which is why the agent takes one extra turn
when it first tries to finish.

<details>
<summary>Options &amp; troubleshooting</summary>

- **Working from a clone?** `agy plugin install` also takes a local directory:
  `agy plugin install ./plugins/antigravity`.
- **Self-hosting tuckit?** Edit `serverUrl` in `plugins/antigravity/mcp_config.json`
  before installing, or configure it manually (see
  [Connecting the MCP by hand](#connecting-the-mcp-by-hand)).
- **Check what's installed:** `agy plugin list`. Turn it off with
  `agy plugin disable tuckit`.
- **Reinstalling?** `agy plugin uninstall tuckit` drops the entry but leaves
  `~/.gemini/config/plugins/tuckit/` on disk. Delete that directory too if you
  want a genuinely clean reinstall.
- **Nothing seems to happen?** The install output is not evidence — it prints
  `hooks : 2 processed` for a file it has not parsed yet. The real parse happens
  when the next session starts, and a bad file becomes one line in
  `~/.gemini/antigravity-cli/log/cli-*.log`. Look there first.
</details>

---

## The workflow skills

The hooks are ambient — they orient the agent and nudge it to write back. The
workflow skills are the other half: they make one unit of work move through
tuckit end to end, so nothing about it ever lives only in a chat log.

### The adoption skill

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`adopting-a-project`** | The workspace is empty and the project is not — you are putting tuckit on something already running | The first **areas**, and a **slice** per piece of work already in flight — specs left empty, evidence in notes |

It runs once, before the pipeline: the other skills read a slice's `stage` to
know what to do, and at this moment there is no board for a stage to live on.
It proposes and waits — tuckit has no delete tool, so anything it creates
unasked is cleanup someone does by hand.

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
the fix loop and its breaker, the rationalization tables — and change one
thing: **the board replaces the markdown files.** Whatever upstream would have
written into `docs/` — a design, a plan, task briefs, a progress ledger — lands
on a slice instead, and the forks that produce no artifact of their own decide
what the others are allowed to claim.

**They are a replacement, not a supplement.** Run this plugin *instead of*
Superpowers, not alongside it: with both enabled, `designing-a-slice` and
`brainstorming` compete for the same trigger, and whichever wins decides
whether your design ends up somewhere the next session can find it.

The trade is honest, so here it is plainly: Superpowers ships fourteen skills
and ten of them are forked here. Four are not. Two are layers this plugin does
not have yet — using-git-worktrees and dispatching-parallel-agents — and they
are being forked next. The other two, using-superpowers and writing-skills, are
Superpowers' own meta-tooling for finding and authoring skills; they have no
counterpart here and none is planned. Every *other* workflow layer Superpowers
covers, this plugin now covers too.

---

## Connecting the MCP by hand

All three plugins wire the MCP for you (above). Use these only for self-hosting,
or if you'd rather set it up yourself. Claude Code and Antigravity authorize via
browser OAuth (no token); for Codex your workspace token lives in tuckit under
**Settings → API tokens / MCP snippet** — no credentials are ever committed to
this repo.

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
- **Antigravity** — add to `~/.gemini/config/mcp_config.json`; OAuth runs in
  your browser on first use, so there is no token to put here:
  ```json
  { "mcpServers": { "tuckit": { "serverUrl": "<YOUR_MCP_URL>" } } }
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
