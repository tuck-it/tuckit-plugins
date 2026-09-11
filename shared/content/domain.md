# tuckit domain reference

tuckit is where a product's decisions, roadmap and deferred work live. The
codebase is the truth about what the software IS today; tuckit is the record of
what was decided, when, and what is still owed — the reasoning that touched no
files, which is exactly the part git cannot reconstruct. Reach for git to see
what changed; reach for tuckit to see what was decided and what is left.

Every spec is a snapshot of the moment it was written. As a record it does not
go stale, and that is the whole point of keeping it. As a description of
today's code it can, and often has: the work moved on and the spec did not
follow, because it was never meant to. So when a spec and the code disagree,
neither is simply wrong — the code is what shipped, the spec is why someone
meant to. Say that and ask which one is out of date, rather than quietly
editing either to match the other.

The human reads and writes it on the web dashboard; you read and write the same
board over MCP. One database, no sync step — whichever one you look at is
current, so keeping your writes on the board is what keeps it honest.

## Vocabulary

- **Area** — a long-lived responsibility domain (backend, frontend, infra…).
  Areas rarely change; they hold slices.
- **Slice** — the one unit of work. It carries:
  - `spec` — the design doc. Empty means it has not been designed yet.
  - `constraints` — what you must not get wrong: landmines and invariants.
    Read this before you touch anything.
  - `done_when` — what would settle that this slice is done. An OBSERVATION,
    never a command: "pytest -q" is a method and says nothing about whether
    the thing works, while "an expired token returns HTTP 401 rather than a
    tool error inside a 200" can be wrong in a way somebody notices. Write it
    BEFORE you build.
  - `evidence` — what somebody actually saw. It has one writing tool of its
    own, which stamps when, and it is what opens the ship gate.
  - `area` — where it belongs. **Required**: a slice always lives in an Area,
    and there is no such thing as an area-less slice. Moving it to a different
    area is free and reversible.
- **Capture** — an unjudged note: a title and prose, and nothing else. No
  priority, no assignee, no stage, no done_when, because nobody has decided it
  is work and every one of those fields would be a claim nobody made. The
  Inbox holds captures, not slices. A capture has exactly two exits and they
  cost the same: promote it into an Area, where it becomes a Slice **keeping
  its number** (capture TP-375 becomes slice TP-375), or dismiss it. Dismissal
  is soft — the row survives, stays readable, and can be restored. Roughly two
  in five captures end there, so it is the ordinary path, not the sad one.
  Neither exit deletes anything and neither is a one-way door. Promoting
  starts the new slice's spec empty, so the design written later replaces
  nothing.
- **Decisions** — the prose record of how a slice was decided: what was
  chosen, why, what was turned down, and what the choice leans on. It hangs
  off the slice and is append-only: its tool adds to the record and nothing
  rewrites it. What was turned down is kept on purpose — it is the only record of what was considered and
  rejected, and nothing in the code will ever say it. Nothing seals it: a
  direction that changes halfway through the work belongs here too.
- **Relations** — one slice can be recorded as blocking another. Record that A
  blocks B only when B cannot meet its **own done_when** until A ships — a
  claim anyone can open B and check, which "it would be more natural to do A
  first", "they touch the same files" and "B is the follow-up to A" are not.
  Every link carries a written reason: the person deciding later whether to
  remove it was not in your session, and an unexplained link is one nobody
  dares delete, so it outlives its truth. While the blocker is open, the
  blocked slice is listed apart from the roadmap so you do not pick it up as
  the next thing to do, and it comes back on its own the moment the blocker
  ships or is dropped — nothing stores "blocked", it is worked out on every
  read. Shipping is refused while something still blocks the slice. A link is
  reversible — unlinking removes it — so it needs nobody's approval to create;
  but a wrong one hides real work from the roadmap until the blocker ships,
  and the web does not yet show blocked-ness on screen. That is why the reason
  is not optional.

There is no Ticket, no Plan and no step layer. An untriaged capture is a
**Capture**, not a slice with something missing — a different object, which is
what makes the choice between "I noticed something" and "this is work" a
choice somebody makes rather than a field left unset. When one verb covered
both, 10 of the 16 things in one production Inbox had a full spec written into
them, and the board reported unjudged observations as needing a done_when.

A slice also carries two axes that answer different questions, and conflating
them is a bug:

- `status` — the decision a human made: `open`, `shipped`, `dropped`.
  Nothing derives it; nothing else should set it.
