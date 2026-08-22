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

### Rank them while you are here — same batch, same question

The list you are about to present is the only time this session asks the human
anything. So the priorities ride along with it rather than becoming a second
prompt: one message, one yes.

Read `org.priority_policy` from the project-state tool first. It is what counts
as which priority *here*, written by a person in their own words. Rank against
that text, not against your own sense of what is usually urgent — the two are
not the same, and only one of them knows this business.

**If the policy is empty, say so out loud.** Rank from general judgement, and
write one line admitting that is what you did:

> "No priority policy is written, so these are my own judgement — correct any
> that are wrong and I will offer to write the rule down."

That sentence is not an apology, it is the mechanism. An empty policy does not
get filled by someone sitting down in front of a blank Settings box; it gets
filled when a wrong ranking is in front of them and they say why it is wrong.

Propose priorities for the open slices you touched or reviewed this session,
not for the whole board — re-ranking everything is a cleanup pass
(`clearing-the-board`), not a write-back. Present them as `REF — title — N`,
grouped so they can be vetoed in blocks.

Apply the approved set in one call: the slice-update tool takes a list of ids
and `priority` is one of the fields a batch may carry.

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

## 4. Harvest the corrections

If the human changed any priority you proposed, **ask why, once, in one line.**

> "Noted. What made TP-42 a 1 rather than a 3?"

The answer is the thing that matters in this whole loop. It is a criterion they
would never have written into an empty box, and it only exists because a wrong
guess was sitting in front of them.

Offer to append it — the wording first, then the write:

> "Shall I add this to the priority policy? — *With zero customers, outreach
> beats most bugs.*"

On a yes, `append_priority_policy`. Append only: you cannot edit or remove a
line from there, and that is deliberate — the policy accrues over weeks out of
exactly these corrections, and no single call of yours should be able to undo
it. Editing and deleting live in the web UI, where a person is doing it.

**Do not append on your own initiative,** and do not append a line they did not
say. This is the most expensive text on the board; you are transcribing, not
authoring.

If they corrected nothing, there is nothing to harvest. Say nothing.

## Red flags

| You are about to… | Instead |
|---|---|
| Create a slice the moment you notice something | Collect it. The list goes to your partner at the end |
| Present the list without the numbers | The human is sizing a pile they cannot see |
| Treat silence as approval | It is not. Ask again, or leave it out |
| Skip step 1 because nothing obviously died | It is the only step that shrinks the board, so it is the one that never happens |
| Run the whole checklist on a session that never touched the board | Stop at the top |
| Ask about priorities in a second message | One batch, one yes. Friction is how a feature gets switched off |
| Rank from your own sense of what is urgent, with a policy sitting right there | Read `org.priority_policy`. It knows this business and you do not |
| Stay quiet about ranking blind when the policy is empty | Saying it is what gets the policy written |
| Append a line to the policy they did not say | You are transcribing a correction, not authoring criteria |
