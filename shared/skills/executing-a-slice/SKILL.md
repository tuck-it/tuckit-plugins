---
name: executing-a-slice
description: "Use when a tuckit slice has bites to implement — stage reads executing — or when picking up a half-finished slice in a fresh session. Runs the checklist and keeps each bite's status current so the board shows where the work actually is."
---

# Executing a Slice

## Overview

Load the slice, review it critically, execute the bites, keep the board current,
report when complete.

Running the checklist from the board instead of from a file means progress is
written where the human and the next session can already see it. A slice sitting
at `executing` with three of seven bites done is a resumable state, not a lost
one. That is the whole reason this skill exists.

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

**Announce at start:** "I'm using executing-a-slice to implement <ref>."

## Step 1: Load and Review

`get_slice(<ref>, with_activity=true)` and read in this order:

1. **spec** — what this is and why.
2. **constraints** — binding. If a constraint contradicts a bite, the constraint
   wins and the bite is wrong.
3. **Steps** — `[x]` means already done by someone, possibly a past you. Do not
   redo them; verify only if you have reason to doubt them.
4. **activity** — notes explain why the last session stopped.

Then:

- Review the plan critically — identify any questions or concerns about it
- If concerns: raise them with your human partner **before the first bite**, not
  halfway through
- If no concerns: create a todo per bite and proceed

## Step 2: Isolated Workspace

Ensure the work happens in an isolated workspace: `git worktree add` a branch
off the base, following whatever branch and path convention the repo already
uses. Parallel sessions are the norm here, so the primary checkout is not
yours to occupy.

**Never start implementation on a main/master branch without your human
partner's explicit consent.**

## Step 3: The Loop, One Bite At A Time

For each bite:

1. `update_bite(bite_id=…, status="doing")` — **before** you start, not after.
   This is what makes the board show the work while it is happening; skipping it
   makes a busy slice look idle to everyone else.
2. Follow the body exactly — it has bite-sized steps for a reason. If it
   specifies a test-first cycle, follow it: write the failing test, run it and
   watch it fail, implement the minimum, run the tests, commit.
3. Run verifications as specified. Verification means the project's real check —
   not the subset that happens to be fast.
4. Commit.
5. `update_bite(bite_id=…, status="done")`.

**Never batch the status updates at the end.** A checklist filled in all at once
after the fact is a report; the point of putting it on the board was to be
readable *during*.

## Step 4: Things The Plan Did Not Predict

- **A bug, an idea, a follow-up you are not doing now** → `create_slice` with no
  area, so it lands in the Inbox. Not a `TODO` comment, not a bullet in your
  closing message — both of those are places the board cannot see.
- **A landmine the next agent could hit** → append it to the slice's
  `constraints`. If it cost you real time, `add_note` as well: constraints say
  what the rule is, notes say what happened.
- **The plan is wrong** → stop and fix the checklist (`update_bite`,
  `add_bites`) and say so. Do not quietly implement something else; the board
  would then describe work nobody did.

## When to Stop and Ask for Help

**STOP executing immediately when:**

- You hit a blocker (missing dependency, failing test, unclear instruction)
- The checklist has critical gaps preventing you from starting
- You don't understand an instruction
- Verification fails repeatedly

Leave the bite at `doing` and `add_note` what you hit — that turns a dead
session into one the next agent can resume.

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**

- Your partner updates the slice based on your feedback
- The fundamental approach needs rethinking

**Don't force through blockers** — stop and ask.

## Step 5: Complete

When every bite is done the slice reads `ready_to_ship` on its own — there is no
field to set. Terminal state: `shipping-a-slice`.

## Remember

- Review the slice critically first
- Follow the bite bodies exactly
- Don't skip verifications
- Update bite status as you go, never in a batch at the end
- Anything you defer becomes a slice, not a sentence in chat
- Stop when blocked, don't guess
- Never start implementation on main/master without explicit consent

## Subagent execution

One subagent per bite, with a review between them, is a stronger loop than
executing inline — and it is what `delegating-a-slice` provides. Use that skill
instead of this one when the bites are mostly independent and you want a fresh
implementer and a reviewer per bite. Execute inline as above when they are
tightly coupled, or when you have no subagents.

Either way the division is the same: **files keep the process; tuckit keeps the
decisions.** Reports and review packages stay on disk. Only three things cross
to the board — bite status, deferred work (as new slices), and constraints you
discovered. Streaming a bite-by-bite ledger into notes drowns the activity
thread and buys nothing.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `executing-plans`,
rewritten so progress lives on the board.
