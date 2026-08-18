<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/media/wordmark-dark.png">
    <img src="docs/media/wordmark.png" alt="tuckit" width="170">
  </picture>
</p>

<h1 align="center">tuckit-plugins</h1>

<p align="center">
  Put your coding agent on the same project board you read.<br>
  Claude Code, Codex CLI and Antigravity CLI.
</p>

<p align="center">
  <a href="https://tuckit.dev">Website</a> &middot;
  <a href="https://docs.tuckit.dev">Docs</a> &middot;
  <a href="https://app.tuckit.dev">Get a workspace</a> &middot;
  <a href="https://github.com/tuck-it/tuckit">Server source</a> &middot;
  <a href="LICENSE">MIT</a>
</p>

---

## What tuckit is

**tuckit is a project board that people and coding agents share.** You open it
in a browser. Your agent reaches the same workspace over MCP. There is one
database and no sync step, so whichever side you look at is current.

The board has three nouns:

- An **Area** is a long-lived responsibility, such as backend or billing.
- A **Slice** is the one unit of work. It carries its spec (what we are building
  and why), its constraints (what a later agent must not get wrong), and a
  checklist. A slice that has no area yet is sitting in the Inbox.
- A **Bite** is one step on that checklist.

## What this repository is

The agent half. It is the plugin you install into your coding agent so that the
agent joins that board instead of working beside it.

A single install gives you three things:

1. **A live MCP connection** to your tuckit workspace, wired up for you. There
   is no separate server to register.
2. **Two hooks.** One orients the agent at the start of every session. The other
   reminds it to write back before it stops.
3. **A set of workflow skills** that carry one piece of work from idea to
   shipped, writing each artifact onto the board rather than into a markdown
   file the next session will never find.

## What it looks like

![One agent session: the agent reads project state, briefs you, finishes the launch blocker, saves a TODO it discovered, and raises the one decision it cannot make itself](docs/media/agent-session.gif)

One session, start to finish. The agent reads the project before it does
anything, tells you where things stand, does the work, files what it discovered
along the way, and hands back the decision that was never its to make.

## What changes once it is installed

**You stop re-briefing.** A session opens with the agent reading live project
state instead of inferring it from `git log`. You give it the goal. It already
knows which slice covers that goal, what was decided about it, and what the last
session left unfinished.

**Discoveries stop dying in the transcript.** An agent fixing one thing notices
three others. Normally those live in a scrollback nobody reopens. The
session-end hook turns them into Inbox slices, so a discovery outlives the
window it was made in.

**Losing context stops losing your place.** Bite status is the progress ledger
and it lives on the server, not in the conversation. An agent that gets
compacted mid-slice reads the board and picks up where it stopped, instead of
redoing steps that are already done.

**You can see the project without reading a chat log.** What the agent did, what
it decided, and what it is waiting on you for are all on a board with a web UI.
Checking progress stops meaning reading transcripts.

**Your agents stop disagreeing about the state.** Claude Code on your laptop,
Codex in another terminal, and a teammate's session all read and write one
workspace. This is shared project state, not per-agent memory.

## At a glance

| Agent | How you install | MCP connection |
|---|---|---|
| **Claude Code** | Two slash commands | Wired by the plugin. You authorize once in your browser (OAuth), with no token to paste. |
| **Codex CLI** | Marketplace add, then `/plugins` | Bundled. You set one environment variable. |
| **Antigravity CLI** | One command | Bundled. You authorize once in your browser (OAuth), with no token to paste. |

**Every install ships the same payload:** the session-start primer, the
session-end write-back reminder, the `tuckit-domain` reference skill, and all of
the workflow skills described below. Claude Code additionally gets a
`/tuckit-sync` command for reconciling the board mid-session.

## Before you start

