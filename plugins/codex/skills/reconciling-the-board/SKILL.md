---
name: reconciling-the-board
description: "Use at the end of a session that touched the tuckit board, or whenever someone asks to sync the board. Closes what became untrue, ships slices whose pull request has merged, records what you did, and puts anything new in front of the person before it is created."
---

# Reconciling the Board

Close first, record second, create last. Creating needs a person's yes.

Reference: `${PLUGIN_ROOT}/content/domain.md`.

**If nothing about the board changed this session, stop here and say nothing.**

## 1. What became untrue

On the slices you hold: one your work made unnecessary, a duplicate, a finding
that turned out wrong. Close it with `save_slice` (`dropped`). A list of ids
closes several in one call.

Merged pull requests are the exception to "only what you hold": if you saw a
slice's PR merged, mark it `shipped` whoever holds it. The merge was the
confirmation. Anything else untrue on someone else's slice, mention with the
holder's name; do not change it.

Re-read the note on any `blocks` link you made or relied on. If it is no longer
true, unlink it with `link_slices(…, unlink=True)`.

## 2. What you did

`add_note` on each slice you worked: what you did, where you stopped, the PR
link, in a few plain sentences. If you met the done_when and have not recorded
it, `record_verification` with what you saw. If you did not, record no
evidence; the note is the honest record.

## 3. What should exist and does not: collect, then ask once

Follow-ups, bugs you noticed, things decided for later. Do not create them as
you think of them. Present the whole list at the end, one line each: the title
you would give it (written for the board), where it would go, and why it is
worth keeping.

Most of these are observations nobody has agreed to do, so they become
captures, `create_capture(title, context)`. A slice is only for what the person
has just decided is work, and it needs an Area.

Before presenting, read `get_project_state` and say how big the Inbox is and how
old its oldest capture is: the person is deciding whether to add to a pile and
should see the pile. If it is already large, keep only what someone will
actually do.

Rank the open slices you touched against the workspace's priority policy in the
same message; with no policy, say you used your own judgement. If the person
corrects one, ask why in one line and offer to add the answer with
`append_priority_policy`, wording first.

Something the person explicitly asked you to put on the board is already
approved; just create it. With nobody to ask (a headless or scheduled run), do
not create slices: write each item as a capture and say in its context that it
came from an unattended run.
