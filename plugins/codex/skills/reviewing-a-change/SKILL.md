---
name: reviewing-a-change
description: "Use when a change needs a reviewer before it goes further (your own branch before its pull request, or any range someone asks about), when review feedback arrives from a reviewer subagent, a teammate or a PR comment, and when a person wants help reviewing a teammate's pull request. Reviews against the slice's promise and routes every finding so none is lost in the chat log."
---

# Reviewing a Change

Three cases: getting a review of your own change, acting on a review, and
helping a person review someone else's pull request.

Reference: `${PLUGIN_ROOT}/content/domain.md`.

## Getting a review

A review is a separate reviewer (a subagent you dispatch), not a pass over your
own diff. Give it the change and the requirements, **never your session
history**: a reviewer who can see how you got here reviews your reasoning
instead of the change.

Dispatch with [reviewer-prompt.md](reviewer-prompt.md). Hand it the base and
head of the change (the base is where the branch forked, not the previous
commit), the slice ref, and the slice's `constraints` verbatim. Do not
pre-judge: never tell a reviewer to ignore something or cap a severity. Pick a
capable model for a whole branch and a cheaper one for a small fix round.

The verdict is information, not an instruction.

## Acting on a review

Read the whole review before acting on any item. Then for each finding:

1. **Check it against the code.** Is it true here? Does fixing it break
   something? Was there a reason for the current code?
2. **If anything is unclear, ask about all of it in one message** before fixing.
3. **Fix it, push back with evidence, or route it** (below).

Restate the point technically or just fix it; no performative agreement. When
your pushback turns out wrong, say so in one sentence and fix it. A
disagreement about direction rather than code belongs to the person who
approved the promise.

### Where each finding goes

A finding that only appears in your closing message has gone nowhere.

1. **Fix it on this branch**: it is serious and inside this change, or fixing
   it is smaller than writing it down.
2. **Push back**: you checked and it does not hold here.
3. **One line in a note**: true, but nobody will act on it. All of these go in
   a single `add_note` on the slice.
4. **Propose a capture**: someone will actually pick it up. Collect these for
   the end-of-session batch in **`reconciling-the-board`**.

Choose between 3 and 4 by asking whether anyone **will** do it, not whether
someone should. A rule the next person must not break also goes in
`constraints`.

Reply to a PR comment inside its thread, not as a new top-level comment. If
the fixes change what the recorded evidence describes, record it again.

## Reviewing a teammate's pull request

The person is the reviewer; you help them see it. Their approval is the
confirmation, so you never approve or merge on their behalf.

1. Find the slice from the PR (its ref in the title, body or commits) and read
   it with `get_slice`. Review against its spec, done_when and decisions. If
   there is no slice, review against what the PR says it does, and say so.
2. Dispatch a reviewer as above, or read the diff yourself if you cannot.
3. Give the person a short verdict first: does the change keep the promise,
   and does the evidence actually show it? Then the findings that matter, each
   with file and line, worst first. Leave out style the repository's tools
   already enforce.
4. Post review comments only when the person asks, in their words.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent): `requesting-code-review`
and `receiving-code-review`, merged and rewritten so every finding lands on the
board or in the code.
