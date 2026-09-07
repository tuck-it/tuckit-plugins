---
name: verifying-before-claiming
description: "Use when a tuckit slice's done_when has to be met — stage reads executing — and before any claim that work is complete, fixed or passing. Runs the check the slice actually names, then writes what was observed into the slice with record_verification, which is what opens the ship gate. Evidence before assertions, always."
---

# Verifying Before Claiming

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

This skill has a product behind it now. The slice you are working on carries a
`done_when` — the observation that settles it — and `record_verification`
writes what you saw. Until that exists the board REFUSES to ship the slice.
So this is no longer only a habit you are asked to keep: it is the step that
moves the work, and the thing you write is read by the next person who opens
the slice with no transcript to fall back on.

Vocabulary and stages: `${PLUGIN_ROOT}/content/domain.md`.

**Announce at start:** "I'm using verifying-before-claiming before I say this
is done."

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim
it passes. A board write is a claim too.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| A slice at `ready_to_ship` | the slice's own `done_when`, met and observed, plus its `constraints` checked literally | every command you happened to run |
| `status: shipped` | the full suite green **on the merged result** | the merge command succeeded |
| A subagent's work | you read the VCS diff yourself | its report says DONE |

A board write is heavier than a line in the chat. A claim in the chat log
scrolls away; `record_verification` persists, and it stamps the slice verified.
Your human partner reads it tomorrow with no transcript, and the next agent
trusts it instead of re-checking.

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When You Cannot Run the Check

The Gate Function assumes pass or fail. There is a third case: you cannot run
the check at all — no access to the production database, no browser in this
environment, the platform the bug reportedly happens on is not the one you are
sitting in.

- Do not quietly move on. Say in one line what you could not confirm.
- Do not summarize the unchecked thing as if it were checked — that is exactly
  the lie this skill exists to prevent.
- If the gap is not one-off — nobody working in this environment can ever run
  that check — file it: `create_slice`, no area (Inbox), so the gap gets fixed
  once instead of rediscovered every time.

Three things commonly turn out to be unverifiable that look verifiable at
first glance: a suite run scoped to the directory you touched skips the wiring
guards that live above it; an endpoint returning green tells you nothing about
whether the screen a person uses is broken; and a green run against your local
database is evidence about your machine, not about production.

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents
- Calling `record_verification`, or setting `status="shipped"`

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## Writing it down

Running the check is half of it. The other half is `record_verification`, and
it is the half that moves the slice.

```
record_verification(slice_id=<id>, evidence="…")
```

**Write what you SAW, not what you ran.** "pytest -q" proves nothing on its
own -- this is a product whose own history includes suites that asserted
nothing, a guard that printed "0/2 covered" and stayed green, and an absent
row read as a pass. Every one of those had a command that exited 0.

```
two shells, one with the modal open; after the other saved, the modal
showed the new title in 4.1s and no skeleton flashed.
409 on a stale save, with the "keep mine" button rendered.
pytest -q at the repo root: 2491 passed.
```

**Name what you did NOT check.** A gap you write down is a gap the next reader
can close; a gap you leave out is one they discover in production. This costs
one sentence and it is the most useful sentence in the field.

**If you cannot meet the done_when, do not write evidence that you did.** Say
so in the terminal and either fix the work or — if the target itself turned
out to be wrong — change it with `update_slice(done_when=…)` and say that you
did. Revising a target you have understood better is the work; quietly
lowering one you could not meet is the failure this whole field exists to
prevent.

**Withdrawing is normal.** `record_verification(evidence="")` takes the slice
back to `executing`. Do it the moment the evidence stops being true — a
done_when that changed under it, a fix that turned out not to hold. Nothing
here is a one-way door.

## What this does NOT do

The product cannot run your tests. `evidence` is a claim, and the board stores
it without judging it. What the board can do is refuse to open the ship button
until somebody has made one, and put your claim in front of the next reader
next to the work it is about.

So the honesty is yours. Nothing downstream will catch a sentence that says
more than you saw.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) —
`verification-before-completion`, extended so a board write counts as a claim
too -- and rewritten once the board grew a field for the claim to land in.
