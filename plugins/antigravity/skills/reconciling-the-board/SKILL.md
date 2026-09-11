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
duplicate you created earlier, a finding that turned out to be wrong, an
approach overtaken by a decision made today — close it (`status: dropped`, or
`shipped` if it is genuinely done). `save_slice` takes a list of ids, so
closing several of them is a single call — tidying the board costs no more per
slice than filling it did.

Dropping is not deleting. The slice, its history and its reasoning stay
readable; only the claim that someone is going to do it goes away.

Links go stale the same way. Re-read the note on any `blocks` link you made or
relied on this session, and ask whether the blocked slice can now meet its own
`done_when` without the other one shipping. If it can, the link is untrue —
remove it with `link_slices(…, unlink=True)`. A stale link costs more than a
stale slice: while it stands, the blocked slice is listed apart from the
roadmap so nobody picks it up, and no screen shows blocked-ness yet, so nothing
will tell you it is wrong.

## 2. What you actually did

Record what you actually observed with `record_verification`, and leave a note
on the Slice — what you did, what blocked you, PR links. Recording evidence
moves the stage to `ready_to_ship` on its own; nothing else to set there.

Write what you SAW, not what you ran, and name what you did not check —
`verifying-before-claiming` owns that standard. If the session ends without you
meeting the slice's `done_when`, do not record evidence for it: the note is the
honest artifact, and an empty `evidence` field is what correctly leaves the
slice at `executing` for whoever picks it up.

If a Slice is genuinely finished (stage already reads `ready_to_ship`), mark it
shipped. That status change is the one decision on this list that is yours to
make rather than derived.

## 3. What should exist that doesn't — collect, then ask

Follow-ups, bugs you noticed, things this session decided to do next or later.

**Do not create these one at a time as you think of them.** Collect them, and at
the end present the whole list to your human partner for approval — each item
one line, with where it would go (the Area it belongs in, or the Inbox) and why
it is worth writing down. Create only what they approve.

Most of what you noticed late in a session is an observation, not work: nobody
has agreed to do it yet. Those go to the Inbox with `create_capture` — a title
in the words you would say it, and what you SAW in prose. It takes no spec
argument on purpose. Writing a design into something nobody agreed to do is how
a board fills with work that only looks decided; in one production Inbox, 10 of
16 unjudged notes had a full spec written into them. `save_slice` is for the
ones your partner just decided are work, and each of those needs an Area.

The approval is the point. An agent captures at the speed it notices things,
which is far faster than anyone closes them; a board that fills that way stops
being read, and then it does not matter what is on it.

Before you present the list, read the numbers `get_project_state` returns:

- `totals.drop_ratio` — of the things this board decided *were* work, the share
  someone later dropped. Slices only; a dismissed capture never enters it. High
  means what this board takes on mostly turns out not to be work, and this list
  should be shorter than it feels.
- `inbox.open_count` and `inbox.oldest_idle_days` — how many captures are
  already waiting, and how long the oldest has waited. Adding to a queue nobody
  has drained in a month is not capturing; it is hiding.

Say those numbers out loud when you present the list. The human is deciding
whether to add to a pile, and they should be able to see the pile.

### Rank them while you are here — same batch, same question

The list you are about to present is the only time this session asks the human
anything. So the priorities ride along with it rather than becoming a second
prompt: one message, one yes.

Read `workspace.priority_policy` from `get_project_state` first. It is what counts
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

Apply the approved set in one call: `save_slice` takes a list of ids, and
`priority` is one of the fields a batch may carry.

The exception: something your human partner explicitly asked you to put on the
board this session is already approved. Just create it.

### When there is nobody to ask

An unattended run (cron, headless, a hook with no human turn left) has no
approver. Do not fall back to creating slices — that is the behaviour this
section exists to stop, and running unattended is not a reason to be trusted
more. Write each item to the Inbox with `create_capture` instead, saying in the
context line that it came from an unattended run and what you were doing at the
time. A capture claims nothing, so one row each is honest here; nothing is
lost, and whoever drains the Inbox is the one who decides.

## 4. Harvest the corrections

If the human changed any priority you proposed, **ask why, once, in one line.**

> "Noted. What made TP-42 “Export the board as CSV” a 1 rather than a 3?"

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
| Write a spec into something nobody agreed to do | It is a capture: a title and what you saw |
| Leave a `blocks` link standing after its note stopped being true | Unlink it. It is holding the blocked slice off the roadmap and no screen says so |
| Present the list without the numbers | The human is sizing a pile they cannot see |
| Treat silence as approval | It is not. Ask again, or leave it out |
| Skip step 1 because nothing obviously died | It is the only step that shrinks the board, so it is the one that never happens |
| Run the whole checklist on a session that never touched the board | Stop at the top |
| Ask about priorities in a second message | One batch, one yes. Friction is how a feature gets switched off |
| Rank from your own sense of what is urgent, with a policy sitting right there | Read `workspace.priority_policy`. It knows this business and you do not |
| Stay quiet about ranking blind when the policy is empty | Saying it is what gets the policy written |
| Append a line to the policy they did not say | You are transcribing a correction, not authoring criteria |
