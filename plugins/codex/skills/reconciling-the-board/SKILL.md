---
name: reconciling-the-board
description: "Use at the end of a session that touched the tuckit board, or whenever someone asks to sync the board — closes what became untrue on the slices you hold, records what you did, and puts anything new in front of the person before it is created."
---

# Reconciling the Board

Close first, record second, create last — and creating needs a person's yes.

Vocabulary: `${PLUGIN_ROOT}/content/domain.md`.

**If nothing about the board changed this session, stop here and say nothing.**

**Only the slices you hold.** On a shared board, someone else's slice is
theirs to reconcile. If you saw something untrue on one, mention it with the
holder's name; do not change it.

## 1. What became untrue

A slice your work made unnecessary, a duplicate, a finding that turned out
wrong: close it with `save_slice` (`dropped`, or `shipped` only if its PR has
merged). A list of ids closes several in one call.

Re-read the note on any `blocks` link you made or relied on. If the blocked
slice can now meet its own done_when without the other one shipping, unlink it
with `link_slices(…, unlink=True)`.

## 2. What you did

`add_note` on each slice you worked: what you did, where you stopped, the PR
link. If you met the done_when and have not recorded it,
`record_verification` with what you saw. If you did not meet it, do not record
evidence; the note is the honest record and the slice stays at `executing`.

## 3. What should exist and does not — collect, then ask once

Follow-ups, bugs you noticed, things decided for later. Do not create them as
you think of them. Present the whole list at the end, one line each with where
it would go and why it is worth keeping.

Most of these are observations nobody has agreed to do: they become captures,
`create_capture(title, context)`. A slice is only for what the person has just
decided is work, and it needs an Area.

Before presenting, read `get_project_state` and say `inbox.open_count`,
`inbox.oldest_idle_days` and `totals.drop_ratio` out loud: the person is
deciding whether to add to a pile and should see the pile.

Priorities ride in the same message. Rank the open slices you touched against
`workspace.priority_policy`; if it is empty, say you ranked from your own
judgement. If the person corrects one, ask why in one line and offer to add the
answer with `append_priority_policy`, wording first.

Something the person explicitly asked you to put on the board this session is
already approved; just create it.

With nobody to ask (a headless or scheduled run), do not create slices. Write
each item as a capture and say in its context that it came from an unattended
run.
