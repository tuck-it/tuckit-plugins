---
name: designing-a-slice
description: "Use before any creative work in a tuckit-tracked workspace — a new feature, a component, a behavior change, anything not yet designed. Turns an idea into an approved design written into the slice's spec. In this workspace it replaces superpowers:brainstorming: same dialogue, but the design lands on the board instead of a markdown file."
---

# Designing a Slice

Turn an idea into a design the next session can pick up. The dialogue is the one
you would have anyway; what changes is where it lands — the slice's `spec`, not
a file under `docs/`. A file is read by whoever knows to look for it. A spec is
read by anyone who opens the board, and by every agent that reads the slice
before touching the code.

Vocabulary and stages: `__REPO__/plugins/antigravity/content/domain.md`.

<HARD-GATE>
Do not write code, scaffold anything, or invoke an implementation skill until
you have presented a design and the user has approved it. Every project,
regardless of how simple it looks. "Simple" is where unexamined assumptions do
the most damage. The design can be three sentences — it still gets presented.
</HARD-GATE>

## 0. Resolve the slice before you ask the first question

1. Search the board — the idea may already be captured, often months ago and
   better phrased than the request you just got. `list_slices(query=…)` searches
   the whole org; `list_slices(area_id='')` is the Inbox specifically. Look at
   both: unfiled captures are the easiest to miss and usually the oldest.
2. If a slice covers this, use it. Say which one, by ref.
3. If none does, `create_slice(title=…)` **now**, with an **empty spec**.
   - An empty spec is not laziness — it reads back as stage `needs_design`,
     which is the board saying *someone is designing this right now*.
   - Do not pre-fill the spec with the raw request. Undesigned work that looks
     designed is worse than an empty field.
   - File it into an area if it obviously belongs to one; otherwise leave the
     area empty and it waits in the Inbox. Both directions are reversible, so
     this is not a decision worth stalling on.

Step 0 is first because a design conversation that dies before step 5 leaves
nothing behind otherwise — and because work the board does not know about is
exactly what makes the board stale.

## 1. Explore the context

Read project state from tuckit (`get_project_state`), then the code: the files
this would touch, recent commits in that area, existing conventions. Check
whether a neighbouring slice already owns part of this — overlapping designs are
cheaper to find now than to merge later.

## 2. Ask questions, one at a time

One question per message. Prefer multiple choice; open-ended is fine when it has
to be. You are after purpose, constraints, and what success looks like — not
implementation detail yet.

**Scope check.** If the request is several independent subsystems, say so
immediately instead of refining the details of something that needs splitting
first. Decompose into sibling slices, then design the first one. One slice
carries one design and one checklist — that is a structural boundary, not a
style preference (see `breaking-down-a-slice`).

## 3. Propose 2–3 approaches

With trade-offs, lead with your recommendation and say why. YAGNI ruthlessly:
strip anything from each approach that this slice does not need.

## 4. Present the design in sections

Sections scaled to their complexity, approval per section. Revise and re-present
until the user approves — no silent redesign after a "yes".

## 5. Write the approved design into the slice

`update_slice(slice_id=…, spec=<the design>)`. Markdown; headings and tables
render.

- **`spec`** answers *what we are building and why*.
- **`constraints`** is a different field and a different reader: what a later
  agent must not get wrong — landmines, invariants, and what "done" actually
  means. If the design surfaced one of those, write it there, not buried in the
  spec's prose. `constraints` is what gets read by someone who will not read the
  whole design.
- Keep out anything that should not live in a tracker (credentials, endpoints
  with secrets in them).
- **One home.** If a repo convention wants a design file in git, make that file
  a pointer to the slice ref. A second copy of a design is a second thing to
  keep true, and it is always the one that goes stale.

## 6. Read it back, then let the user read it

`get_slice(<ref>)` and read what actually rendered. Check for placeholders you
meant to fill, contradictions between sections, scope that crept in, and prose
that is really a constraint in disguise. Fix inline.

Then ask the user to review the spec **as it now reads on the board** — not as
you described it in chat.

## 7. Terminal state

Invoke `breaking-down-a-slice`. That is the only skill you invoke from here — no
implementation skill, no code, no scaffolding.

## Resuming a half-finished design

A session that died mid-design left a slice at `needs_design` with whatever spec
it had. Pick that slice up at step 1. Do not create a second one for the same
idea.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `brainstorming`, rewritten
so the design lands on the board.
