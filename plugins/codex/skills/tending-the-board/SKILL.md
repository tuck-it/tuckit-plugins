---
name: tending-the-board
description: "Use when a tuckit board needs judging rather than building: captures are waiting in the Inbox, an Area holds more open slices than anyone reads, rows have sat for weeks, titles are hard to read, or nobody can say what is next. Reads the board's own numbers, proposes in one batch what to promote, leave, dismiss, close or retitle and why, and applies only what the person approves."
---

# Tending the Board

Capturing costs an agent nothing and closing costs a person a decision, so a
board left alone fills until nobody reads it. This pass is where the person
sets direction in bulk: one list, one approval.

Reference: `${PLUGIN_ROOT}/content/domain.md`, including how to write for the board.

**Propose, never apply on your own. And say why something should go, never how
old it is.**

## 1. Read the numbers first

`get_project_state`, and keep these visible for the whole pass:

| number | what it tells you |
|---|---|
| `inbox.open_count`, `inbox.oldest_idle_days` | the unjudged pile: captures, not slices |
| `totals.open` | open slices; captures are not inside it |
| `totals.drop_ratio` | the share of what this board decided was work that was later dropped |
| `workspace.priority_policy` | what counts as urgent here, in a person's words |

A high `drop_ratio` says the capture side is too eager. Say so; closing more
does not fix it. When `inbox.open_count` is 20 or more, or `drop_ratio` is 0.5
or higher, a new capture is only worth it if someone can be named to do it.

## 2. Read both piles

`list_captures()` for the Inbox and `list_slices(status="open")` for the
roadmap. They are different sets. Read `age_days`, `idle_days`, `stage`,
`priority` and `assignee` on each row, and `list_areas()` so you know what each
Area owns before you put anything in one.

## 3. Sort

**Captures** — exactly one of:

- **Promote** into a named Area: someone will actually do this. The new slice
  starts with an empty spec; no design here.
- **Leave**: still true, its moment has not come. That is what the Inbox is for.
- **Dismiss**: you can say what killed it — shipped another way, overtaken by a
  decision, describes something that no longer exists.

**Open slices** — exactly one of:

- **Alive**: say nothing.
- **Propose closing**: you can say what killed it. "We are not doing this now"
  is a schedule, not a reason; that slice stays.
- **Ask**: you cannot tell without the person's context.

A high priority that has sat still goes to **Ask**, never to the close list. It
means either the ranking is wrong or something is stuck, and both are worth a
person's eyes more than the slice is.

Keep: a deadline hangs on it, it makes a customer, it prevents irreversible
damage, someone is working it now (`stage` executing with recent activity), or
it is the fix for why the board filled up.

**Someone else's slice** — you may propose closing it, but name the holder in
the row. It is their call as much as the approver's.

Do not create a new Area for one capture. An Area with one slice is a tag
pretending to be a boundary.

**Titles** — a title a person cannot take in at a glance (jargon, a ref or
code name, two clauses joined by a dash, or simply long) makes the whole board
heavier. Propose a plain rewrite for each one you pass, following the domain
reference. Retitling changes no promise; it is the cheapest thing in this
pass.

## 4. One message, one approval

State the numbers from step 1, then the lists. Every row carries its title.
Every dismissal and every close carries one line saying what killed it. Group
rows so they can be vetoed in blocks.

> "Inbox: 13 captures, oldest 40 days. 50% of what this board took on was
> later dropped.
>
> **Promote (2)** — TP-355 "Retry duplicates the welcome note" → billing, …
> **Leave (4)** — TP-306 "Split the settings page in two", …
> **Dismiss (3)** — TP-280 "Re-point the webhook": rebuilt in TP-291 "Queue
> rewrite". …
> **Close (5 of 31 open)** — TP-212 "Dark mode for the docs" (held by Mina):
> the docs moved to the theme that ships it. …
> **Ask (1)** — TP-198 "Export as CSV", priority 1, idle 30 days: still urgent?
> **Retitle (2)** — TP-240 "Session restore — hydrate order regression …" →
> "Home screen is blank after logging in". …
>
> Shall I apply this?"

Silence is not approval. Wait.

## 5. Apply

- Promote: `triage_capture(capture_id, "promote", area_id=…)`.
- Dismiss: `triage_capture(capture_id, "dismiss")`. `"restore"` undoes it.
- Close: one `save_slice(slice_id=[…], status="dropped")` for the whole
  approved set. Dropped, never deleted.
- Priorities the person set while approving: `save_slice` takes a list of ids
  and `priority` may ride in the batch.
- Retitle: `save_slice(slice_id, title=…)`, one slice at a time.

Record what was closed and why in **one** `add_note` on one slice, not on each.
Then report the counts in one line.

If the person corrected a priority you proposed, ask why in one line. If the
answer is a rule, offer to add it to the policy with the wording first; on a
yes, `append_priority_policy`. Never append a line they did not say.
