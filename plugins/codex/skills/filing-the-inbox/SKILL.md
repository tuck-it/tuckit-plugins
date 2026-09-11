---
name: filing-the-inbox
description: "Use when a tuckit board has captures waiting — the Inbox holds notes nobody has judged yet, or someone asks what is in it. Reads the whole Inbox, decides which captures become slices in an Area, which get dismissed and which simply wait, and puts the whole judgement up for one approval rather than one question at a time."
---

# Filing the Inbox

Vocabulary and stages: `${PLUGIN_ROOT}/content/domain.md` — it carries what a capture
is and what each of its two exits does, so this skill does not repeat it.

What this skill is for is the one thing that reference cannot enforce: the two
exits have to stay peers in your head. **Promote** into an Area and **dismiss**
cost the same, and roughly two captures in five end in dismissal on a board
somebody tends. Read promoting as the good outcome and dismissing as giving up,
and you will promote most of an Inbox — and every promotion puts a row on
somebody's roadmap.

**Announce at start:** "I'm using filing-the-inbox to work through the N
captures in the Inbox."

**Core principle:** one batch, one approval. Not because the judgement needs a
gate — both exits are reversible — but because the person is reading N rows at
once, and asking about twenty captures one at a time costs more attention than
the whole Inbox is worth. That cost is why Inboxes rot.

## When this runs

- The Inbox has more than a handful of captures.
- Someone asks what is in the Inbox, or what is next.
- You captured several things during a session and they are all still unjudged.
  Do it now rather than leaving it for `reconciling-the-board`, which is about
  what THIS session changed, not about the backlog it landed in.

Not this skill: closing a full **roadmap** — that is `clearing-the-board`,
which reads an Area's numbers and proposes what to close. The two collide when
run together, so run this one first: what you promote here becomes an open
slice, which is exactly what that skill reads.

## 1. Read the board before reading the captures

`get_project_state`. Three numbers decide how you read everything below:

- `inbox.open_count` — how many are waiting. It counts captures, not slices.
- `inbox.oldest_idle_days` — an Inbox whose oldest capture has sat forty days
  is telling you that judging what is already there matters more than adding to
  it.
- `totals.drop_ratio` — the share of everything this board has turned into a
  slice that someone later dropped. **This is the denominator for "will anyone
  actually do this?"** A board that drops half of what it promotes has already
  answered that question about half of what you are looking at, and your
  optimism about any one capture is not evidence against it.

Then `list_captures()` for the captures themselves, newest first. That is a
different set from `list_slices`, not a filter on it. Each row carries `title`,
`context`, `source` and `age_days`. Read `age_days` per row and not only on the
oldest: a capture written this morning and one that has waited six weeks are not
the same question. `list_captures(dismissed=True)` shows what was already thrown
away, which is worth a glance when you cannot tell whether something is new or a
re-run of a judgement somebody already made.

## 2. Read what the Areas actually are

`list_areas`. **Promoting requires an `area_id`** — a promote without one is
refused, and the error text sends you here — so read the Areas before you
propose anything. An Area is a long-lived responsibility, not a label. You are
about to say a capture belongs to one, so know what each one owns.

If a capture belongs to no existing Area and you are tempted to make a new one:
don't, unless a second capture wants the same one. **An Area with one slice in
it is a tag pretending to be a boundary**, and every later judgement pays for it.

## 3. Sort into three, and be able to say why

For each capture, exactly one of:

**Promote** — someone will do this. Name the Area. The new slice starts with an
empty spec on purpose, so do not write a design anywhere in this pass;
`designing-a-slice` fills it later and replaces nothing.

**Leave it** — worth keeping, not yet worth judging. This is a real answer, not
a failure to decide. A capture whose moment has not come stays in the Inbox and
costs nothing there. That is what the Inbox is for.

**Dismiss** — you can say what killed it: it shipped some other way, it was
overtaken by a decision, it describes a product that no longer exists. "We are
not doing this now" is a schedule, not a decision; that one gets *leave it*.

The split that matters is not important-vs-unimportant. It is **will anyone
actually do this**, and the honest answer for most of an old Inbox is no.

## 4. One message, one approval

Present all three lists at once. Every promotion gets its Area; every dismissal
gets **one line saying what killed it**. Say the numbers you read in step 1,
because they are the argument.

**Every row carries its title.** A row the reader has to look up is a row they
approve without reading, which is the failure this batch was meant to avoid.

> "Inbox: 13 captures, oldest 40 days, and this board has dropped 50% of
> everything it has decided on.
>
> **Promote (6)** — TP-355 "Retry duplicates the welcome note" → oss,
> TP-352 "Docs search returns nothing for two-word queries" → oss, …
> **Leave (4)** — TP-306 "Split the settings page in two", … : still true,
> no moment yet.
> **Dismiss (3)** — TP-280 "Re-point the webhook at the new queue": the
> re-point it describes was rebuilt in TP-291 "Queue rewrite". …
>
> Objections, or shall I apply it?"

**Wait for a real answer.** Silence is not approval. Both exits are reversible,
so a wrong one is cheap to undo — but a batch nobody read is an Inbox judged by
an agent alone, and what is worth doing is the human's call.

## 5. Apply it

`triage_capture(capture_id, decision, area_id)`, once per capture:
`decision="promote"` with the `area_id` you named, or `decision="dismiss"`,
which ignores `area_id`. A dismissal anyone changes their mind about later is
`decision="restore"`.

Promoting returns the new slice alongside the capture it came from. A capture
has no priority to carry, so if the workspace has a `priority_policy` and you
want the new slice ranked, read that policy — what counts as urgent here is
what a person wrote in their own words, not your sense of it — and set the
priority with `save_slice` on the returned slice.

Then say what you did in one line, with the counts. Not a table of everything.

## Red flags

| You are about to… | Instead |
|---|---|
| Promote everything, because each one is defensible on its own | The drop ratio is the argument against that, and it is on the board |
| Treat dismissal as the failure case | Two in five is the normal share. The row stays readable and restores |
| Promote without an `area_id` | It is refused. `list_areas` first, in step 2 |
| Make a new Area for one capture | A boundary nobody works along is paid for at every later judgement |
| Dismiss because "not now" | That is a schedule. Leave it in the Inbox |
| Ask about each capture in turn | One batch. The per-question cost is why Inboxes rot |
| Write a design while judging | Promote first, empty spec. `designing-a-slice` says what it is |
| Treat an empty Inbox as a problem | It is the normal state of a board someone tends |
