# tuckit domain reference

tuckit is the single source of truth (SSOT) for a product's state, roadmap, and
deferred work. The human reads and writes it on the web dashboard; you read and
write the same workspace over MCP. One database, no sync step — whichever one
you look at is current, so keeping your writes on the board is what keeps it
honest.

## Vocabulary

- **Area** — a long-lived responsibility domain (backend, frontend, infra…).
  Areas rarely change; they hold slices.
- **Slice** — the one unit of work. It carries:
  - `spec` — the design doc. Empty means it has not been designed yet.
  - `constraints` — what you must not get wrong: landmines, invariants, and
    what "done" means. Read this before you touch anything.
  - `area` — where it belongs. **Empty means it is still in the Inbox** — the
    idea is captured but not yet filed. Setting an area files it; clearing the
    area sends it back. Both directions are reversible.
- **Bite** — one implementation step under a slice.

There is no Ticket and no Plan. An untriaged capture is a slice with no area.

A slice also carries two axes that answer different questions, and conflating
them is a bug:

- `status` — the decision a human made: `open`, `shipped`, `dropped`.
  Nothing derives it; nothing else should set it.
- `stage` — what the slice needs next, derived from its own content (see
  "Reading state" below). You never set this — write the spec, add the
  constraints, check off bites, and it follows.

## Reading state (don't scan git)

Start every "where are we" question with `get_project_state` — it returns each
Area's shipped / roadmap breakdown, the Inbox count, and your identity,
instead of you scanning markdown or git history.

For a single slice, read its **derived stage** to know what it needs next
without opening every child:

- `needs_design` — spec is empty; it needs a design.
- `needs_steps` — has a design but no bites.
- `executing` — has bites, some unfinished.
- `ready_to_ship` — all bites done.
- `shipped` / `dropped` — terminal, mirrors `status` once a human has decided.

To learn where work stands, read `stage`. Do not infer progress from
`status` — `status` only ever records the open/shipped/dropped decision.

## The workflow (how work moves)

1. A raw idea or request → capture as a **Slice with no area** (the Inbox).
2. When it's worth doing → file it into an **Area** (this is reversible;
   clearing the area sends it back to the Inbox).
3. Design it → the slice's **spec** (moves it past `needs_design`).
4. Break it down → **Bites** (moves it through `needs_steps` → `executing`).
5. Do it → update **Bite** statuses as you go (toward `ready_to_ship`).
6. Ship it → advance the slice to shipped.

Anything decided for "later" belongs on the board too — a committed next step
as a Slice filed into an Area, a vaguer idea as a Slice left in the Inbox (no
area). If it's only in the chat, it will be lost.

## Tools

The exact MCP tool names and their arguments are whatever the tuckit server
exposes in this session — treat that list as authoritative and discover tools
there. This document intentionally names only `get_project_state`, the stable
entry point, so it can't fall out of date.
