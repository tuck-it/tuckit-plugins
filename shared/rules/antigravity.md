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
