---
name: filing-the-inbox
description: "Use when a tuckit board has unfiled captures waiting — the Inbox has items nobody has put anywhere, or someone asks what is in it. Decides which ones are worth doing, files those into Areas, and proposes the rest for closing, in one batch rather than one question at a time."
---

# Filing the Inbox

The Inbox is every slice with no area: things someone decided mattered before
deciding where they belong. Filing one into an Area is the moment somebody says
**this is worth doing**. Nothing else on the board carries that judgement, and
a capture that never gets it is not deferred work — it is a note nobody will
read again.

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

**Announce at start:** "I'm using filing-the-inbox to work through the N
unfiled captures."

**Core principle:** one batch, one approval. Filing is reversible in both
directions, so it is cheap to be wrong — but asking about twenty captures one
at a time costs more attention than the whole Inbox is worth, and that cost is
why boards go unfiled in the first place.

## When this runs

- The Inbox has more than a handful of open captures.
- Someone asks what is in the Inbox, or what is next.
- You just captured several things during a session and they are all sitting
  unfiled. Do it now rather than leaving it for `reconciling-the-board`, which
  is about what THIS session changed, not about the backlog it landed in.

Not this skill: closing a full **roadmap** — that is `clearing-the-board`,
which reads an Area's numbers and proposes what to close. Filing and clearing
answer different questions and they collide when run together, so run this one
first: what you file stops being a candidate for closing.

## 1. Read the board before reading the captures

`get_project_state`. Three numbers decide how you read everything below:

- `inbox.open_count` — how many are waiting.
- `inbox.oldest_idle_days` — an Inbox whose oldest capture has sat forty days
  is telling you that filing more is not what it needs.
- `totals.drop_ratio` — the share of everything ever captured that someone
  later decided was not work. **This is the denominator for "will anyone
  actually do this?"** A board that drops half of what it collects has already
  answered that question about half of what you are looking at, and your
  optimism about any one capture is not evidence against it.

Then `list_slices(area_id='')` for the captures themselves, with `age_days`
and `idle_days` on every row.

## 2. Read what the Areas actually are

`list_areas`. An Area is a long-lived responsibility, not a label. You are
about to say a capture belongs to one, so know what each one owns.

If a capture belongs to no existing Area and you are tempted to make a new one:
don't, unless a second capture wants the same one. **An Area with one slice in
it is a tag pretending to be a boundary**, and every later filing decision pays
for it.

## 3. Sort into three, and be able to say why

For each capture, exactly one of:

**File it** — someone will do this. Name the Area and, if the workspace has a
`priority_policy`, the priority. Read that policy first: what counts as urgent
here is what a person wrote in their own words, not your own sense of it.

**Leave it** — worth keeping, not yet worth placing. This is a real answer, not
a failure to decide. A capture whose moment has not come stays where it is.

**Propose closing** — you can say what killed it: it shipped some other way, it
was overtaken by a decision, it describes a product that no longer exists. "We
are not doing this now" is a schedule, not a decision; that one gets *leave
it*.

The split that matters is not important-vs-unimportant. It is **will anyone
actually do this**, and the honest answer for most of an old Inbox is no.

## 4. One message, one approval

Present all three lists at once. Every filing gets the Area; every proposed
close gets **one line saying what killed it**. Say the numbers you read in step
1, because they are the argument.

**Every ref carries its title.** A row the reader has to look up is a row they
approve without reading, which is the failure this batch was meant to avoid.

> "Inbox: 13 open, oldest idle 40 days, and this board has dropped 50% of
> everything it ever captured.
>
> **File (6)** — TP-355 "Retry duplicates the welcome note" → oss,
> TP-352 "Docs search returns nothing for two-word queries" → oss, …
> **Leave (4)** — TP-306 "Split the settings page in two", … : still true,
> no moment yet.
> **Close (3)** — TP-280 "Re-point the webhook at the new queue": the
> re-point it describes was rebuilt in TP-291 "Queue rewrite". …
>
> Objections, or shall I apply it?"

**Wait for a real answer.** Silence is not approval, and this is the one step
where an agent filing on its own would be making the judgement the human keeps.

## 5. Apply it in one call

`save_slice` takes a **list** of ids and sets `area_id`, `status` and
`priority` across them — the reversible decisions, and only those. Tidying a
board should not cost more per slice than filling it did.

Then say what you did in one line, with the counts. Not a table of everything.

## Red flags

| You are about to… | Instead |
|---|---|
| File everything, because each one is defensible on its own | The drop ratio is the argument against that, and it is on the board |
| Make a new Area for one capture | A boundary nobody works along is paid for at every later filing |
| Close because "not now" | That is a schedule. Keep it |
| Ask about each capture in turn | One batch. The per-question cost is why Inboxes rot |
| File it and start building it | Filing says it is worth doing. `designing-a-slice` says what it is |
| Treat an empty Inbox as a problem | It is the normal state of a board someone tends |
