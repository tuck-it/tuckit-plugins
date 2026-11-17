---
name: building-a-slice
description: "Use when a tuckit slice has an approved promise (stage reads executing) or when picking up a half-built one in a fresh session. Builds against the done_when, gets the branch reviewed, records what was actually observed, opens the pull request, and marks the slice shipped once the PR is merged."
---

# Building a Slice

The promise is set and approved: the spec says what, the done_when says how
anyone would know. Make that true, show that it is, and hand a teammate a pull
request they can confirm. How you build it is yours.

Reference: `${PLUGIN_ROOT}/content/domain.md`.

## 1. Load it and check whose it is

`get_slice(<ref>, with_activity=true)`. Read the spec, the constraints (binding;
they win over the spec), the done_when, the decisions, the latest notes, and
the `Approved:` line: that person owns the promise.

- **Held by someone else**: say who and stop. If they asked you to take it
  over, or it has clearly stalled and the person you work with says to,
  `save_slice(assignee="me", handover_reason="…")`.
- **Held by nobody**: `save_slice(assignee="me")`.
- **Stage is not `executing`**: the promise is missing or not approved. Go back
  to **`designing-a-slice`**.

Ask once whether you could meet the done_when and still have built the wrong
thing. If yes, say so now.

## 2. Show how you will build it

Before the first edit, send one short message: the shape of the change, the
files it touches, and the close calls, each close call also recorded with
`append_decision`. Skip it if this session already sent one. Do not wait for an
answer.

## 3. Build

Work on a branch, never on the default branch without the person's say-so.
Follow the repository's own conventions for commits, tests and tooling. Put the
slice's ref in commit subjects or the PR title so the code leads back to the
reason.

The board hears from you when something changed, not to narrate progress:

- **A design choice made at the keyboard**: `append_decision`.
- **A landmine**: `constraints`, and `add_note` if it cost real time.
- **Something you are not doing now**: collect it for
  **`reconciling-the-board`**. Not a `TODO`, not a line in chat.
- **Another slice must ship first**: `link_slices` with a `blocks` note.
- **The done_when turns out wrong**: stop and ask the person who approved it.
  Changing it clears the approval, and quietly lowering a target you could not
  meet is the one failure this field exists to prevent.

When you are stuck on the same failure and further attempts are not changing
anything, stop, `add_note` what you hit, and ask.

## 4. Review the branch

Use **`reviewing-a-change`** on the whole branch before writing evidence:
evidence about a branch that then changes is evidence about something that no
longer exists. If you cannot dispatch a reviewer here, say so in one line; the
teammate's review still happens.

## 5. Meet the done_when and write down what you saw

Do what the done_when describes, on the surface it names, on the code that will
land. Then `record_verification(slice_id, evidence)`, only if every part of it
was observed. If part cannot be met yet, record nothing: `add_note` what was and
was not met, and tell the person who approved the promise.

**Write what you saw, not what you ran**, and name what you did not check:

```
Two browsers, one with the modal open; after the other saved, the modal
showed the new title in 4.1s.
Test suite at the repo root: 2491 passed.
Not checked: Safari.
```

A command that exits 0 is not an observation. Read the output. If you cannot
check something here (no browser, no production access), say so plainly. When
the screen is the only witness, attach a picture with `create_image_upload`.

If the evidence stops being true, `record_verification(evidence="")` takes the
slice back to `executing`.

## 6. Open the pull request

Push and open a PR, following the repository's PR template if it has one. In
the body: the slice ref and title, the done_when, the evidence, a pointer to the
slice's decisions so the reviewer can challenge the design, and what you did not
check. `add_note` the PR link on the slice and give the person the link. Review
comments go through **`reviewing-a-change`**.

## 7. After the merge

When you see the PR merged (merged, not approved),
`save_slice(slice_id, status="shipped")`. The merge was the confirmation, so do
not ask again. This applies to anyone who sees the merge, not only the builder.

Two things refuse that call: no evidence, and another slice still blocking this
one. For a block, read the link's note; if it is no longer true, unlink it. The
`over_block` and `over_unverified` overrides are for a person who has looked and
decided, not for clearing an error.

If the PR is closed without merging, the slice stays open. Dropping it is the
holder's decision.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent): `executing-plans`, `finishing-a-development-branch` and
`verification-before-completion`, merged and rewritten so the work ends at a
pull request a teammate confirms.
