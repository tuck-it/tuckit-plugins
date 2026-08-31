# This workspace is tracked in tuckit

tuckit holds this project's decisions, its roadmap and its deferred work. The
codebase is the truth about what the software is today; tuckit is the record of
what was decided and when — a snapshot, not a standing instruction. Neither
answers the other's question. A design that also lives in a markdown file is a second copy, and the
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