1. **A tuckit workspace.** Sign up at [app.tuckit.dev](https://app.tuckit.dev),
   or [self-host the server](https://github.com/tuck-it/tuckit).
2. **Python 3** on your `PATH`. The hooks run a small, dependency-free script.
   There is nothing to `pip install`.
3. **Your MCP URL**, only if you self-host. On tuckit Cloud the default
   (`https://app.tuckit.dev/mcp`) is already correct, so you need nothing here.
   Claude Code and Antigravity authorize in your browser on first use. Codex
   reads a token from an environment variable, which you can generate in tuckit
   under **Settings > Access tokens**.

## Install

### Claude Code

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
```

When the plugin enables, it **wires up the MCP connection for you**, so there is
no separate `claude mcp add` to run. The URL is prefilled to tuckit Cloud, so
press Enter to accept it, or type your own if you self-host. On first tool use,
Claude Code opens your browser to **authorize once via OAuth**. There is no
token to paste, and the credential is stored in your OS keychain and refreshed
automatically.

That one install gives you the primer, the write-back reminder, the
`tuckit-domain` skill, **every workflow skill in this repository**, the
`/tuckit-sync` command, and a live tuckit MCP connection.

<details>
<summary>Options and troubleshooting</summary>

- **Not on GitHub, or working from a clone?** `/plugin marketplace add` also
  takes a git URL or a local path, for example
  `/plugin marketplace add ./tuckit-plugins`.
- **Scripted, with no prompt?** On tuckit Cloud you need nothing extra, because
  the URL defaults in and OAuth runs on first use. Self-hosters pass their URL:
  ```bash
  claude plugin install tuckit@tuckit-plugins --scope user \
    --config mcp_url="<YOUR_MCP_URL>"
  ```
  (`--scope project` shares it with your team through `.claude/settings.json`.
  `--scope local` keeps it to just you in this repo.)
- **Did not pick up right away?** Run `/reload-plugins`, then confirm with
  `/plugin list`.
- **Already ran `claude mcp add tuckit` yourself?** That is fine. A manually
  added server takes precedence over the plugin's, so the two never conflict.
</details>

### Codex CLI

Add the marketplace, then install `tuckit` from the in-session browser:

```
codex plugin marketplace add tuck-it/tuckit-plugins
```
```
/plugins      -> select "tuckit" -> install -> enable
```

This wires the primer, the write-back reminder, the `tuckit-domain` skill,
**every workflow skill in this repository**, and the tuckit MCP server. There is
no `~/.codex/config.toml` edit to make.

Codex does not prompt during install, so give it your token through the
environment variable the bundled server reads:

```bash
export TUCKIT_MCP_TOKEN="<YOUR_TOKEN>"    # add to your shell profile to keep it
```

<details>
<summary>Options and troubleshooting</summary>

- **Self-hosting tuckit?** The bundled URL defaults to the hosted app
  (`https://app.tuckit.dev/mcp`). Point it at your own server by editing `url`
  in `plugins/codex/.mcp.json`, or configure it manually (see
  [Connecting the MCP by hand](#connecting-the-mcp-by-hand)).
- Your token is never committed. Codex reads it from `TUCKIT_MCP_TOKEN` each
  time it connects.
- Want a standing nudge in every session? Paste
  `plugins/codex/AGENTS.snippet.md` into your `AGENTS.md`.

> **Heads-up:** the Codex plugin (its hooks and bundled `.mcp.json`) follows
> Codex's documented format but has not been verified against a live Codex
> install yet. If the primer, the write-back, or the MCP do not come up, check
> your Codex version's docs and adjust `plugins/codex/hooks/hooks.json` or
> `plugins/codex/.mcp.json`.
</details>

### Antigravity CLI

```bash
agy plugin install https://github.com/tuck-it/tuckit-plugins/tree/main/plugins/antigravity
```

That installs the hooks, the `tuckit-domain` skill, **every workflow skill in
this repository**, and the tuckit MCP server. There is no `mcp_config.json` edit
to make. On first tool use Antigravity opens your browser to **authorize once
via OAuth**, so there is no token to paste.

> **Point at the plugin directory, not the repository root.** Given a bare repo
> URL, `agy plugin install` treats `plugins/` as a bulk directory and installs
> the Claude Code plugin too. Both declare the name `tuckit`, so they land in
> the same directory and their `hooks.json` files get merged. The merged file is
> then rejected whole, leaving you with no hooks at all.

Antigravity has no `SessionStart` event, so the primer rides on `PreInvocation`
behind a first-turn guard, injecting once per session rather than every turn.
`Stop` carries the write-back reminder, which is why the agent takes one extra
turn the first time it tries to finish.

<details>
<summary>Options and troubleshooting</summary>

- **Working from a clone?** `agy plugin install` also takes a local directory:
  `agy plugin install ./plugins/antigravity`.
- **Self-hosting tuckit?** Edit `serverUrl` in
  `plugins/antigravity/mcp_config.json` before installing, or configure it
  manually (see [Connecting the MCP by hand](#connecting-the-mcp-by-hand)).
- **Check what is installed:** `agy plugin list`. Turn it off with
  `agy plugin disable tuckit`.
- **Reinstalling?** `agy plugin uninstall tuckit` drops the entry but leaves
  `~/.gemini/config/plugins/tuckit/` on disk. Delete that directory too if you
  want a genuinely clean reinstall.
- **Nothing seems to happen?** The install output is not evidence. It prints
  `hooks : 2 processed` for a file it has not parsed yet. The real parse happens
  when the next session starts, and a bad file becomes one line in
  `~/.gemini/antigravity-cli/log/cli-*.log`. Look there first.
</details>

---

## The workflow skills

The hooks are ambient. They orient the agent and nudge it to write back. The
workflow skills are the other half: they make one unit of work move through
tuckit end to end, so nothing about it ever lives only in a chat log.

Each skill ends by naming the next one, so the chain runs itself. The payoff is
**resumption**: a new session reads the slice's stage and knows where the work
is, instead of hunting for the markdown file the last session left behind.

### Starting from an existing project

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`adopting-a-project`** | The workspace is empty and the project is not. You are putting tuckit on something already running. | The first **areas**, and a **slice** per piece of work already in flight, with specs left empty and evidence in notes |

It runs once, before the pipeline. The other skills read a slice's `stage` to
know what to do, and at this moment there is no board for a stage to live on. It
proposes and waits, because tuckit has no delete tool, so anything it creates
unasked is cleanup somebody does by hand.

### The pipeline

The slice's `stage` names the skill to use next, so there is nothing to choose.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`designing-a-slice`** | An idea, before any code | Resolves or creates the slice, then writes the approved design into its **spec** |
| **`breaking-down-a-slice`** | The spec is approved (`needs_steps`) | The **constraints**, then an ordered **bite** checklist |
| **`executing-a-slice`** | There are bites to do (`executing`) | Each bite's status as it happens. Deferrals become new slices. |
| **`delegating-a-slice`** | Same, but the bites are mostly independent and you have subagents | Same, driven by a fresh implementer and reviewer per bite |
| **`shipping-a-slice`** | The checklist is empty (`ready_to_ship`) | A note with what shipped and, after asking, `status: shipped` |

`delegating-a-slice` is where the board pays off twice. A dispatched subagent
gets a slice ref and a bite id and reads its own requirements, so there is no
brief file to drift from the board. And because bite status *is* the progress
ledger, a controller that lost its place after a compaction reads the board
instead of re-dispatching work that is already done.

### Called from inside a step

These have no stage of their own. The review pair is called by a pipeline skill
when it needs a reviewer, while the rest govern *how* you carry out a step you
are already in. You can also invoke any of them directly.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`requesting-a-review`** | Work needs a reviewer's eyes: one bite, a whole branch before merge, or any range you ask about | Nothing directly. It produces findings. |
| **`receiving-a-review`** | Review feedback has arrived, before you implement any of it | Deferred findings become Inbox slices, rulings become a note, landmines become constraints |
| **`writing-tests-first`** | Before writing implementation code for a feature or a fix | An agreed exception becomes a line in the slice's constraints |
| **`verifying-before-claiming`** | Before saying anything is done, including before ticking a bite | Nothing new. It decides whether the tick is honest. |
| **`debugging-systematically`** | A bug, a test failure, anything unexpected, before proposing a fix | The rule becomes a constraint, the session becomes one note, an unrelated bug becomes an Inbox slice, and after three failed fixes the architecture conclusion becomes its own slice |
| **`explain-change`** | Someone needs to actually understand a change an agent wrote | Nothing new. It turns a branch, PR or commit range into a self-contained HTML walkthrough that links each slice's recorded intent and ends in a quiz. |

### Reference

| Skill | What it is |
|---|---|
| **`tuckit-domain`** | The domain reference: the Area / Slice / Bite model, how to read project state, and how work moves from idea to shipped |

### Relationship to Superpowers

Several of these skills are forks of
[Superpowers](https://github.com/obra/superpowers) skills (MIT).
[NOTICE](NOTICE) lists exactly which ones and is the file to trust; this section
explains what the fork changed rather than repeating the list.

The forks keep upstream's form: the checklists you must materialise as tasks,
the task template, the placeholder ban, the self-reviews, the fix loop and its
breaker, the rationalization tables. They change one thing. **The board replaces
the markdown files.** Whatever upstream would have written into `docs/`, whether
a design, a plan, task briefs or a progress ledger, lands on a slice instead.
The forks that produce no artifact of their own decide what the others are
allowed to claim.

**They are a replacement, not a supplement.** Run this plugin *instead of*
Superpowers, not alongside it. With both enabled, `designing-a-slice` and
`brainstorming` compete for the same trigger, and whichever wins decides whether
your design ends up somewhere the next session can find it.

Some upstream layers have no counterpart here. `using-git-worktrees` and
`dispatching-parallel-agents` are being forked next. `using-superpowers` and
`writing-skills` are Superpowers' own meta-tooling for finding and authoring
skills; nothing here corresponds to them and nothing is planned.

---

## Connecting the MCP by hand

All three plugins wire the MCP for you, as described above. Use this section
only for self-hosting, or if you would rather set it up yourself. Claude Code
and Antigravity authorize through browser OAuth, so they need no token. For
Codex, your workspace token lives in tuckit under **Settings > Access tokens**.
No credentials are ever committed to this repository.

- **Claude Code.** OAuth is auto-detected, so there is no token to supply:
  ```bash
  claude mcp add --transport http tuckit <YOUR_MCP_URL>
  ```
- **Codex.** Add to `~/.codex/config.toml`, keeping the token in an env var:
  ```toml
  [mcp_servers.tuckit]
  url = "<YOUR_MCP_URL>"
  bearer_token_env_var = "TUCKIT_MCP_TOKEN"
  ```
- **Antigravity.** Add to `~/.gemini/config/mcp_config.json`. OAuth runs in your
  browser on first use, so there is no token to put here:
  ```json
  { "mcpServers": { "tuckit": { "serverUrl": "<YOUR_MCP_URL>" } } }
  ```

---

## For contributors

`shared/` is the **one place you edit**. Each agent installs a self-contained
copy, so the per-agent payloads are generated from it. Never hand-edit the
generated files.

```
shared/                 authored single source (edit here)
├─ content/*.md         primer / writeback / domain text
├─ scripts/emit.py      the hook emitter
└─ skills/<name>/SKILL.md    skill body, with a {{ROOT}} path token
plugins/<agent>/        self-contained, installable payload per agent
├─ claude/  codex/  antigravity/
scripts/                dev tooling (not shipped in any plugin)
├─ build.py             fan shared/ out into each plugins/<agent>/
└─ check_drift.py       content must name only get_project_state
docs/media/             README artwork and the demo recording
```

The manifests, hooks, commands, and the AGENTS snippet under each
`plugins/<agent>/` are authored in place. Only `content/`, `scripts/emit.py`,
and the skills are generated.

Two guards pull in opposite directions on purpose. `content/` may name **only**
`get_project_state`, because that prose has to survive the tool catalog
changing, while the skills name tools outright: a skill that says "discover the
tools yourself" cannot drive a pipeline. `tests/test_skill_tools.py` is the
trade. Every tool a skill names is checked against the live catalog in
`../tuckit`, and adding a new one means listing it there first.

**After editing anything in `shared/`, rebuild and verify:**

```bash
python3 scripts/build.py         # regenerate every plugins/<agent>/ payload
python3 -m pytest                # emitter, build, manifest, and drift-guard tests
python3 scripts/check_drift.py   # content must name only get_project_state (needs ../tuckit)
```

The build tests fail if any generated payload drifts from `shared/`, so a
forgotten `build.py` run cannot slip through.

### House style

Two rules, both learned the hard way:

1. **Do not count things in prose.** A sentence saying how many skills exist
   goes quietly wrong the next time one is added, and it has already gone wrong
   here more than once. Name things, or point at the file that lists them.
2. **Do not make absolute scope claims.** "Everything else is covered" is a
   sentence a single new upstream skill turns into a lie.

## License

MIT. See [LICENSE](LICENSE). The plugins are deliberately permissive so they can
be vendored into any agent toolchain.

The tuckit server they talk to is a separate project under the
[Business Source License 1.1](https://github.com/tuck-it/tuckit/blob/main/LICENSE).
BSL is source-available rather than OSI open source: you can read the code and
run it in production, including self-hosting it for your own organisation. The
one thing it withholds is offering tuckit to third parties as a hosted or
managed service. On 2030-07-10 it converts to Apache 2.0.
