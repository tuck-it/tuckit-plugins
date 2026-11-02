---
name: building-a-slice
description: "Use when a tuckit slice has an approved promise — stage reads executing — or when picking up a half-built one in a fresh session. Builds against the done_when, gets the branch reviewed, records what was actually observed, opens the pull request, and marks the slice shipped once the PR is merged."
---

# Building a Slice

The promise is set: the spec says what, the done_when says how anyone would
know. Your job is to make that one sentence true, show that it is, and hand a
teammate a pull request they can confirm.

Vocabulary: `${CLAUDE_PLUGIN_ROOT}/content/domain.md`.

## 1. Load it and check whose it is

`get_slice(<ref>, with_activity=true)`. Read the spec, the constraints (binding;
they win over the spec), the done_when, the decisions, and the latest notes.

Its `Assignee:` line says who holds it; `get_project_state` says who you are.

- **Held by someone else** → say who holds it and stop. Do not build it, even
  if something else about the slice also looks wrong: the holder is the first
  thing to report.
- **Held by nobody** → `save_slice(assignee="me")`.
- **No done_when** → the stage reads `needs_done_when`, not `executing`. Go back
  to `designing-a-slice`: a target written after the work is a description of
  the work.

Before the first change, `git log --oneline -12 -- <files you will touch>`.
Refs in those subjects are decisions someone already made about this code;
`get_slice` on one is the reasoning, including what was turned down.

Then ask once whether you could meet the done_when and still have built the
wrong thing. If yes, say so now.

## 2. Show how you will build it

Before the first edit, send one short message: the shape of the change, the
files it touches, and the close calls, each close call also recorded with
`append_decision`. Skip this only if this session already sent that message.
Decisions on the board do not count; the person is reading the conversation.
Do not wait for an answer.

## 3. Build

Work on a branch in its own worktree; parallel sessions are normal and the main
checkout is not yours. Never build on main without the person's say-so.

- Commit as you go with the slice's ref in the subject (`TP-42: …`). That ref is
  the thread from a line of code back to the reason for it.
- Run the project's real check, not the subset that is fast. A suite scoped to
  one directory skips the wiring guards above it.
- Your task breakdown is yours. It does not go on the board.

The board hears from you when something changed, not to narrate progress:

- **A design choice made at the keyboard** → `append_decision`.
- **A landmine** → `constraints`; if it cost real time, `add_note` too.
- **Something you are not doing now** → collect it for the end-of-session
  batch in `reconciling-the-board`. Not a `TODO`, not a line in chat.
- **Another slice must ship first** → `link_slices` with a `blocks` note.
- **The done_when turns out wrong** → stop and ask the person who approved it.
  Changing it is changing the promise. Quietly lowering a target you could not
  meet is the one failure this field exists to prevent.

Stop and ask when you are blocked, when the spec is unclear, or after three
fixes for the same failure have not held — by then the approach is the likelier
thing that is wrong. `add_note` what you hit before you stop.

## 4. Review the branch

Use `reviewing-a-change` on the whole branch before writing evidence. Evidence
recorded against a branch that then changes is evidence about something that no
longer exists.

If you cannot dispatch a reviewer, say so in one line: "No subagents here, so
this branch goes to the PR without an agent review." The teammate's review still
happens.

## 5. Meet the done_when and write down what you saw

Do the thing the done_when describes, on the surface it names, now, on the code
that will land. Then `record_verification(slice_id, evidence)` -- only if every
part of it was observed. If part of it cannot be met yet, record nothing:
`add_note` what was and was not met, and tell the person who approved the
promise. Evidence for half a promise moves the slice to `ready_to_ship` and
tells the next reader it is done.

**Write what you saw, not what you ran.**

```
two shells, one with the modal open; after the other saved, the modal
showed the new title in 4.1s and no skeleton flashed.
409 on a stale save, with the "keep mine" button rendered.
pytest -q at the repo root: 2491 passed.
Not checked: Safari.
```

This product's own history has suites that asserted nothing, a guard that
printed "0/2 covered" and stayed green, and an absent row read as a pass. Every
one of them had a command that exited 0. So:

- Read the output and the exit code; a pipe can hide the exit code.
- An endpoint returning 200 says nothing about the screen a person uses.
- A green run on your local database is evidence about your machine.
- **Name what you did not check.** It is the most useful sentence in the field.

If you cannot run the check at all here (no browser, no access to production),
say so plainly rather than describing it as checked. If no one in this
environment ever could, that gap is worth a capture.

When the screen is the only witness, put a picture in the evidence with
`create_image_upload`. Otherwise, paste text.

If the evidence stops being true, `record_verification(evidence="")` takes the
slice back to `executing`.

## 6. Open the pull request

Push the branch and open a PR against the base it forked from, following the
repo's PR template if there is one. In the body:

- the slice ref and title, and the done_when;
- the evidence, as recorded;
- a link to the slice's decisions, so the reviewer can challenge the design,
  not only the diff;
- what you did not check.

`add_note` the PR link on the slice, then give the person the link. This is
where your part ends: a teammate's review is the confirmation. Keep the
worktree; review fixes happen there.

Review comments that come back go through `reviewing-a-change`. If a fix
changes what the evidence describes, record it again.

## 7. After the merge

When the PR is merged — you see it merged, not that it was approved — run the
full suite on the merged result if you can, then
`save_slice(slice_id, status="shipped")`. The merge was the confirmation, so do
not ask again.

Two things refuse that call: no evidence, and another slice still blocking this
one. For a block, read the link's note; if it is no longer true, unlink it. The
`over_block` and `over_unverified` overrides are for a person who has looked and
decided, not for clearing an error.

Then remove the worktree if you created it, and close with one line: which
slice shipped, and what this session left in the Inbox.

If the PR is closed without merging, the slice stays open. Dropping it is the
holder's decision.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `executing-plans`, `finishing-a-development-branch` and
`verification-before-completion`, merged and rewritten so the work ends at a
pull request a teammate confirms.
