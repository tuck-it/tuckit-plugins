---
name: shipping-a-slice
description: "Use when a tuckit slice's implementation is finished — stage reads ready_to_ship — and the branch needs to land. Verifies for real, lands the branch, records what happened on the slice, and asks before marking it shipped."
---

# Shipping a Slice

## Overview

**Core principle:** Verify for real → Reconcile the board → Detect environment →
Present options → Execute choice → Record what happened → Clean up.

Two things end here: the branch, and the board's claim about this work. Letting
one happen without the other is how a tracker starts lying.

Vocabulary and stages: `{{ROOT}}/content/domain.md`.

**Announce at start:** "I'm using shipping-a-slice to land <ref>."

## Step 1: Verify For Real

The standard for what counts as evidence here — and what does not — is
`verifying-before-claiming`. Landing is where it matters most: this is the
last gate before the board says shipped.

- **Re-read the slice's `done_when` and meet it again, now, on what is about to
  land.** The `evidence` on the board was recorded against an earlier state of
  this branch; review fixes have happened since. Evidence about a branch that
  changed afterwards is evidence about something that no longer exists.
- Run the project's **full** test suite (`npm test` / `cargo test` / `pytest` /
  `go test ./...`) — not the scoped subset you were iterating on.
- Re-read the slice's `constraints` and check the work against them literally.
  That field is where the landmines were written down by someone who had more
  context than you do now.
- If the change has a surface a person uses, open it and look.
- If production runs a different database or runtime than your local one, run
  the check there too.

**If tests fail**, report the failures and stop — the menu comes after a green
suite:

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

Report what actually ran: an unrun suite described as passing is the exact
failure this step exists to prevent.

**If tests pass:** continue to Step 2.

## Step 2: Reconcile the Board With Reality

Before landing anything, make the board match what happened:

- **The evidence must describe what is landing.** If Step 1 turned up anything
  the recorded evidence does not cover, call `record_verification` again with
  what you just saw. It replaces the old claim and re-stamps when.
- **If you could not meet the `done_when`, do not land on the old evidence.**
  Either fix the work, or — if the target itself turned out to be wrong —
  `save_slice(done_when=…)`, say so out loud, and re-verify against the new
  one. Withdrawing is a normal move: `record_verification(evidence="")` takes
  the slice back to `executing` and nothing is lost.
- **Work you decided not to do** → say so in the note at Step 8, and if it is
  worth doing later, capture it. Silence here makes the slice look complete
  when part of it was dropped on purpose.
- **Anything discovered and deferred** → `create_capture` now, one per thing.
  Nobody has agreed to do them yet, so they go to the Inbox as captures, not as
  slices with a spec written in. "We should also…" said in chat and nowhere
  else does not survive this session.
- **Any decision you made while landing** → `append_decision`.

## Step 3: Detect Environment

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 7) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

This determines which menu to show and how cleanup works:

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 3 options | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 3 options | Provenance-based (see Step 7) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 2 options (no merge) | Externally managed — leave in place |

## Step 4: Determine Base Branch

The base branch is whatever this work forked from — usually named in the slice,
the conversation, or the branch's upstream. If it is not already known, ask:
"This branch split from <your best guess> - is that correct?" Confirm before
merging: merging into the wrong base is expensive to undo.

## Step 5: Present Options

**Normal repo and named-branch worktree — present exactly these 3 options:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)

Which option?
```

**Detached HEAD — present exactly these 2 options:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)

Which option?
```

Present the menu exactly as written — concise, with every option coming from the
list above. Discarding the work happens only in response to your human partner
explicitly asking for it (see "If your human partner asks to discard the work"
below). Wait for their answer; the integration decision is theirs.

## Step 6: Execute Choice

### Option 1: Merge Locally

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

If tests fail on the merged result: stop, leave the worktree and branch in
place, and investigate — nothing has been pushed, so the merge is local and
recoverable.

Once the merged result is green: clean up the worktree (Step 7), then delete the
branch:

```bash
git branch -d <feature-branch>
```

### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch>
```

Then create the pull/merge request against <base-branch> with the forge's
tooling — its CLI if one is available, or the creation URL most forges print
when you push — following the repo's PR template and conventions if present, and
report the URL to your human partner.

Keep the worktree — your human partner iterates on PR feedback there.

### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

### If your human partner asks to discard the work

This path exists only as a response to an explicit request to throw the work
away. Confirm first:

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for that exact confirmation. When it arrives:

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

Then clean up the worktree (Step 7) and force-delete the branch:

```bash
git branch -D <feature-branch>
```

Discarding the branch does not drop the slice. If the work is genuinely
abandoned, that is a `status="dropped"` decision the human makes — see Step 9.

## Step 7: Cleanup Workspace

**Runs for Option 1 and confirmed discards.** Options 2 and 3 always preserve
the worktree. Both callers have already changed directory to the main repo root
— worktree removal must run from outside the worktree — and use the
`GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` values captured in Step 3, from before
that directory change.

**If `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Done.

**If `WORKTREE_PATH` is under `.worktrees/` or `worktrees/`:** we created this
worktree — we own cleanup:

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**Otherwise:** The host environment owns this workspace — leave it in place. If
your platform provides a workspace-exit tool, use it.

## Step 8: Record What Happened

`add_note(slice=<ref>, body=…)`: what shipped, the merge commit or PR link, what
surprised you, what you left out. Notes are timestamped and append-only, and
they are what makes this slice readable in six months when the diff no longer
explains itself.

If you hit a landmine along the way, it belongs in `constraints` as well as in
the note. The note says what happened to you; constraints say what the next
person must not repeat.

## Step 9: Ask Before Marking It Shipped

`status` is the one field nothing derives — it records a decision a human made.
The stage reading `ready_to_ship` means somebody wrote down evidence, which is
not the same as someone deciding this is done and out. The board never judged
that evidence; it only refused to proceed without it.

Ask. On a yes, `save_slice(slice_id=…, status="shipped")`. On a no, say what
is still missing and leave it open — an open slice with a clear note is honest;
a shipped slice with unfinished work is not.

Two things refuse that call, and neither is a bug: no evidence recorded, and
another slice still blocking this one. The second refusal names the blockers.
Read the note on each link before doing anything else, and hold it against the
bar the link was written under: this slice cannot meet its **own `done_when`**
until the blocker ships. If that has stopped being so, the link is untrue —
`link_slices(…, unlink=True)` removes it and the ship goes through.
`over_block` and `over_unverified` push past the matching refusal, and each
lands on the activity thread as itself, so a ship over a block never reads as an
ordinary one. They are for the case where your human partner has looked and
decided to ship anyway, not for getting the call to succeed.

Then close with one line about the board, not about your process: which slice is
shipped, and what this session left in the Inbox for later.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| Discard (explicit request only) | - | - | - | yes (force) |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on. |
| "The scoped run is the same thing, just faster" | It is not. Narrowing to the directory you touched skips the wiring guards above it. |
| "They obviously want it merged" | Integration is your human partner's decision. Present the menu and wait. |
| "They seem done with this feature — I'll offer to discard it" | The menu is complete as written. Discard happens only when your human partner asks for it in so many words. |
| "'Yeah, get rid of it' counts as confirmation" | Only the typed word `discard` authorizes deletion. |
| "The PR is up, so the worktree is clutter now" | PR feedback gets fixed in that worktree. It stays until the work lands. |
| "This other worktree looks stale — I'll clean it too" | Clean up only worktrees under `.worktrees/` or `worktrees/`. Everything else belongs to the host. |
| "The merged-result failure is probably flaky" | A failing merged result stops everything. Branch and worktree stay put while you investigate. |
| "The base branch is obviously main" | Confirm the fork point or ask. Merging into the wrong base is expensive to undo. |
| "The push was rejected — force-push will fix it" | A rejected push means the remote moved. Investigate; force-push only on your human partner's explicit request. |
| "I'll write the evidence up after the merge" | Then it is a description of what you did, not a check you ran. Evidence is recorded before the branch lands, in Step 2. |
| "The stage already reads ready_to_ship, so it is shipped" | Stage is derived; status is decided. Ask before setting it. |
| "I'll mention the follow-up in my closing message" | The board cannot see your closing message. It is a capture or it does not exist. |
| "The ship was refused because something blocks it — pass over_block" | Read the link's note first. If it is still true the work is not done; if it is not, unlink it. The override is for a decision your human partner made, not for clearing an error. |
| "The constraints were written before the work — they are stale now" | Then say so and update the field. Skipping the check is not the same as disagreeing with it. |

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) —
`finishing-a-development-branch`, rewritten so landing the branch and closing
the slice are one act.
