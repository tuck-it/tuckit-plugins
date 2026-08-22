# This workspace is tracked in tuckit

tuckit is the single source of truth for this project's state, roadmap and
deferred work — not git, not markdown files. You read and write it over MCP;
your human partner reads and writes the same board on the web.

For "what's the state / what are we working on / what's next", call
`get_project_state` first and answer from it.

Before starting work, check whether the board already covers it, and continue
that rather than opening a second one. When the session ends, use the
**`reconciling-the-board`** skill.

The model (Area / Slice / Bite) and the workflow are in the
**`tuckit-domain`** skill. Load it when you need more than the above.
