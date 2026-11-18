---
name: designing-a-slice
description: "Use before building anything in a tuckit-tracked workspace that has no approved promise yet (stage needs_design, needs_done_when or needs_approval): a new feature, a behavior change, a vague request like 'build login'. Questions the request until it can be written as a spec and a done_when, records the designer's approval, then designs the work and records each choice as a decision."
---

# Designing a Slice

The person agrees **what** and **how anyone would know it is done**. You decide
**how**. Get the first two out of them with as few questions as possible, put
them in front of them once, record their yes, and then get out of their way.

Reference: `${PLUGIN_ROOT}/content/domain.md`, including how to write for the board.

## 1. Find or take the slice

Search first: `list_slices(query=…)` for slices and `list_captures()` for the
Inbox, which is a different set.

- **A slice covers it.** If `get_slice` shows someone else on the `Assignee:`
  line, say who and stop. Otherwise take it with `save_slice(assignee="me")`.
- **A capture covers it.** `triage_capture(<capture_id>, "promote",
  area_id=<area>)`, then take the new slice.
- **Nothing covers it.** `save_slice(title=…, area_id=…, assignee="me")` with an
  empty spec. Pick the Area from `list_areas()`; it is reversible, so do not
  stall on it.

## 2. Look before you ask

Read `get_project_state`, the code the work would touch, and any slice that
already owns part of it. Many questions answer themselves, and the rest get
sharper. If the request is really several independent pieces, say so and split
it into sibling slices; design the first one.

## 3. Question the request until it is a promise

Ask only what would change the promise:

- **Scope**: what is in, and what is explicitly out.
- **Who it is for**: which user, in which situation.
- **What success looks like**: the observation that would settle it, and where.

Do not ask how to build it. Ask one or two questions at a time with your best
guess attached, so a "yes" is a full answer. Stop as soon as you can write both
halves. A specific request may need no questions.

## 4. Get the promise approved

Write both halves with `save_slice(spec=…, done_when=…)`. The stage reads
`needs_approval`, which is the truth: written, not agreed. Then show both in the
conversation, written the way the board needs them (a teammate who never saw
this conversation should understand them), and ask for one approval. This is
the only place this skill waits.

On a yes, `approve_promise(slice_id, kind="designer")`. It records who approved
and when, and moves the stage to `executing`. Never call it to get past the
gate without that yes.

If they change the wording, save the new text and ask again. If the promise has
to change after approval, editing it clears the approval on its own; ask again.

If someone else will build it, stop here: leave the slice unassigned (or hand
it to them) and say so. The approval tells the builder whom to ask.

## 5. Design it, show it, keep going

Read the code and decide how to build it. Record each real choice as you reach
it with `append_decision(slice_id, body)`:

```
**Chose a text field on Slice.**

One field and one migration. Turned down a separate model: queryable, but a
new noun on the board that nobody has asked to query.
Leans on nobody needing to search decisions across slices.
```

Then send the design summary as its own message (the shape of the change, the
files it touches, the close calls) and start **`building-a-slice`** without
waiting for a reply. The summary is there so the person can object while it is
cheap. If they object, follow them and append a decision saying what they
overrode and why.

Landmines and invariants go in `constraints`. If this slice cannot meet its own
done_when until another ships, `link_slices` with a `blocks` note that says
why; "it would be more natural first" is not a block.

## The small lane

A typo, a version bump, a copy fix, a one-line change with one obvious way to
do it. Create and take the slice, write a one-line spec and done_when,
`approve_promise(slice_id, kind="self")`, say in one line which slice it is and
that you took the small lane, and build it. If you can name a choice you would
be making on the person's behalf, it is not the small lane.

## Resuming

A slice you hold at `needs_design`, `needs_done_when` or `needs_approval` is a
design that stopped part way. Pick it up where it stopped.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent): `brainstorming`, rewritten so the person approves the promise and the agent owns the design.
