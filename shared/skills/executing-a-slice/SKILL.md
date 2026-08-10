---
name: executing-a-slice
description: "Use when a tuckit slice has bites to implement — stage reads executing — or when picking up a half-finished slice in a fresh session. Runs the checklist and keeps each bite's status current so the board shows where the work actually is. In this workspace it replaces superpowers:executing-plans."
---

# Executing a Slice

Run the checklist from the board instead of from a file, and progress is written
where the human and the next session can already see it. A slice sitting at
`executing` with three of seven bites done is a resumable state, not a lost one.
That is the whole reason this skill exists.

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

**Announce at start:** "I'm using executing-a-slice to implement <ref>."

## 0. Load and review before you touch anything

`get_slice(<ref>, with_activity=true)` and read in this order:

1. **spec** — what this is and why.
2. **constraints** — binding. If a constraint contradicts a bite, the constraint
   wins and the bite is wrong.
3. **Steps** — `[x]` means already done by someone, possibly a past you. Do not
   redo them; verify only if you have reason to doubt them.
4. **activity** — notes explain why the last session stopped.

Review the plan critically first. Raise concerns before the first bite, not
halfway through. Never start implementation on `main`/`master` without explicit
consent.

## 1. Isolated workspace

Work in a worktree, not the primary checkout — parallel sessions are the norm
here. Use `superpowers:using-git-worktrees` if it is installed; otherwise
`git worktree add`. Follow whatever branch and path convention the repo already
uses.

## 2. The loop, one bite at a time

1. `update_bite(bite_id=…, status="doing")` — **before** you start, not after.
   This is what makes the board show the work while it is happening; skipping it
   makes a busy slice look idle to everyone else.
2. Follow the body exactly. If it specifies a test-first cycle, follow it
   (`superpowers:test-driven-development` if installed).
3. Verify as the bite specifies. Verification means the project's real check —
   not the subset that happens to be fast.
4. Commit.
5. `update_bite(bite_id=…, status="done")`.

**Never batch the status updates at the end.** A checklist filled in all at once
after the fact is a report; the point of putting it on the board was to be
readable *during*.

## 3. Things the plan did not predict

- **A bug, an idea, a follow-up you are not doing now** → `create_slice` with no
  area, so it lands in the Inbox. Not a `TODO` comment, not a bullet in your
  closing message — both of those are places the board cannot see.
- **A landmine the next agent could hit** → append it to the slice's
  `constraints`. If it cost you real time, `add_note` as well: constraints say
  what the rule is, notes say what happened.
- **The plan is wrong** → stop and fix the checklist (`update_bite`,
  `add_bites`) and say so. Do not quietly implement something else; the board
  would then describe work nobody did.

## 4. When to stop and ask

A blocker, a missing dependency, an instruction you do not understand, or
verification that keeps failing. Leave the bite at `doing` and `add_note` what
you hit — that turns a dead session into one the next agent can resume. Ask
rather than guess.

## 5. Subagent execution

If `superpowers:subagent-driven-development` is installed, use it for the
dispatch mechanics — one subagent per task, review packages, the on-disk ledger.
The rules above still apply on top of it, with one division:

**Files keep the process; tuckit keeps the decisions.** The ledger stays on
disk. Only three things cross to the board: bite status, deferred work (as new
slices), and constraints you discovered. Streaming a task-by-task ledger into
notes drowns the activity thread and buys nothing.

## 6. Done

When every bite is done the slice reads `ready_to_ship` on its own — there is no
field to set. Terminal state: `shipping-a-slice`.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `executing-plans`,
rewritten so progress lives on the board.
