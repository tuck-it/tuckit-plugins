# You are working in a tuckit-tracked workspace

tuckit is the single source of truth (SSOT) for this project's state, roadmap,
and deferred work. It is read and written by both the human (web dashboard) and
you (MCP tools).

## Read state from tuckit, not from git

For any "what's the state / what are we working on / what's the roadmap"
question, call the `get_project_state` MCP tool FIRST. Do not answer from
`git log` or by scanning files — git is *code* history; tuckit is *project*
state.

## The shape of the board

- **Area** — a long-lived responsibility domain (e.g. backend, frontend).
- **Slice** — one deliverable unit of work in an Area (a spec plus a checklist
  of bites).
- **Plan** / **Bite** — a Slice's implementation plan and its steps.
- **Ticket** — a quick capture in the Inbox for triage.

## Before you start: reconcile with the board

Before doing work, check whether a Slice or Ticket already covers it. If one
does, continue that one. If none does, create it first. Doing work the board
doesn't know about is exactly what makes the board go stale.

## When you finish: reconcile again

Before ending, make sure what you did — and anything you decided to do *next* —
is on the board.

The exact set of tools is whatever the tuckit MCP server exposes; discover it
there rather than assuming a fixed list.
