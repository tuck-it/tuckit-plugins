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
