# tuckit

These rules apply when this workspace is connected to a tuckit board — that is,
when the `tuckit` MCP server is available. If it is not, ignore them.

## Reaching the board

Antigravity does not bind MCP tools as callable functions. Every tuckit tool
goes through the generic dispatcher:

```
call_mcp_tool(ServerName="tuckit", ToolName="get_project_state", Arguments={})
```

That is how you call every tool a tuckit skill names — `get_project_state`,
`list_areas`, `list_slices`, `create_slice`, `update_slice`, `add_note`, and the
rest. Each tool's argument schema is cached at
`~/.gemini/antigravity-cli/mcp/tuckit/<tool>.json`; read one when you need the
exact parameters.

That server is the only way in. There is no tuckit command on PATH and no file
in the plugin directory that reads or writes the board, so do not go looking for
one: a board you cannot reach over MCP is a board you cannot reach at all. Say
so rather than working around it.

---

# This workspace is tracked in tuckit

tuckit holds this project's decisions, its roadmap and its deferred work. The
codebase is the truth about what the software is today; tuckit is the truth
about why it is that way and what is still owed. Neither answers the other's
question. A design that also lives in a markdown file is a second copy, and the
copy is the one that goes stale.

You read and write the board over MCP; your human partner reads and writes the
same board on the web. Every tuckit tool is served by the MCP server named
`tuckit`, and that server is the only way to reach it.

For "what's the state / what are we working on / what's next", call
`get_project_state` first and answer from it.

Work enters through the board. Before you change code, find the slice this
belongs to or create one, and take anything you would have to think about
first through **`designing-a-slice`**.

If live state has no Areas, use **`starting-with-tuckit`**. When the session
ends, use **`reconciling-the-board`**.

The model (Area / Slice / Bite) and the workflow are in the **`tuckit-domain`**
skill.

---

Board check: find the tuckit slice this belongs to, or create one, before you
change code. Undesigned work goes through **`designing-a-slice`** first; a
one-line spec is enough for a small fix. Ignore this if the request is not work.
