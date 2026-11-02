---
name: reviewing-a-change
description: "Use when a change needs a reviewer before it goes further — a whole branch before its pull request, or any range someone asks about — and when review feedback arrives from a reviewer subagent, a teammate, or a PR comment. Dispatches a reviewer with only the change and the requirements, then checks each finding against the code and routes every one so none is lost in the chat log."
---

# Reviewing a Change

Two halves: getting a review, and acting on one. Both apply whether the
reviewer is a subagent you dispatched or a teammate commenting on the PR.

Vocabulary: `${CLAUDE_PLUGIN_ROOT}/content/domain.md`.

## Getting a review

A review is a subagent you dispatch, not a pass over your own diff. Give it the
change and the requirements, and **never your session history**: a reviewer who
can see how you got here reviews your reasoning instead of the change.

Write the diff to a file first, so it never passes through your context:

```bash
BASE=$(git merge-base <base-branch> HEAD)   # never HEAD~1
OUT="$WORK/review-$(git rev-parse --short "$BASE")..$(git rev-parse --short HEAD).diff"
{ echo "## Commits";       git log --oneline "$BASE"..HEAD
  echo; echo "## Files changed"; git diff --stat "$BASE"..HEAD
  echo; echo "## Diff";     git diff -U10 "$BASE"..HEAD
} > "$OUT"
```

`$WORK` is any ignored scratch path. For uncommitted work, use
`git diff -U10 HEAD` and leave the head blank.

Dispatch with [reviewer-prompt.md](reviewer-prompt.md). Hand it the diff path,
the slice ref (it reads the spec and done_when itself), and the slice's
`constraints` copied verbatim. Do not pre-judge: never tell a reviewer to ignore
something or cap a severity.

Name the model. A branch review gets the most capable one available; a small
fix round gets a cheaper one. An omitted model silently inherits the session's.

The verdict is information, not an instruction. What happens to the branch is
decided by you and the people you work with.

## Acting on a review

Read the whole review before acting on any item; item 4 can change item 2.
Then for each finding:

1. **Check it against the code.** The reviewer read a diff; you can read the
   repository. Is it true here? Does fixing it break something? Was there a
   reason for the current code?
2. **If any item is unclear, ask about all the unclear ones in one message
   before fixing anything.** Findings interlock.
3. **Fix, push back, or route it** — see below.

No performative agreement ("You're absolutely right!", thanks). Restate the
point technically, push back with evidence, or just fix it. When your pushback
turns out wrong, say so in one sentence and fix it.

Fix blocking items first (breakage, security, data loss), then simple ones,
then complex ones, testing after each. Before building out something a finding
calls incomplete, check whether anything calls it.

When a disagreement is about direction rather than code, it belongs to the
person who owns the slice's promise. Bring them in.

### Where each finding goes

Every finding leaves through one of four doors. A finding that only appears in
your closing message has gone nowhere.

1. **Fix it on this branch** — it is Critical or Important and inside this
   change, or it is inside this change and fixing it is smaller than writing it
   down.
2. **Push back** — you checked and it does not hold here. If the next reviewer
   would raise it again, it also goes in the note below.
3. **One line in a note** — true, but nobody will act on it. All of these go in
   a single `add_note` on the slice, not one each.
4. **Propose a capture** — someone will actually pick it up later. Collect these
   for the end-of-session batch; nothing is created until the person approves.

Choose between 3 and 4 by asking whether anyone **will** do it, not whether
someone should. Read `get_project_state` before you answer: when
`inbox.open_count` is 20 or more, or `totals.drop_ratio` is 0.5 or higher, a
finding only becomes a capture if you can name who will do it and when. A board
once reached 140 open slices this way and 78% of them were closed unread.

A rule the next person must not break goes in `constraints` as well.

With no slice behind the review, door 3 has nowhere to land: send those items
to door 4 or put them to the person.

### PR comments

Reply inside the comment's thread, not as a new top-level comment:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="…"
```

If the fixes change what the recorded evidence describes, record the evidence
again before asking for another look.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `requesting-code-review`
and `receiving-code-review`, merged and rewritten so every finding lands on the
board or in the code.
