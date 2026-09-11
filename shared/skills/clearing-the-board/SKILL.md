---
name: clearing-the-board
description: "Use when a tuckit board has more open slices than anyone reads — a roadmap is capped, rows have sat for months, or nobody can say what is actually next. Reads the board's own numbers, proposes what to close and why, and closes the approved set in one pass. Run it on a schedule, not only in a crisis."
---

# Clearing the Board

## Overview

An open slice costs nothing to create and nothing to keep. That asymmetry is
the whole problem: capture happens at the speed an agent notices things, and
closing happens only when a human sits down and decides to. Left alone, a board
converges on a state where everything is technically true and nothing is
readable.

**Core principle:** propose, never close on your own — and say *why this is
dead*, never *how old it is*.

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

**Announce at start:** "I'm using clearing-the-board to go through the open
slices and what is sitting in the Inbox."

## When to run this

- The board's own numbers say so: an area's roadmap reports `roadmap_omitted`
  above zero, or a roadmap has rows whose `idle_days` is past a month.
- Someone asks what is next and the honest answer is "I can't tell from this."
- On the schedule the last run left behind (see step 6).

Not this skill: an Inbox that piled up on its own. Judging captures is
`filing-the-inbox`, and it runs before this one. Step 2 is where you tell the
two cases apart.

Do not run it because a session felt untidy. This skill is the one that makes
the board smaller, which means it is also the one that can quietly delete a
roadmap — running it often and casually is its failure mode, not its purpose.

## The pass

### 1. Read the numbers before the slices

`get_project_state` first. Write down four things and keep them visible for the
rest of the pass:

| number | why you need it |
|---|---|
| `totals.open` | the size of what you are about to review |
| `totals.drop_ratio` | how much of what this board decided *was* work later turned out not to be. Slices only — a dismissed capture never enters it |
| `inbox.open_count` / `inbox.oldest_idle_days` | how deep the unjudged pile is and how long it has waited. **It counts captures, not slices.** None of them are inside `totals.open`, so the whole board is the two added; reading either as the other counts one pile twice |
| `totals.by_source` | whether this board is filled by people or by agents |

A high `drop_ratio` is not a reason to close more. It is evidence that the
*capture* side is miscalibrated, which is a different repair — see step 7.

### 2. Read both piles, with their ages

`list_slices` for the open slices. Each row carries `age_days` and `idle_days`.
Read `stage` too: a slice at `executing` with recent activity is someone's work
in progress and is not a candidate, whatever its age.

Read `priority` as well. A row with none is simply unranked — that is the
normal state and says nothing either way. A row that *has* one is a decision
somebody made, and it changes what its age means.

Then `list_captures()` for the Inbox. It is a different set from `list_slices`,
not a filter on it, and its rows carry `title`, `context`, `state`, `source` and
`age_days` — no priority, no stage, no `done_when`, because nobody has decided
any of it is work. Read it before you decide this is the right pass: 30 open
slices and 40 captures is a different board from 70 open slices. The second is
a board nobody closes, which is this skill. The first is a board nobody judges,
and that is `filing-the-inbox` — run it first, since what it promotes becomes
an open slice you would then be reading here.

### 3. Sort each one into three piles

**Alive** — leave it open, say nothing about it.

**Propose closing** — you can say what killed it.

**Ask** — you cannot tell without the human's context. Do not guess; a wrong
close here is how a roadmap loses a load-bearing item.

**A high priority that has sat still belongs in Ask, never in the close list.**
Somebody decided this was urgent and then nobody did it. That means one of two
things — it was not actually urgent, or it is blocked — and you cannot tell
which from the board. Both need the human, and both are worth more than the
slice itself: the first says the ranking is miscalibrated, the second says
something is stuck and silent.

It is the strongest signal on this pass, and the easiest to get backwards.
Age alone would put it at the top of the close list; it is the one row that
most deserves a person's eyes.

The line that matters, and the one this pass gets wrong:

> **"We are not doing this now" is not "this is not work."**

The first is a schedule. The second is a decision. Only the second closes.

