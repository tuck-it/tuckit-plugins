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
- **Slice** — the one unit of work: a spec, constraints, and a checklist of
  Bites. **Empty area means it's still in the Inbox** — filing it into an
  Area (and clearing the area again) is fully reversible. There is no Ticket
  and no Plan.

## Before you start: reconcile with the board

Before doing work, check whether a Slice already covers it — in an Area, or
still in the Inbox with no area. Search before you conclude there is nothing:
by text, and separately through the unfiled captures — the ones with no area,
which are the easiest to miss and usually the oldest. If one covers it, continue that
one. Only if none does, create it. Doing work the board doesn't know about is
what makes the board go stale — and filing a second slice for work it already
knows about is what makes it unreadable.

## When you finish: reconcile again

Before ending, make sure the board reflects what happened: what you did, what
became untrue and can be closed, and — with your human partner's approval —
what should exist and doesn't.

Closing counts as reconciling. The board only gets smaller on purpose.

The exact set of tools is whatever the tuckit MCP server exposes; discover it
there rather than assuming a fixed list.
