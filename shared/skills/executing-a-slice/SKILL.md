---
name: executing-a-slice
description: "Use when a tuckit slice is ready to build — stage reads executing — or when picking up a half-finished one in a fresh session. Builds against the slice's done_when as the target, and ends by recording what was observed so the board moves."
---

# Executing a Slice

## Overview

Load the slice, review it critically, build until its `done_when` is met, then
record what you saw.

The slice already says what would settle it. That sentence was written before
anybody wrote code, on purpose — it is a target you can miss, and a target you
can miss is the only kind worth having. Your job here is not to work through a
list; it is to make that one sentence true and then show that it is.

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

**Announce at start:** "I'm using executing-a-slice to implement <ref>."

## Step 1: Load and Review

`get_slice(<ref>, with_activity=true)` and read in this order:

1. **spec** — what this is and why.
2. **constraints** — binding. If a constraint contradicts the spec, the
   constraint wins: it was written for exactly this moment.
3. **done_when** — the target. Read it before you write anything, because
   everything below is aimed at it.
4. **activity** — notes explain why the last session stopped, and are how you
   resume rather than restart.

Then, before the first change, **read what was already decided about the files
you are about to touch**:

```bash
git log --oneline -12 -- <the files this slice names>
```

Subjects carry slice refs. Any ref you do not recognise is a decision someone
made about this code, and `get_slice(<ref>)` is the whole reasoning behind it —
including the options that lost, which nothing in the code will ever tell you.
Two minutes here is what stops you re-litigating a settled question or quietly
undoing one.

This only reaches back as far as the convention does; older commits carry no
ref, and that is a gap to work around rather than a reason to skip the look.

**Then read the done_when once more and ask whether you could meet it and still
have built the wrong thing.** If yes, say so now — before the first commit, not
halfway through. A target that does not discriminate is the failure mode this
field exists to prevent, and it is cheapest to fix here.

If the slice has no `done_when` at all its stage reads `needs_done_when`, not
`executing`. Stop and write one with `designing-a-slice` first. A target
written afterwards is a description of what you did, which is the one thing it
must not be.

## Step 2: Isolated Workspace

Ensure the work happens in an isolated workspace: `git worktree add` a branch
off the base, following whatever branch and path convention the repo already
uses. Parallel sessions are the norm here, so the primary checkout is not
yours to occupy.

**Never start implementation on a main/master branch without your human
partner's explicit consent.**

## Step 3: Build Toward the Target

Break the work down however you like — a todo list, a scratch file, your own
head. **That breakdown is yours and it stays out of the board.** It is worth
something for the hour you are holding it and nothing the day after, and the
board is for what outlives the session.

While you build:

- If the work has a test-first shape, follow `writing-tests-first`.
- Run the project's real check, not the subset that happens to be fast. A
  suite scoped to the directory you touched skips the wiring guards above it.
- When something fails and the cause is not obvious, use
  `debugging-systematically` rather than guessing at fixes.
- Commit as you go, with the slice's ref in the subject line (`TUC-42: …`).
  That ref is the only thread running from a line of code back to the reason it
  exists: git says what changed, and following the ref is what turns that into
  why. Take it from the `Ref:` line of `get_slice`, never from the id you
  passed.

**Do not narrate progress into the board.** There is no status to tick here, and
a stream of "started X, finished Y" notes drowns the activity thread for the
person reading it next month. The board hears from you when something *changed*
— see the next step.

## Step 4: Things The Design Did Not Predict

- **A bug, an idea, a follow-up you are not doing now** → `create_capture(title=…,
  context=…)`: the title in the words you would say it, and what you saw in the
  context. Not a `TODO` comment, not a bullet in your closing message — both of
  those are places the board cannot see. Do not write a design into it and do
  not make it a slice: nobody has agreed to do it yet, and a capture is the
  object that says so.
