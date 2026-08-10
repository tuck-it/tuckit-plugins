---
name: shipping-a-slice
description: "Use when a tuckit slice's implementation is finished — stage reads ready_to_ship — and the branch needs to land. Verifies for real, lands the branch, records what happened on the slice, and asks before marking it shipped. In this workspace it replaces superpowers:finishing-a-development-branch."
---

# Shipping a Slice

Two things end here: the branch, and the board's claim about this work. Letting
one happen without the other is how a tracker starts lying.

Vocabulary and stages: `${PLUGIN_ROOT}/content/domain.md`.

**Announce at start:** "I'm using shipping-a-slice to land <ref>."

## 1. Verify for real, before you present anything

- Run the **full** suite, not the scoped subset you were iterating on. Narrowing
  to the directory you touched skips the wiring guards that live above it, and
  those are the ones that catch integration mistakes.
- Re-read the slice's `constraints` and check the work against them literally.
  That field is where "done" was defined, by someone who had more context than
  you do now.
- If the change has a surface a person uses, open it and look. Endpoint tests
  pass while the screen is broken.
- If production runs a different database or runtime than your local one, run
  the check there too. A green local suite is evidence about your machine.

Tests failing → report the failures and stop. The menu in step 3 comes after a
green suite, never before it. Report what actually ran: an unrun suite described
as passing is the exact failure this step exists to prevent.

## 2. Reconcile the checklist with reality

Before landing anything, make the board match what happened:

- Work that is done but still shows `todo` → mark it `done`.
- Work you decided **not** to do → `dropped`, with a note saying why. Leaving it
  `todo` makes the slice look unfinished forever; deleting it hides the
  decision.
- Anything discovered and deferred → new slices now, in the Inbox. "We should
  also…" said in chat and nowhere else does not survive this session.

## 3. Present the landing options

Verify green, work out which branch this forked from (ask if it is not obvious —
merging into the wrong base is expensive to undo), then present exactly:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
```

On a detached HEAD (an externally managed workspace), drop the merge option and
offer push-and-PR or keep-as-is. Wait for the answer — the integration decision
is the human's. Discard the work only if they explicitly ask for it.

## 4. Record what happened

`add_note(slice=<ref>, body=…)`: what shipped, the merge commit or PR link, what
surprised you, what you left out. Notes are timestamped and append-only, and
they are what makes this slice readable in six months when the diff no longer
explains itself.

If you hit a landmine along the way, it belongs in `constraints` as well as in
the note. The note says what happened to you; constraints say what the next
person must not repeat.

## 5. Ask before marking it shipped

`status` is the one field nothing derives — it records a decision a human made.
The stage reading `ready_to_ship` means the checklist is empty, which is not the
same as someone deciding this is done and out.

Ask. On a yes, `update_slice(slice_id=…, status="shipped")`. On a no, say what
is still missing and leave it open — an open slice with a clear note is honest;
a shipped slice with unfinished work is not.

Shipping does not need an area. A slice can ship straight out of the Inbox.

## 6. Clean up, then say what is true

Remove the worktree and branch the way the repo expects. Then close with one
line about the board, not about your process: which slice is shipped, and which
slices this session created for later.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) —
`finishing-a-development-branch`, rewritten so landing the branch and closing
the slice are one act.
