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
  <a href="LICENSE">MIT</a>
</p>

---

## What tuckit is

**tuckit is a project board that people and coding agents share.** You open it
in a browser. Your agent reaches the same workspace over MCP. There is one
database and no sync step, so whichever side you look at is current.

The board has three nouns:

- An **Area** is a long-lived responsibility, such as backend or billing.
- A **Slice** is the one unit of work, and it always lives in an Area. It
  carries its spec (what we are building and why), its constraints (what a
  later agent must not get wrong), its decisions (how it was decided, in
  prose), and two fields that settle it: a **done_when** — what somebody would
  have to observe to call it finished — and the **evidence** of what was
  actually observed.
- A **Capture** is an unjudged note: a title and prose, and nothing else, and
  it is what the Inbox holds. Nobody has decided it is work yet, so it has no
  done_when to miss and no stage to be behind on. It leaves the Inbox one of
  two ways and they cost the same: promote it into an Area, where it becomes a
  Slice keeping its number, or dismiss it. Neither one deletes anything.

There is no step layer. Nobody read one, and a plan that nobody reads is a
third copy of the spec.

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
session-end hook turns each one into a capture in the Inbox, so a discovery
outlives the window it was made in — and it lands there as a note, not as work
somebody has to pretend was decided.

**"Done" stops being an opinion.** The done_when is written before the code,
so it is a target the work can miss. The board will not open the ship button
until somebody has written down what they saw — it cannot run your tests, but it
can refuse to let the claim go unmade.

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
| **Antigravity CLI** | One command, then `/mcp` | Bundled. `/mcp` authorizes it in your browser once, with no token to paste. |

**Every install ships the same payload:** the session-start primer, a one-line
reminder on each request that work goes on the board before it goes in the
code, the session-end write-back reminder, the `tuckit-domain` reference skill,
and all of the workflow skills described below. Claude Code additionally gets a
`reconciling-the-board` skill, which you can also invoke by name to reconcile
mid-session.

The per-request reminder is what makes the rest of it fire. A session-start
primer lands once and then competes, thirty turns later, with an instruction
from three lines ago — and loses. Antigravity gets the same line in its rule
file, because its only pre-turn event cannot carry text that survives the
turn.

## Before you start

