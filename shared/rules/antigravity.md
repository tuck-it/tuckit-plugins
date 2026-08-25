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
