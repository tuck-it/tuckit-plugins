# tuckit

These rules apply when this workspace is connected to a tuckit board — that is,
when the `tuckit` MCP server is available. If it is not, ignore them.

## Reaching the board

Antigravity does not bind MCP tools as callable functions. Every tuckit tool
goes through the generic dispatcher:

```
call_mcp_tool(ServerName="tuckit", ToolName="get_project_state", Arguments={})
```

That is how you call every tool a tuckit skill names: put the tool name the
skill gives you into `ToolName`. The catalog this rule file must not carry is
the one the server itself advertises in this session — treat that list as
authoritative rather than a list written down here, which cannot stay current
when the product renames a tool. Each tool's argument schema is cached at
`~/.gemini/antigravity-cli/mcp/tuckit/<tool>.json`; read one when you need the
exact parameters.

That server is the only way in. There is no tuckit command on PATH and no file
in the plugin directory that reads or writes the board, so do not go looking for
one: a board you cannot reach over MCP is a board you cannot reach at all. Say
so rather than working around it.

---

# This workspace is tracked in tuckit

tuckit holds this project's decisions, its roadmap and its deferred work. The
codebase is the truth about what the software is today; tuckit is the record of
what was decided and when. A design that also lives in a markdown file is a
second copy, and the copy is the one that goes stale.

You read and write the board over MCP, through the server named `tuckit`;
people use the same board on the web.

For "what's the state / what are we working on / what's next", call
`get_project_state` first and answer from it.

Work enters through the board. Before you change code, find the slice this
belongs to or create one in an Area, and take anything without an approved
promise through **`designing-a-slice`**. Someone else's slice is theirs to
build.

People skim the board, so everything you write there is plain and short: one
point per title, no code names. The rules are in **`tuckit-domain`**.

If live state has no Areas, use **`starting-with-tuckit`**. When the session
ends, use **`reconciling-the-board`**.

---

Board check: find or create this work's slice in an Area before you change
code. Work without an approved promise goes through **`designing-a-slice`**
first; a small fix needs only a one-line promise you approve yourself. Ignore
this if it is not work.

Write for a person skimming: give every ref its title, one point per title.
