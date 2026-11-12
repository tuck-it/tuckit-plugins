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

## What it does

[tuckit](https://tuckit.dev) is a project board that you and your coding agents
share. You use it in the browser; your agent uses the same board over MCP.

This plugin teaches your agent to work through that board. You decide what gets
built and what "done" means. The agent works out how, builds it, and hands you a
pull request. Everything it decided along the way is written on the board, not
lost in a chat log.

![One agent session: the agent reads project state, briefs you, finishes the launch blocker, saves a TODO it discovered, and raises the one decision it cannot make itself](docs/media/agent-session.gif)

## What a piece of work looks like

1. **You ask.** "Build login."
2. **It asks back, only if the request is vague.** Who is it for, what is in and
   out, what would count as working. Not which library to use.
3. **You approve once.** It shows what it will build and why, and what you would
   see when it is done. That is the only time it waits for you.
4. **It builds.** Before writing code it tells you its plan and keeps going. Each
   choice it makes is recorded on the board, so you can object at any point.
5. **It checks and opens a PR.** It tests what it promised, writes down what it
   actually saw, and opens a pull request.
6. **A teammate reviews and merges.** The board marks the work shipped.

Anything it notices along the way but does not do goes into the board's Inbox as
a note, for you to file or dismiss later.

**Working in a team?** Each person installs the plugin and points it at the same
workspace. An agent claims a piece of work before it starts, and leaves work
someone else has claimed alone.

## Install

You need a tuckit workspace ([app.tuckit.dev](https://app.tuckit.dev)) and
Python 3 on your `PATH`.

### Claude Code

```
/plugin marketplace add tuck-it/tuckit-plugins
/plugin install tuckit@tuckit-plugins
```

Press Enter to accept the default MCP URL. The first time the agent uses the
board, your browser opens to sign in. There is no token to paste.

### Codex CLI

```
codex plugin marketplace add tuck-it/tuckit-plugins
```

Then in a session, `/plugins` → **tuckit** → install → enable. Codex needs a
token, which you create in tuckit under **Settings > Access tokens**:

```bash
export TUCKIT_MCP_TOKEN="<YOUR_TOKEN>"    # add to your shell profile to keep it
```

### Antigravity CLI

```bash
agy plugin install https://github.com/tuck-it/tuckit-plugins/tree/main/plugins/antigravity
```

Then run `/mcp` once and approve tuckit in the browser. Until you do, the agent
cannot see the board at all.

Use the URL above as written. Pointing `agy` at the repository root installs
the Claude Code plugin as well, and the two break each other's hooks.

### Check it works

Start a new session and ask "what's the state of this project?". The agent
should answer from your board.

<details>
<summary>Troubleshooting and other setups</summary>

**Claude Code**
- Working from a clone: `/plugin marketplace add ./tuckit-plugins`.
- Not picked up: `/reload-plugins`, then `/plugin list`.
- Your own MCP URL, without the prompt:
  `claude plugin install tuckit@tuckit-plugins --scope user --config mcp_url="<YOUR_MCP_URL>"`.
- A server you added yourself with `claude mcp add tuckit` takes precedence
  over the plugin's.

**Codex CLI**
- A different workspace URL: edit `url` in `plugins/codex/.mcp.json`.
- Codex has no session-end hook that can reach the model, so the session-start
  text asks it to tidy the board when it finishes.
- The hooks were checked against codex-cli 0.154.0; the bundled `.mcp.json` has
  not been checked the same way.

**Antigravity CLI**
- Working from a clone: `agy plugin install ./plugins/antigravity`.
- A different workspace URL: edit `serverUrl` in
  `plugins/antigravity/mcp_config.json` before installing.
- The agent cannot find tuckit: run `/mcp`. `agy mcp list` does not show
  servers that come from a plugin, so it is no evidence either way.
- A clean reinstall: `agy plugin uninstall tuckit`, then delete
  `~/.gemini/config/plugins/tuckit/`.
- Problems loading hooks show up in `~/.gemini/antigravity-cli/log/cli-*.log`,
  not in the install output.

**Connecting the MCP by hand**
- Claude Code: `claude mcp add --transport http tuckit <YOUR_MCP_URL>`
- Codex, in `~/.codex/config.toml`:
  ```toml
  [mcp_servers.tuckit]
  url = "<YOUR_MCP_URL>"
  bearer_token_env_var = "TUCKIT_MCP_TOKEN"
  ```
- Antigravity, in `~/.gemini/config/mcp_config.json`:
  ```json
  { "mcpServers": { "tuckit": { "serverUrl": "<YOUR_MCP_URL>" } } }
  ```
</details>

## The skills

The agent picks the right one on its own. You can also call any of them by name.

| Skill | When it runs |
|---|---|
| **`starting-with-tuckit`** | Once, when your board is empty. Proposes the first Areas and work for you to approve. |
| **`designing-a-slice`** | A new request. Turns it into something you approve: what, why, and how you would know it is done. |
| **`building-a-slice`** | Builds what you approved, checks it, and opens the PR. Marks it shipped after the merge. |
| **`reviewing-a-change`** | Gets a second agent to review the branch, and handles review comments. |
| **`reconciling-the-board`** | End of a session. Tidies the work you hold and asks before adding anything new. |
| **`tending-the-board`** | When the Inbox or the board has piled up. Proposes what to file or close, in one list. |
| **`tuckit-domain`** | Reference for how the board works. |

The plugin also adds short hooks: a note at the start of each session that this
project is tracked in tuckit, and a one-line reminder on each request to put
work on the board before changing code.

## Coming from Superpowers?

Some of these skills started as forks of
[Superpowers](https://github.com/obra/superpowers) (MIT; see [NOTICE](NOTICE)).
The difference is that designs and decisions go on the board instead of into
markdown files, and you are asked to approve far less. Use this plugin instead
of Superpowers, not alongside it: both try to handle the same requests.

## Contributing

Edit `shared/` only. Everything under `plugins/<agent>/` except each agent's
manifest and hooks is generated from it. After a change:

```bash
python3 scripts/build.py         # regenerate plugins/<agent>/
python3 -m pytest                # tests, including that the build is current
python3 scripts/check_drift.py   # shared content may name only get_project_state
```

Do not write counts in prose ("seven skills"); they go wrong silently the next
time something is added.

## License

MIT. See [LICENSE](LICENSE).