A worked example, from the run this skill came out of: a board bankruptcy on
2026-08-22 closed 109 of 140 open slices, and two of them had to be reopened
the same day — the slice asking for a priority field, and the one asking for a
container that ends. Both had sat untouched for weeks, both looked exactly like
dead weight, and both turned out to be the mechanisms that would have stopped
the board filling in the first place. Age said close; the actual question —
*is this still true?* — said keep. Age is how you pick candidates. It is never
the reason.

**Close when:** the observation still holds but nobody will act on it · the
direction changed and its premise is gone · something else absorbed it · it was
a duplicate.

**Keep when:** a real deadline hangs on it · it makes a customer · it is
irreversible damage (data, security, money) · it is in someone's hands right
now · it is the fix for why this board filled up.

**Captures sort the same way, on less.** One has no priority, no stage and no
`done_when`, so most of the reading above has nothing to work with — you have a
title, prose and an age. Take only the ones you can say what killed them; the
rest stay in the Inbox for `filing-the-inbox`. Nothing gets promoted in this pass. A
promotion puts a new row on somebody's roadmap, which is the opposite of what
you are here to do, and it is a judgement that deserves its own reading.

### 4. Present the proposal

One list. Every proposed close gets **one line saying what killed it** — and
"40 days old" is not that line. If you cannot write the line, the item belongs
in **Ask**, not in the close list.

Group them so the human can scan and veto in blocks (by area, or by the reason
they are dying), and state the totals: closing N of M, leaving K. Keep the
captures as their own block with their own count — they are not slices, and a
single merged number tells the reader nothing about which pile is the problem.

Every row carries its title. This list exists to be scanned, and a row that is
only a number cannot be.

Then stop and wait. Nothing is closed before approval, and "no objection" is
not approval.

### 5. Close the approved set

`save_slice` takes a list of ids, so the approved slices are a single call.
`dropped`, never deleted — the slice and its reasoning stay readable, and only
the claim that someone is going to do it goes away.

The captures are not in that call. Each one is
`triage_capture(<capture_id>, "dismiss")`, one call per capture. Dismissal is
soft the same way dropping is: the row survives, stays readable, and
`decision="restore"` brings it back if the judgement was wrong. Worth saying in
step 4 while the list is still a proposal: bulk closing stalls on the fear of
losing something, and neither exit here loses anything.

Record the list and the reasons — dropped slices and dismissed captures
together — on **one** slice, not on each closed one. A note per closed slice is
a second job that nobody will ever read; a single record of what was closed and
why is the artifact that makes the next pass possible.

### 6. Leave the next run behind you

Create the next pass as a slice before you finish. A cleanup routine with no
trigger runs once, and then the board refills for a year.

### 7. If the capture side is the real problem, say so

If `drop_ratio` is high, or `by_source` shows agents writing most of the board,
closing things is treating a symptom. The repair lives on the capture side —
the review-routing gate, and the end-of-session approval batch. And an unjudged
observation now has the Inbox to sit in, so a dropped slice is one somebody
wrote as work before anyone agreed it was — that is the gap the ratio is
pointing at. Name it in your closing message rather than scheduling another
cleanup.

The same goes for a pile of stalled high priorities: that is not a cleanup
problem either. It means the ranking and the doing have come apart, and the
repair is the priority policy — the criteria are wrong, or nobody is reading
them. Name it instead of closing the rows.

## Red flags

| You are about to… | Instead |
|---|---|
| Close because it is old | Age picks candidates. Say what killed it, or move it to Ask |
| Close because "we're not doing this now" | That is a schedule, not a decision. Keep it |
| Write a note on each closed slice | One record, on one slice |
| Close without approval | Propose. "No objection" is not approval |
| Run this because the session felt untidy | Run it on the numbers, or on the schedule |
| Delete instead of dropping | The record survives. That is the product's whole claim |
| Schedule another cleanup after a high `drop_ratio` | Fix the capture gate instead |
| Close a high priority because it has not moved | That is the strongest signal on the board. It goes to Ask |
| Count `inbox.open_count` as part of `totals.open` | Two piles. One is captures, one is slices, and neither is inside the other |
| Promote a capture while you are here | Promoting adds a roadmap row. That pass is `filing-the-inbox` |
