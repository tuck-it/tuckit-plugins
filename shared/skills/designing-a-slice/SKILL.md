---
name: designing-a-slice
description: "Use before building anything in a tuckit-tracked workspace that has no agreed promise yet — a new feature, a behavior change, a vague request like 'build login'. Questions the request until it can be written as a spec (what and why) and a done_when, gets the designer's one approval on that promise, then designs the work itself and records each choice as a decision."
---

# Designing a Slice

The person agrees **what** and **how anyone would know it is done**. You decide
**how**. This skill gets the first two out of them with as few questions as
possible, puts them in front of them once, and then gets out of their way.

Vocabulary: `{{ROOT}}/content/domain.md`.

Nothing is built before the work exists on the board and its promise is
approved. The small lane below is the one exception to the approval, never to
the board.

## 1. Find or take the slice

Search before creating: `list_slices(query=…)` for slices and `list_captures()`
for the Inbox, which is a different set. The idea may already be on the board.

- **A slice covers it.** Read who holds it. If someone else does, say who and
  stop: it is theirs. Otherwise take it with `save_slice(assignee="me")`.
- **A capture covers it.** `triage_capture(<capture_id>, "promote",
  area_id=<area>)`, then take the new slice.
- **Nothing covers it.** `save_slice(title=…, area_id=…, assignee="me")` with
  an empty spec. Pick the Area from `list_areas()`; it is a reversible choice,
  so do not stall on it.

Name the slice to the person by ref and title.

## 2. Look before you ask

`get_project_state`, then the code the work would touch, its recent commits and
any slice that already owns part of it. Many questions answer themselves here,
and the rest get sharper. Investigation is not design and needs nobody's yes.

If the request covers several independent pieces, say so now and split it into
sibling slices; design the first one.

## 3. Question the request until it is a promise

A vague request ("build login", "make the board faster") cannot be written as a
done_when, so it has to be questioned first. Ask only what would change the
promise:

- **Scope** — what is in, what is explicitly out.
- **Who it is for** — which user, in which situation.
- **What success looks like** — the observation that would settle it, on which
  surface (browser, terminal, production).

Do not ask how to build it. Which library, which table, which component split:
those are yours.

Ask one or two questions at a time, with your best guess attached so a "yes" is
a full answer. Stop as soon as you can write both halves of the promise. A
request that is already specific may need no questions at all.

## 4. Write the promise and get it approved

Write it to the slice first, so the person approves what the board will hold:

- `spec` — what is being built and why, including what is out of scope. No
  implementation detail.
- `done_when` — the observation that settles it. Good ones can fail, name the
  surface, and say what would NOT settle it when there is an obvious wrong
  answer waiting:

  ```
  An expired token returns HTTP 401, not a tool error inside a 200 --
  that status code is the only thing that makes a client refresh.
  ```

Then show both in the conversation and ask for one approval. This is the only
place this skill waits for an answer. The person who approves it owns the
promise.

After approval the spec is not edited again. If the promise has to change
later, that is a new approval, not a quiet edit.

## 5. Design it, show it, keep going

Read the code and decide how to build it. For each real choice,
`append_decision(slice_id, body)`:

```
**Chose a text field on Slice.**

One field, no new vocabulary; a migration is the whole cost.

Turned down: a separate model -- queryable, but a fourth noun on the board,
and nobody has asked to query it.

**Leans on** nobody needing to search decisions across slices.
```

Record decisions as you reach them, not as a summary afterwards.

Then post a short design summary in the conversation — the shape of the change,
the files it touches, the choices that were close calls — and **go straight on
to `building-a-slice` without waiting.** The summary exists so the person can
object, not so they have to approve.

If they object at any point, stop, follow them, and append a decision that says
what they overrode and why. That disagreement is the most useful entry in the
record.

Landmines and invariants you found go in `constraints`.

## 6. Dependencies

If this slice cannot meet its own done_when until another one ships, record it:
`link_slices([{"from": <blocker>, "to": <this>, "kind": "blocks", "note":
"why"}])`. "It would be more natural first" and "they touch the same files" are
not blocks.

## The small lane

A typo, a version bump, a copy fix, a one-line change with one obvious way to
do it. Create and take the slice, write a one-line spec and a done_when
yourself, say in one line which slice it is and that you are taking the small
lane, and build it. No approval; the pull request review is the human step.

If you can name a choice you would be making on the person's behalf, it is not
the small lane.

## Resuming

A slice at `needs_design` or `needs_done_when` that you hold is a design that
stopped part way. Pick it up where it stopped; do not create a second slice.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `brainstorming`, rewritten so the person approves the promise and the agent owns the design.