- `stage` — what the slice needs next, derived from its own content (see
  "Reading state" below). You never set this — write the spec, write the
  done_when, record the evidence, and it follows.

## Reading state (don't scan git)

Start every "where are we" question with `get_project_state` — it returns each
Area's shipped / roadmap breakdown, the Inbox count (captures waiting, not
slices), and your identity, instead of you scanning markdown or git history.

For a single slice, read its **derived stage** to know what it needs next
without reading the whole slice:

- `needs_design` — spec is empty; it needs a design.
- `needs_done_when` — designed, but nobody has said what would settle it.
- `executing` — the target is set and nothing has met it yet.
- `ready_to_ship` — evidence recorded.
- `shipped` / `dropped` — terminal, mirrors `status` once a human has decided.

To learn where work stands, read `stage`. Do not infer progress from
`status` — `status` only ever records the open/shipped/dropped decision.

## The workflow (how work moves)

Every step names the skill that owns it, because reading a step is not doing
it — the skills carry the parts that go wrong.

1. **Capture.** A raw idea, a request, something you noticed becomes a
   **Capture** in the Inbox: a one-line title in the words you would say it,
   and what you SAW in prose. Nothing else — you are not claiming it is work
   yet, and there is deliberately nowhere to write a design. If it is only in
   the conversation, it is gone when the conversation is.
2. **File it.** Deciding the work is worth doing is what promotes the capture
   into an **Area**, where it becomes a Slice keeping its number — a
   judgement, not paperwork. Dismissing it costs exactly the same, and both
   exits are reversible, and leaving a capture where it is until its moment
   comes is a third real answer. `filing-the-inbox` walks a full Inbox and
   proposes all three in one batch.
3. **Design it** — **`designing-a-slice`**. Each decision you reach goes into
   the slice's **decisions** as prose while you think, and the design that
   wins goes in the **spec**, which is what moves it past `needs_design`. Then
   write the **done_when**: what would settle that this is finished. Writing
   it before you build is the whole point — one written afterwards is a
   description of what you did, which is the one thing it must not be.
4. **Do it** — **`executing-a-slice`**, or **`delegating-a-slice`** for work
   that splits cleanly. Treat the done_when as the target you have to meet,
   and put the slice's ref in the commit message: that ref is the only thread
   running from a line of code back to the reason it exists.
5. **Show it was met** — **`verifying-before-claiming`**, after a reviewer has
   seen the branch and not before, because evidence about a branch that then
   changes describes something that no longer exists. Write down what you
   actually SAW, and name what you did not check.
   This is what moves the slice to `ready_to_ship`; until it exists the board
   refuses to ship, and that refusal is the point.
6. **Ship it** — **`shipping-a-slice`**.

**The small lane.** A typo, a version bump, a one-line fix: it is already
judged, so put it straight into an Area as a slice, write the one line of spec
that says what it is, do it, and say which slice it was. Skipping the design
for work that genuinely has none in it is correct and expected. Skipping the
board is not — that is how a repo fills up with changes nobody can explain,
and it is the failure this whole model exists to prevent.

## Asking your partner something

You can write ten thousand lines in an afternoon; they cannot outsource
understanding what those lines commit them to. Their judgement is the scarce
thing in the session, and a decision made without understanding is not one.

So a message asking them to decide is finished only when they can answer it
without leaving the message:

- **A ref never travels alone.** Give it its title, and a line of what it is.
  A ref is an address, not a meaning, and a row they have to look up is a row
  they approve without reading.
- **Options say what changes for them**, not what you would build.
- **Spell out any identifier they did not introduce** — a ref, a stage name, a
  flag, a file they have not seen. This is the checkable version of "write it
  more simply", which is not something the writer can measure.

Length follows what is at stake, not what you happen to know. Reversible
decisions get one scannable line each, batched. Irreversible ones get what
breaks and what cannot be undone, first.

Short is not the axis. A bare "TP-1?" is the other end of the same failure:
told to be brief, an agent compresses into identifiers and abbreviations. The
axis is whether they can answer from the message.

**Do not ask whether they understood.** That moves the cost of understanding
onto them, and people say yes to it.

## Tools

The exact MCP tool names and their arguments are whatever the tuckit server
exposes in this session — treat that list as authoritative and discover tools
there. This document intentionally names only `get_project_state`, the stable
entry point, so it can't fall out of date.
