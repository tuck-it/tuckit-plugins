---
name: requesting-a-review
description: "Use when work needs a reviewer's eyes before it goes further — one bite in a checklist, a whole branch before merge, or any range someone asks about. Dispatches a reviewer subagent with precisely crafted context and hands the findings to receiving-a-review."
---

# Requesting a Review

## Overview

A review is a subagent you dispatch, not a pass you make over your own diff. You
construct exactly what the reviewer needs — what was requested, the diff as a
file, the constraints that bind the work — and **never hand it your session
history**. A reviewer that can see how you got here reviews your reasoning; a
reviewer that sees only the change reviews the change.

**Core principle:** requirements in, diff in, findings out. You choose the scope
and the model; the reviewer decides nothing about what happens next.

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

**Announce at start:** "I'm using requesting-a-review to review <what>."

## Scopes

Three scopes, and the scope decides what the reviewer is told, what it grades
against, and how wide its judgment reaches.

| Scope | Under review | Requirements | Verdict it answers |
|---|---|---|---|
| `bite` | one bite of a slice's checklist, with the implementer's report | the bite's body, plus the slice's constraints | may the next bite be built on this? |
| `branch` | every commit on the branch, before it lands | the slice's spec, its Constraints binding | may this merge? |
| `ad-hoc` | whatever range someone asks about | whatever was stated, if anything | what is wrong with this? |

**Who calls which.** `bite` and `branch` are called by the skill running the
work — a bite gate after each bite, a merge gate once the branch is complete.
`ad-hoc` is nobody's pipeline: it is the scope for "review this for me," and it
is why this skill works with no slice at all.

A `branch` review is the last gate. Nothing broader follows it, so it carries
what a bite-scoped review structurally cannot see: integration between the
bites, duplication across them, and requirements that fell between two of them.
Do not weaken it into a bigger bite review.

Both prompt templates carry these scope names in `<!-- SCOPE: … -->` blocks. Keep
the blocks for your scope, delete the others, and delete the markers — the
reviewer should never learn that other scopes exist.

## Review package

The reviewer reads the diff from a **file**. Write it before you dispatch:

```bash
OUT="$WORK/review-$(git rev-parse --short "$BASE")..$(git rev-parse --short HEAD).diff"
{ echo "## Commits";       git log --oneline "$BASE"..HEAD
  echo; echo "## Files changed"; git diff --stat "$BASE"..HEAD
  echo; echo "## Diff";     git diff -U10 "$BASE"..HEAD
} > "$OUT"
```

The redirect is the point: the diff never passes through your context, and the
reviewer gets the commit list, the stat summary, and the full diff with context
in one Read. `$WORK` is a scratch directory — `.tuckit/work/<REF>/` under the
repo root when there is a slice, any ignored path when there is not. Review
packages are files; none of this belongs on the board.

`BASE` is a value you recorded **before the work started** — for a `branch`
review, `git merge-base <base-branch> HEAD`. **Never `HEAD~1`**: it silently
drops all but the last commit whenever the work took more than one.

For an `ad-hoc` review, `BASE` is whatever range the requester named. When what
they want reviewed is not committed yet there is no range at all, so build the
package from the working tree instead — there are no commits to list, and the
prompt's **Head:** line stays blank:

```bash
OUT="$WORK/review-worktree.diff"
{ echo "## Files changed"; git diff --stat HEAD
  echo; echo "## Diff";    git diff -U10 HEAD
} > "$OUT"
```

`git diff HEAD` covers everything uncommitted, staged or not; plain `git diff`
narrows it to unstaged work when that is what was asked about. Either way the
reviewer still reads one file, and the rules below are unchanged.

**Never dispatch a reviewer without a diff file.**

Hand it, alongside the diff path: the slice ref (so it reads the requirements
itself, from the same source the implementer used), the slice's `constraints`
copied verbatim, and — in `bite` scope only — the implementer's report file.
Copy constraints exactly: exact values, exact formats, the stated relationships
between components. That block is the reviewer's attention lens; the template
already carries the process rules.

**Do not pre-judge findings for the reviewer.** Never tell one to ignore an
issue, cap a severity, or treat something as settled because a checklist chose
it. If a prompt you are writing contains "do not flag," "at most Minor," or "the
checklist decided," stop — you are spending the review to spare yourself a fix
round.

## Model selection

Scale the reviewer's model to the diff's size, complexity, and risk. A small
mechanical diff does not need the most capable model; a subtle concurrency
change does. Scoped re-reviews of small fix diffs take a cheap-to-mid tier.

**A `branch` review runs on the most capable model available.** It is the last
gate, and it judges integration across the whole change.

**Always name the model when you dispatch.** An omitted model silently inherits
the session's — usually the most capable and most expensive one — which defeats
every line above.

## When findings come back

Hand the findings to `receiving-a-review` and work them there. Do not act on
them straight out of the report: that skill decides, item by item, whether a
finding is fixed, pushed back on, noted, or turned into a slice — and it is what
keeps the ones you are not fixing from evaporating into the chat log.

The verdict is a verdict, not an instruction. A reviewer that says "Needs fixes"
has not decided what happens to this branch; you and your human partner do.

## Templates

- [reviewer-prompt.md](reviewer-prompt.md) — the review itself, five scope slots
- [re-review-prompt.md](re-review-prompt.md) — verifying a fix wave against the
  findings it was supposed to address

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `requesting-code-review`,
rewritten so one rubric serves a bite, a branch, and an ad-hoc review.
