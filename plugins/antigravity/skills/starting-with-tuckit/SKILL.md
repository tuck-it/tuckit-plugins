---
name: starting-with-tuckit
description: "Use once when a user is starting a new or existing project with tuckit for the first time and the live board has no Areas. Reads the project and intent, helps the user choose the initial responsibility-based Areas, and creates only the first real Slices. Do not use for new ideas inside an already-organised board."
---

# Starting With Tuckit

Give an Area-less tuckit board its first truthful shape. This is not project
scaffolding and it is not installation: tuckit and its MCP connection already
exist. The output is a small, approved set of Areas and the work that is real
right now, ready for `designing-a-slice`.

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

<HARD-GATE>
Read live board state before asking a question. If state cannot be read, or if
the board already has even one Area, do not create or modify anything in this
skill. If the board is empty, do not create anything until the human has seen
and approved the complete Area and Slice proposal.
</HARD-GATE>

## Checklist

Create a task for each item and complete them in order:

1. **Confirm the board is unstarted** — read state and stop safely if it is not
2. **Read and form a draft** — intent, project evidence, candidate Areas and Slices
3. **Interview only consequential gaps** — one question at a time
4. **Present the whole proposal** — Areas and Slices as separate blocks
5. **Create after approval** — Areas, then Slices, then evidence notes
6. **Hand back** — the human reads the board before choosing a Slice to design

## 1. Confirm the board is unstarted

Call `get_project_state` and `list_areas` before reading the repo or asking the
human anything.

- If either call fails, stop. Say that tuckit state could not be established;
  do not infer emptiness from an unavailable connection.
- If `list_areas` returns even one Area, this board has already been organised.
  Do not top it up or reinterpret its absences. Treat the user's project idea as
  work on the existing board and use `designing-a-slice` instead.
- Continue only when both reads succeed and there are no Areas.

This state check, not memory or the skill description, is the safety boundary.

## 2. Read and form a draft

Start with the user's first request: it is evidence of the project they mean
and, for a new or quiet project, the first real Slice they want to design.

Then read whatever project evidence exists. Keep its two uses separate:

| Evidence | What it may support |
|---|---|
| Directory structure and recent commits | A hypothesis about enduring responsibilities worth asking about |
| Current branch, unmerged commits, open PRs, uncommitted changes | Work genuinely in flight, and therefore a Slice candidate |
| TODO/FIXME comments, issue backlogs, someday notes | Nothing; do not import a backlog |

No repository or VCS history is a normal greenfield case. Build the draft from
the user's intent rather than manufacturing the structure of a “typical”
project.

Draft the complete Area set and Slice candidates before interviewing. The human
should correct a reasoned proposal, not supply a taxonomy from a blank page.

### What an Area is

An Area is a durable responsibility somebody can say is theirs. A directory,
language, frontend/backend layer, deployment target, or monorepo boundary is not
an Area by itself. Those facts are prompts to investigate ownership and
responsibility, never automatic cuts.

Do not carry project archetypes or a fixed Area menu between projects. Derive
the cut from this user's intent and this project's evidence.

Bias low: one Area is valid. Split only when there is evidence of an independent
responsibility, owner, or operating/change cycle. There is no hard Area count,
but every proposed Area beyond three must state the independent responsibility
that makes merging it misleading.

## 3. Interview only decisions that change the board

Ask a question only when two plausible answers would produce two different Area
sets. Before asking, be able to name both resulting boards. Otherwise the
question is context gathering that does not earn the user's time.

- Ask one question per message and show the evidence that created it.
- Prefer a concrete choice when the alternatives are known; use an open question
  when the project evidence does not justify inventing alternatives.
- Do not run a standard questionnaire. Team size, monorepo plans, release
  cadence, or infrastructure ownership matter only when the answer changes the
  proposed responsibility boundaries.
- Update the draft after every answer. Stop when no unresolved answer would
  change the Area set.

Questions are sequential; approval is not. Areas define each other's borders,
so the human must see the complete set together before choosing it.

## 4. Present the whole proposal

Present two visibly separate blocks:

1. **Areas** — name, durable responsibility, and the user/repo evidence for the
   boundary.
2. **Work that is real now** — Slice title, destination Area, and evidence. For
   a new or quiet project, this is the user's initial goal. For an active repo,
   use only current branch/PR/uncommitted evidence and show no more than the five
   strongest candidates; say which evidenced candidates were omitted.

Ask for one approval covering both blocks. If the human changes anything,
revise and present the complete proposal again. Do not call `create_area`,
`create_slice`, or `add_note` before approval.

## 5. Create after approval

Create in dependency order:

1. `create_area(name, description)` for each approved Area. Describe the
   responsibility in the human's language, not as a directory inventory.
2. `create_slice(title, area_id=...)` for each approved piece of work, with the
   spec left empty so its stage is truthfully `needs_design`.
3. `add_note(...)` to an in-flight Slice with its branch, PR, or working-tree
   evidence. Observations belong in notes; design never comes from commit
   messages.

For in-flight work, pass a stable `external_key` such as the PR URL or
`start:<branch>` so a retry cannot duplicate it. A new or quiet project gets
exactly one first-goal Slice rather than an invented starter roadmap.

If any creation call fails, stop immediately. Report exactly which approved
items now exist and which were not attempted. Do not retry or continue from a
stale view of the board; a later recovery must read current state first.

## 6. Hand back

Ask the human to inspect the board that now exists. Explain that empty specs are
intentional: the board knows what is real, but the design has not been agreed
yet.

Do not chain onward without that review. When the human chooses the first Slice,
use `designing-a-slice`.

---

Unlike the Slice pipeline skills, this runs at the one moment when there was no
Area for a Slice stage to live under.