- **You cannot finish until another slice lands** → record it:
  `link_slices([{"from": <the blocker>, "to": <this slice>, "kind": "blocks",
  "note": "why"}])`. Otherwise the dependency lives in this session's chat log
  and goes with it. Nobody has to approve the link — `link_slices(…,
  unlink=True)` takes it back — but the bar is checkable, so use it instead of
  your instinct: record a block only when this slice cannot meet its **own
  `done_when`** until the other one ships. "It would be more natural to do that
  first" and "they touch the same files" are not blocks. The `note` is
  required; `content/domain.md` says what the link then does to the roadmap,
  and why a wrong one is expensive: the blocked slice sits off the roadmap
  until somebody reads your reason and disagrees with it.
- **A landmine the next agent could hit** → append it to the slice's
  `constraints`. If it cost you real time, `add_note` as well: constraints say
  what the rule is, notes say what happened.
- **A decision you had to make while building** → `append_decision`. Design does
  not stop when implementation starts, and a choice made at the keyboard is
  exactly as expensive to rediscover as one made in the design conversation.
- **The done_when turns out to be wrong** → change it with
  `save_slice(done_when=…)` and **say out loud that you did, and why.**
  Revising a target you have understood better is the work. Quietly lowering one
  you could not meet is the single failure this whole axis exists to prevent,
  and the two look identical afterwards unless you said which one happened.

## When to Stop and Ask for Help

**STOP immediately when:**

- You hit a blocker (missing dependency, unclear instruction, a constraint you
  cannot satisfy)
- You don't understand something in the spec
- A verification keeps failing — that is a bug to investigate, not a blocker to
  report. Use `debugging-systematically`. Stop and ask only once three fixes
  have failed, which is that skill's own signal that the architecture, not the
  hypothesis, is wrong.

`add_note` what you hit before you stop — that turns a dead session into one the
next agent can resume. If what you hit is another slice, link it as well (Step
4): the note is prose someone has to read, the link is what keeps this slice off
the roadmap until the blocker moves.

**Ask for clarification rather than guessing.**

## Step 5: Review Before You Verify

The branch is what ships. Get a reviewer's eyes on it first: use
`requesting-a-review` with scope `branch`.

Hand the findings to `receiving-a-review`. Fix what needs fixing on this
branch, and route the rest — nothing is left in the chat log.

Review comes before verification on purpose. Evidence recorded against a branch
that then changes is evidence about something that no longer exists.

**If you have no subagents**, you cannot dispatch a reviewer, and reviewing
your own diff in this same session is worth little. Skip the review, but say
so plainly:

> "No subagents available, so this branch is going to shipping without a
> code review."

Saying it is the point. Work that was never reviewed and work that was
reviewed clean look identical on the board, and only your human partner can
decide whether that trade is acceptable here.

## Step 6: Show the Target Was Met

Meet the `done_when` for real, and write down what you actually SAW with
`record_verification`. That call is what moves the slice to `ready_to_ship`;
until it exists the board refuses to ship, and that refusal is the point.

**`verifying-before-claiming` owns this step** — including what counts as
evidence, why you name what you did *not* check, and why "pytest -q" is not an
observation. Use it. Writing evidence is a claim, and it is the heaviest claim
in this workflow because it is the one that persists.

Then: `shipping-a-slice`.

## Remember

- Read the done_when first, and doubt it once, before you build
- Your step breakdown is yours; the board gets decisions, landmines and evidence
- Don't skip the real check for the fast one
- Anything you defer becomes a capture, not a sentence in chat
- A dependency on another slice is a link with a note, also not a sentence in chat
- Changing the target is fine — changing it silently is not
- Stop when blocked, don't guess
- Never start implementation on main/master without explicit consent

## Subagent execution

When the work splits into parts that can be built and judged separately, hand
it out instead: `delegating-a-slice` runs implementers against this same
target and reviews what comes back. Execute inline as above when the work is
one indivisible piece, or when you have no subagents.

Either way the division is the same: **files keep the process; tuckit keeps the
decisions.** Reports and review packages stay on disk. What crosses to the
board: decisions, deferred work (as captures), dependencies you found (as
links), constraints you discovered, and the evidence at the end.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `executing-plans`,
rewritten so the target, not the checklist, is what the work aims at.
