---
name: clearing-the-board
description: "Use when a tuckit board has more open slices than anyone reads — the Inbox has piled up, a roadmap is capped, or nobody can say what is actually next. Reads the board's own numbers, proposes what to close and why, and closes the approved set in one call. Run it on a schedule, not only in a crisis."
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

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

**Announce at start:** "I'm using clearing-the-board to go through the open
slices."

## When to run this

- The board's own numbers say so: an area's roadmap reports `roadmap_omitted`
  above zero, or the Inbox has more than ~20 open, or `oldest_idle_days` is
  past a month.
- Someone asks what is next and the honest answer is "I can't tell from this."
- On the schedule the last run left behind (see step 6).

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
| `totals.drop_ratio` | how much of what this board captures has historically turned out not to be work |
| `inbox.open_count` / `oldest_idle_days` | how deep the unfiled pile is and how long it has waited |
| `totals.by_source` | whether this board is filled by people or by agents |

A high `drop_ratio` is not a reason to close more. It is evidence that the
*capture* side is miscalibrated, which is a different repair — see step 7.

### 2. List everything open, with its age

List the open slices, including the unfiled ones. Each row carries `age_days`
and `idle_days`. Read `stage` too: a slice at `executing` with recent activity
is someone's work in progress and is not a candidate, whatever its age.

### 3. Sort each one into three piles

**Alive** — leave it open, say nothing about it.

**Propose closing** — you can say what killed it.

**Ask** — you cannot tell without the human's context. Do not guess; a wrong
close here is how a roadmap loses a load-bearing item.

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

### 4. Present the proposal

One list. Every proposed close gets **one line saying what killed it** — and
"40 days old" is not that line. If you cannot write the line, the item belongs
in **Ask**, not in the close list.

Group them so the human can scan and veto in blocks (by area, or by the reason
they are dying), and state the totals: closing N of M, leaving K.

Then stop and wait. Nothing is closed before approval, and "no objection" is
not approval.

### 5. Close the approved set in one call

The slice-update tool takes a list of ids, so the whole approved set is a
single call. `dropped`, never deleted — the slice and its reasoning stay
readable, and only the claim that someone is going to do it goes away.

Record the list and the reasons on **one** slice, not on each closed one. A
note per closed slice is a second job that nobody will ever read; a single
record of what was closed and why is the artifact that makes the next pass
possible.

### 6. Leave the next run behind you

Create the next pass as a slice before you finish. A cleanup routine with no
trigger runs once, and then the board refills for a year.

### 7. If the capture side is the real problem, say so

If `drop_ratio` is high, or `by_source` shows agents writing most of the board,
closing things is treating a symptom. The repair lives on the capture side —
the review-routing gate, and the end-of-session approval batch. Name that in
your closing message rather than scheduling another cleanup.

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
