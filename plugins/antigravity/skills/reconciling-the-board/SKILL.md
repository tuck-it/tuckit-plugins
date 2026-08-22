---
name: reconciling-the-board
description: "Use at the end of a session that touched the tuckit board, or whenever someone asks to sync/reconcile the board — close what became untrue, record what you did, and get approval before creating anything new. The write-back checklist in full."
---

# Reconciling the Board

## Overview

A stale board makes the SSOT lie. This is the pass that keeps it honest.

**Core principle:** close first, record second, create last — and creating needs
a person's yes.

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

**If nothing about the board changed this session, stop here.** Not every
session produces board work, and reaching for something to add is how a board
fills with things nobody asked for.

## 1. Did anything on the board become untrue?

Ask this first, because it is the only step that can make the board smaller and
it is the one that never gets taken. A slice your work just made unnecessary, a
duplicate you created earlier, a finding that turned out to be wrong, a plan
overtaken by a decision made today — close it (`status: dropped`, or `shipped`
if it is genuinely done).

The slice-update tool takes a list of ids, so closing several of them is a
single call — tidying the board costs no more per slice than filling it did.

Dropping is not deleting. The slice, its history and its reasoning stay
readable; only the claim that someone is going to do it goes away.

## 2. What you actually did

Check off completed Bites and leave a note on the Slice — what you did, what
blocked you, PR links. Checking off the last Bite moves its stage to
`ready_to_ship` on its own; nothing else to set there.

If a Slice is genuinely finished (stage already reads `ready_to_ship`), mark it
shipped. That status change is the one decision on this list that is yours to
make rather than derived.

## 3. What should exist that doesn't — collect, then ask

Follow-ups, bugs you noticed, things this session decided to do next or later.

**Do not create these one at a time as you think of them.** Collect them, and at
the end present the whole list to your human partner for approval — each item
one line, with where it would go (an Area, or the Inbox) and why it is worth a
slice. Create only what they approve.

The approval is the point. An agent captures at the speed it notices things,
which is far faster than anyone closes them; a board that fills that way stops
being read, and then it does not matter what is on it.

Before you present the list, read the numbers the project-state tool returns:

- `totals.drop_ratio` — the share of everything ever captured here that someone
  later decided was not work. High means your instinct to capture has been
  wrong most of the time, and this list should be shorter than it feels.
- `inbox.open_count` and `inbox.oldest_idle_days` — how much is already waiting,
  and how long the oldest has waited. Adding to a queue nobody has drained in a
  month is not capturing; it is hiding.

Say those numbers out loud when you present the list. The human is deciding
whether to add to a pile, and they should be able to see the pile.

The exception: something your human partner explicitly asked you to put on the
board this session is already approved. Just create it.

### When there is nobody to ask

An unattended run (cron, headless, a hook with no human turn left) has no
approver. Do not fall back to creating each item — that is the behaviour this
section exists to stop, and running unattended is not a reason to be trusted
more. Capture the whole batch as **one** slice in the Inbox, titled as what it
is (`"Unattended capture: N follow-ups from <what you were doing>"`), with the
list in its spec. One row, nothing lost, and it is honest that nobody has
triaged it.

## Red flags

| You are about to… | Instead |
|---|---|
| Create a slice the moment you notice something | Collect it. The list goes to your partner at the end |
| Present the list without the numbers | The human is sizing a pile they cannot see |
| Treat silence as approval | It is not. Ask again, or leave it out |
| Skip step 1 because nothing obviously died | It is the only step that shrinks the board, so it is the one that never happens |
| Run the whole checklist on a session that never touched the board | Stop at the top |