1. **A tuckit workspace.** Sign up at [app.tuckit.dev](https://app.tuckit.dev).
2. **Python 3** on your `PATH`. The hooks run a small, dependency-free script.
   There is nothing to `pip install`.
3. **Your MCP URL**, only if yours differs from the default. On tuckit Cloud it
   is `https://app.tuckit.dev/mcp` and you need nothing here.
   Claude Code authorizes in your browser on first use; Antigravity authorizes
   when you run `/mcp`. Codex reads a token from an environment variable, which
   you can generate in tuckit under **Settings > Access tokens**.

## Install

### Claude Code

In a Claude Code session:

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
```

When the plugin enables, it **wires up the MCP connection for you**, so there is
no separate `claude mcp add` to run. The URL is prefilled to tuckit Cloud, so
press Enter to accept it, or type your own if yours differs. On first tool use,
Claude Code opens your browser to **authorize once via OAuth**. There is no
token to paste, and the credential is stored in your OS keychain and refreshed
automatically.

That one install gives you the primer, the write-back reminder, the
`tuckit-domain` skill, **every workflow skill in this repository**, the
`reconciling-the-board` skill, and a live tuckit MCP connection.

<details>
<summary>Options and troubleshooting</summary>

- **Not on GitHub, or working from a clone?** `/plugin marketplace add` also
  takes a git URL or a local path, for example
  `/plugin marketplace add ./tuckit-plugins`.
- **Scripted, with no prompt?** On tuckit Cloud you need nothing extra, because
  the URL defaults in and OAuth runs on first use. A different URL is passed in:
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

- **Pointing at a different workspace?** The bundled URL defaults to
  `https://app.tuckit.dev/mcp`. Change it by editing `url`
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

That installs the rules file, the `Stop` hook, the `tuckit-domain` skill,
**every workflow skill in this repository**, and the tuckit MCP server. There is
no `mcp_config.json` edit to make.

Then authorize the server, once:

```
/mcp
```

Approve tuckit in the browser tab it opens. There is no token to paste, and
every later session connects on its own — this is a one-time step, not a
per-session one.

**Do not skip it.** Until the server is authorized, Antigravity has no live
connection to it, so the board is absent from the agent's tool surface rather
than reported as broken. What you see is an agent that goes looking for another
way in: reading the plugin directory, defining a subagent, checking whether
`tuckit` is a command on your `PATH`. To confirm it worked, ask a new session
what the state of the project is; it should answer from `get_project_state`
without touching the filesystem.

> **Point at the plugin directory, not the repository root.** Given a bare repo
> URL, `agy plugin install` treats `plugins/` as a bulk directory and installs
> the Claude Code plugin too. Both declare the name `tuckit`, so they land in
> the same directory and their `hooks.json` files get merged. The merged file is
> then rejected whole, leaving you with no hooks at all.

Antigravity has no `SessionStart`, and the pre-turn event it does have can
inject only an `ephemeralMessage` — a transient step the model stops seeing
almost immediately. So the orientation ships as `rules/AGENTS.md`, which agy
loads for as long as the plugin is enabled, and which also spells out how a
tool is called here (`call_mcp_tool`, since agy does not bind MCP tools as
functions). `Stop` stays a hook and carries the write-back reminder, which is
why the agent takes one extra turn the first time it tries to finish.

<details>
<summary>Options and troubleshooting</summary>

- **Working from a clone?** `agy plugin install` also takes a local directory:
  `agy plugin install ./plugins/antigravity`.
- **Pointing at a different workspace?** Edit `serverUrl` in
  `plugins/antigravity/mcp_config.json` before installing, or configure it
  manually (see [Connecting the MCP by hand](#connecting-the-mcp-by-hand)).
- **Check what is installed:** `agy plugin list`. Turn it off with
  `agy plugin disable tuckit`.
- **Reinstalling?** `agy plugin uninstall tuckit` drops the entry but leaves
  `~/.gemini/config/plugins/tuckit/` on disk. Delete that directory too if you
  want a genuinely clean reinstall.
- **The agent cannot find tuckit?** Check the authorization first: an
  unauthorized server is invisible rather than broken. `agy mcp list` will not
  settle it — that command reads only the global
  `~/.gemini/config/mcp_config.json` and never shows a server a plugin
  provides, so `No MCP servers configured` is not evidence of anything. Run
  `/mcp` instead.
- **Nothing seems to happen?** The install output is not evidence. It prints
  `hooks : 2 processed` for a file it has not parsed yet. The real parse happens
  when the next session starts, and a bad file becomes one line in
  `~/.gemini/antigravity-cli/log/cli-*.log`. Look there first.
</details>

---

## The workflow skills

The hooks are ambient, and deliberately thin. Between them the session-start
primer and the session-end nudge are about 170 words, because that text is
injected into **every** session whether or not it touches the board — a session
that never opens tuckit still pays for it. So the hooks say what is true with no
skill loaded (this workspace is tuckit-tracked, read state from tuckit, here is
the skill to use) and nothing else. The substance lives in the skills below,
which load only when they are needed.

The hooks orient the agent and nudge it to write back. The
workflow skills are the other half: they make one unit of work move through
tuckit end to end, so nothing about it ever lives only in a chat log.

Each skill ends by naming the next one, so the chain runs itself. The payoff is
**resumption**: a new session reads the slice's stage and knows what the work
still needs, instead of hunting for the markdown file the last session left
behind.

### Starting with tuckit

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`starting-with-tuckit`** | This project's board has no Areas yet, whether the project is new or already running. | An approved, responsibility-based set of **Areas**, then one first goal or the evidence-backed work already in flight, with specs left empty |

It runs once, before the pipeline. It reads the project and the human's intent,
drafts the whole Area set, and asks only questions whose answers would produce
different responsibility boundaries. The other skills read a slice's `stage`
to know what to do, and at this moment there is no Area for that first slice to
live under. It proposes and waits, because anything it creates unasked is
cleanup somebody does by hand.

### The pipeline

The slice's `stage` names the skill to use next, so there is nothing to choose.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`designing-a-slice`** | An idea, before any code | Each decision as prose in **decisions**, the approved design in the **spec**, the **constraints**, and the **done_when** (`needs_design` → `needs_done_when` → `executing`) |
| **`executing-a-slice`** | There is a target to meet (`executing`) | Decisions made while building, landmines as constraints, deferrals as new slices — and the **evidence** at the end |
| **`delegating-a-slice`** | Same, but the work splits cleanly and you have subagents | Same, driven by a fresh implementer and reviewer per piece |
| **`shipping-a-slice`** | Evidence has been recorded (`ready_to_ship`) | A note with what shipped and, after asking, `status: shipped` |

The done_when is written before the work and the evidence after it, and the
board derives the stage from which of the two is missing. That is the whole
mechanism: the middle of the pipeline asks *how will we know* rather than *how
many steps are left*.

`delegating-a-slice` is where the board pays off. A dispatched subagent gets a
slice ref and reads its own requirements — including the target the branch has
to meet — so there is no brief file to drift from the board.

### Called from inside a step

These have no stage of their own. The review pair is called by a pipeline skill
when it needs a reviewer, while the rest govern *how* you carry out a step you
are already in. You can also invoke any of them directly.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`requesting-a-review`** | Work needs a reviewer's eyes: one piece of a slice mid-flight, a whole branch before merge, or any range you ask about | Nothing directly. It produces findings. |
| **`receiving-a-review`** | Review feedback has arrived, before you implement any of it | Deferred findings are proposed as captures and created once your partner approves the batch, rulings become a note, landmines become constraints |
| **`writing-tests-first`** | Before writing implementation code for a feature or a fix | An agreed exception becomes a line in the slice's constraints |
| **`verifying-before-claiming`** | Before saying anything is done, and to meet the slice's done_when | The **evidence**, which is what opens the ship gate. It also decides whether that claim is honest. |
| **`debugging-systematically`** | A bug, a test failure, anything unexpected, before proposing a fix | The rule becomes a constraint, the session becomes one note, an unrelated bug becomes a capture, and after three failed fixes the architecture conclusion becomes its own slice |
| **`explain-change`** | Someone needs to actually understand a change an agent wrote | Nothing new. It turns a branch, PR or commit range into a self-contained HTML walkthrough that links each slice's recorded intent and ends in a quiz. |

### Keeping the board honest

None of these belongs to one piece of work. The first runs at the end of a
session; the other two every so often.

| Skill | Use it when | What it writes to the board |
|---|---|---|
| **`reconciling-the-board`** | A session that touched the board is ending, or you want the board reconciled right now | Closes what became untrue, notes what you did, and proposes anything new for approval before creating it |
| **`filing-the-inbox`** | Captures are piling up unfiled, or nobody can say what is in the Inbox | Nothing without approval. It proposes, in one batch, which captures are worth doing and where they go, which stay put, and which are dead |
| **`clearing-the-board`** | More open slices than anyone reads: a capped roadmap, or nobody can say what is next | Nothing without approval. It proposes what to close and why, then closes the approved set as `dropped` and records the list and reasons on one slice |

`reconciling-the-board` is what the session-end hook points at — the hook is the
nudge, this is the checklist.

The other two both make a board smaller, so they propose and wait for the same
reason `starting-with-tuckit` does. Run `filing-the-inbox` before
`clearing-the-board`: filing is the judgement that something is worth doing, and
what you file stops being a candidate for closing.

### Reference

| Skill | What it is |
|---|---|
| **`tuckit-domain`** | The domain reference: the Area / Slice model, how to read project state, and how work moves from idea to shipped |

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
only if you would rather set it up yourself. Claude Code
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

The manifests, hooks, and the AGENTS snippet under each `plugins/<agent>/` are
authored in place. Only `content/`, `scripts/emit.py`, and the skills are
generated.

**There are no slash commands.** There was one, `/tuckit-sync`, and it drifted:
it kept telling the agent to capture follow-ups on its own for as long as it
took anyone to notice that the checklist had grown an approval step. It lived
outside `shared/`, so no build and no guard could catch it. Every entry point is
a skill now — one copy, generated into all three agents, invocable by a person
or by the model.

`content/` is capped by a test. It is injected into every session, so words
added there are paid for by sessions that had no use for them; if a hook needs
to say more, that is a signal the material belongs in a skill.

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

