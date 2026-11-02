# tuckit domain reference

tuckit is where a product's decisions, roadmap and deferred work live. The
codebase is the truth about what the software IS today; tuckit is the record of
what was decided, when, and what is still owed — the reasoning that touched no
files, which is exactly the part git cannot reconstruct.

Every record here is a snapshot of the moment it was written. When a spec and
the code disagree, neither is simply wrong — the code is what shipped, the spec
is what someone agreed to. Say that and ask which one is out of date, rather
than quietly editing either to match the other.

People read and write the board on the web; agents read and write the same
board over MCP. One database, no sync step.

## Who decides what

As models get better, the person's job narrows to three things, and the
workflow is built so those are the only places it stops for one:

- **Direction** — which work exists and how much it matters: slices, captures,
  priorities. People set it, mostly on the web.
- **The promise** — what a slice will deliver and how anyone would know it did:
  its `spec` and its `done_when`. The developer who designs the slice approves
  both, once, and owns that promise.
- **Confirmation** — a teammate reviews the pull request. The merge is the
  confirmation; the slice is shipped once it has landed.

Everything between the promise and the pull request — how to build it — is the
agent's call. It is recorded as decisions, shown before the code is written,
and open to challenge at any point, but it does not wait for a yes.

## Vocabulary

- **Area** — a long-lived responsibility (billing, the public site, …). Areas
  rarely change; they hold slices.
- **Slice** — the one unit of work. It carries:
  - `spec` — **what** is being built and **why**, as the slice's designer
    agreed it. Not how. Empty means nobody has agreed a promise yet.
  - `done_when` — the other half of the promise: the observation that would
    settle it. An OBSERVATION, never a command. "pytest -q" is a method and
    says nothing; "an expired token returns HTTP 401 rather than a tool error
    inside a 200" can be wrong in a way somebody notices.
  - `decisions` — the append-only record of how it was decided and how it is
    being built: what was chosen, why, what was turned down, and what the
    choice leans on. The design lives here.
  - `constraints` — what a later agent must not get wrong: landmines and
    invariants. Read this before you touch anything.
  - `evidence` — what somebody actually saw. It is what opens the ship gate.
  - `assignee` — who holds the slice right now. On a shared board this is how
    two agents avoid building the same thing.
  - `area` — required. A slice always lives in an Area.
- **Capture** — an unjudged note: a title and prose, nothing else. The Inbox
  holds captures. A capture has two exits that cost the same: promote it into
  an Area, where it becomes a Slice **keeping its number**, or dismiss it. Both
  are reversible and neither deletes anything. Roughly two in five captures are
  dismissed on a board somebody tends; that is the ordinary path.
- **Relations** — one slice can block another. Record that A blocks B only when
  B cannot meet its **own done_when** until A ships, and always say why. While
  the blocker is open, B is listed apart from the roadmap, and shipping B is
  refused.

A slice has two axes, and conflating them is a bug:

- `status` — what a person decided: `open`, `shipped`, `dropped`.
- `stage` — what the slice needs next, derived on every read:
  - `needs_design` — no spec yet: the promise has not been agreed.
  - `needs_done_when` — a spec but no done_when: half a promise.
  - `executing` — the promise is set and nothing has met it yet.
  - `ready_to_ship` — evidence recorded.
  - `shipped` / `dropped` — terminal.

Read progress from `stage`, never from `status`.

## Reading state

Start every "where are we" question with `get_project_state`, not with git or
markdown files.

## The workflow

1. **Capture** — something noticed becomes a capture: a title in the words you
   would say it, and what you saw. It claims nothing.
2. **Direction** — someone promotes it into an Area, dismisses it, or leaves it
   for later. **`tending-the-board`** proposes all of that in one batch, and
   proposes what to close when the roadmap is fuller than anyone reads.
3. **Promise, then design** — **`designing-a-slice`**. A vague request is
   questioned until it can be written as a spec and a done_when; the designer
   approves both; the agent designs and records its decisions.
4. **Build, verify, open the PR** — **`building-a-slice`**, with
   **`reviewing-a-change`** before the evidence is written.
5. **Confirm** — a teammate reviews the PR. Once it is merged, the slice is
   shipped.

At the end of a session, **`reconciling-the-board`** closes what became untrue
on the slices you hold.

**The small lane.** A typo, a version bump, a one-line fix: it still gets a
slice, but the agent writes the one-line spec and the done_when itself and does
not stop to ask. The pull request review is the only human step.

## Working on a shared board

- Take a slice by assigning it to yourself before you build it.
- A slice someone else holds is theirs. Read it freely; do not build it, change
  its promise, or close it. Say who holds it and stop.
- Reconcile only what you hold. Proposals about someone else's slice name them.

## Asking a person something

Their judgement is the scarce thing in the session. A message asking them to
decide is finished only when they can answer it without leaving the message:

- **A ref never travels alone.** Give it its title.
- **Options say what changes for them**, not what you would build.
- **Spell out any identifier they did not introduce.**

Length follows what is at stake. Reversible decisions get one line each,
batched. Irreversible ones lead with what breaks and what cannot be undone.

## Tools

The exact MCP tool names are whatever the tuckit server exposes in this
session. This document names only `get_project_state`, the stable entry point,
so it cannot fall out of date.
