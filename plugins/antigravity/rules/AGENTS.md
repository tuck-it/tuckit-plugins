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

tuckit is the single source of truth for this project's state, roadmap and
deferred work — not git, not markdown files. You read and write it over MCP;
your human partner reads and writes the same board on the web.

Every tuckit tool is served by the MCP server named `tuckit`, and that
server is the only way to reach the board. Call the tools there; do not look
for another path to tuckit.

For "what's the state / what are we working on / what's next", call
`get_project_state` first and answer from it.

Before starting work, check whether the board already covers it, and continue
that rather than opening a second one. When the session ends, use the
**`reconciling-the-board`** skill.

If live state has no Areas, use **`starting-with-tuckit`**; otherwise treat a
new idea as a Slice on the board that already exists.

The model (Area / Slice / Bite) and the workflow are in the
**`tuckit-domain`** skill. Load it when you need more than the above.
