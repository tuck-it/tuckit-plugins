---
name: breaking-down-a-slice
description: "Use when a tuckit slice has an approved spec and needs implementation steps — stage reads needs_steps — before touching any code. Writes the constraints and an ordered bite checklist onto the slice itself. In this workspace it replaces superpowers:writing-plans: the board is the plan, so there is no plan file."
---

# Breaking Down a Slice

Write the steps for an engineer who is skilled, knows nothing about this
codebase, and has questionable taste. In practice that engineer is a fresh agent
session that will read **one bite and its body**, and little else. Write for
that reader: which files, what test, how to verify, what not to do.

**Announce at start:** "I'm using breaking-down-a-slice to turn the spec into
steps on the board."

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

## 0. Load the slice

`get_slice(<ref>)`. Confirm where it actually is:

- `needs_design` — stop. There is no approved design to break down; use
  `designing-a-slice`.
- `needs_steps` — this skill.
- `executing` — bites already exist. Read them before adding; extend the
  checklist, never restate it.

## 1. Constraints first — the highest-value text you will write

`update_slice(slice_id=…, constraints=…)` before you write a single bite.

What belongs there: the landmine (the thing that looks right and is wrong), the
invariants that must still hold afterwards, and what "done" actually means for
this slice — which suite, which surface checked how, which environment.

Not a restatement of the spec.

Do it first because everything below is disposable: bites get checked off and
stop being read. Constraints outlive the work, and every agent that opens this
slice is told to treat them as binding.

## 2. Map the files before you write tasks

Which files get created, which get modified, what each is responsible for. This
is where the decomposition is actually decided.

- One clear responsibility per file. Prefer focused files — you reason better
  about code you can hold in context at once.
- Files that change together live together. Split by responsibility, not by
  technical layer.
- Follow the codebase's existing patterns. Do not unilaterally restructure; a
  split is fair game only for a file you are already changing.

## 3. Right-size the bites

A bite is **the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate.**

- Fold setup, configuration, scaffolding, and docs into the bite whose
  deliverable needs them.
- Split only where a reviewer could meaningfully reject one bite and approve its
  neighbour.
- Every bite ends in something independently testable.

Inside a bite, the steps are one action each (2–5 minutes): write the failing
test → run it and watch it fail → implement the minimum → run the tests →
commit.

## 4. Write bites that survive being read alone

`add_bites(slice_id=…, bites=[{title, body}, …])`, in execution order.

- **title** — imperative, names the deliverable.
- **body** — markdown, and it *is* read back over MCP, so it is the working
  instruction set: files to touch, the test-first cycle, how to verify, and any
  non-obvious context.

If a body only makes sense to someone who just read the whole spec, it is too
thin. The reader will not have read the whole spec.

## 5. One slice, one plan

If the spec really needs several independent plans — subsystems that ship and
verify separately — that is several slices, not one slice with forty bites.
Create the siblings now, give each its own spec, and have each spec name the
others by ref in one line. A checklist nobody can finish in one branch stops
telling you anything.

## 6. Read it back, then hand off

`get_slice(<ref>)` and read the `## Steps` section the way the executing agent
will see it. Then offer the two execution paths:

- **This session** — you already hold the context.
- **A fresh session** — usually better: it starts from the board, which is also
  the first real test of whether the bites read standalone.

Terminal state: `executing-a-slice`.

## No plan file

Upstream writes plans to `docs/…/plans/YYYY-MM-DD-*.md`. Do not. The plan is the
slice's constraints plus its bites, where the human already looks and where the
next session already reads. A plan file is a copy, and the copy is what rots.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `writing-plans`, rewritten
so the plan is the board.
