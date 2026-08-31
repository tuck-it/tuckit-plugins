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
  - `constraints` — what you must not get wrong: landmines, invariants, and
    what "done" means. Read this before you touch anything.
  - `area` — where it belongs. **Empty means it is still in the Inbox** — the
    idea is captured but not yet filed. Setting an area files it; clearing the
    area sends it back. Both directions are reversible.
- **Bite** — one implementation step under a slice.
- **Decision canvas** — the questions a slice was designed by, each with the
  options weighed and the one that won. It hangs off the slice, it is
  append-only, and writing the `spec` seals it. A losing branch is kept on
  purpose: it is the only record of what was considered and rejected, and
  nothing in the code will ever say it.

There is no Ticket and no Plan. An untriaged capture is a slice with no area.

A slice also carries two axes that answer different questions, and conflating
them is a bug:

- `status` — the decision a human made: `open`, `shipped`, `dropped`.
  Nothing derives it; nothing else should set it.
- `stage` — what the slice needs next, derived from its own content (see
  "Reading state" below). You never set this — write the spec, add the
  constraints, check off bites, and it follows.

## Reading state (don't scan git)

Start every "where are we" question with `get_project_state` — it returns each
Area's shipped / roadmap breakdown, the Inbox count, and your identity,
instead of you scanning markdown or git history.

For a single slice, read its **derived stage** to know what it needs next
without opening every child:

- `needs_design` — spec is empty; it needs a design.
- `needs_steps` — has a design but no bites.
- `executing` — has bites, some unfinished.
- `ready_to_ship` — all bites done.
- `shipped` / `dropped` — terminal, mirrors `status` once a human has decided.

To learn where work stands, read `stage`. Do not infer progress from
`status` — `status` only ever records the open/shipped/dropped decision.

## The workflow (how work moves)

Every step names the skill that owns it, because reading a step is not doing
it — the skills carry the parts that go wrong.

1. **Capture.** A raw idea or request becomes a **Slice with no area** (the
   Inbox). Anything decided for "later" belongs here rather than in the chat:
   a committed next step filed into an Area, a vaguer idea left unfiled. If it
   is only in the conversation, it is gone when the conversation is.
2. **File it.** Deciding the work is worth doing is what puts it in an
   **Area** — a judgement, not paperwork. `filing-the-inbox` walks a full
   Inbox and proposes the filings in one batch. Reversible in both directions,
   so it is never a one-way door.
3. **Design it** — **`designing-a-slice`**. The questions you weigh and the
   options that lose go on the slice's **decision canvas** as you think, and
   the design that wins goes in the **spec**, which is what moves it past
   `needs_design`. When the answer came in the terminal rather
   than by a click, record it in the same call: an answer nobody wrote down
   reads back afterwards as a question nobody answered.
4. **Break it down** — **`breaking-down-a-slice`**. Constraints first, then
   **Bites** (`needs_steps` → `executing`). Steps need a spec to be steps of,
   and adding them over MCP is refused while the spec is empty.
5. **Do it** — **`executing-a-slice`**, or **`delegating-a-slice`** when the
   bites are mostly independent. Update each Bite's status as you go, and put
   the slice's ref in the commit message: that ref is the only thread running
   from a line of code back to the reason it exists.
6. **Ship it** — **`shipping-a-slice`**.

**The small lane.** A typo, a version bump, a one-line fix: capture it, write
the one line of spec that says what it is, do it, and say which slice it was.
Skipping steps 3 and 4 for work that genuinely has no design in it is correct
and expected. Skipping step 1 is not — that is how a repo fills up with
changes nobody can explain, and it is the failure this whole model exists to
prevent.

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
