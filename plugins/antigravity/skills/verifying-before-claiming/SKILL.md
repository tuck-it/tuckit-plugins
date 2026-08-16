---
name: verifying-before-claiming
description: "Use when about to claim work is complete, fixed, or passing, before committing, creating PRs, ticking a bite off, or moving a slice to shipped — requires running verification commands and confirming output before making any success claims; evidence before assertions always"
---

# Verifying Before Claiming

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

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
| A bite marked `done` | the verification that bite's own body specifies, run now, output read | "I implemented it", an earlier run |
| A slice at `ready_to_ship` | every bite verified, and the slice's `constraints` checked literally | every box is ticked |
| `status: shipped` | the full suite green **on the merged result** | the merge command succeeded |
| A subagent's bite | you read the VCS diff yourself | its report says DONE |

A board write is heavier than a line in the chat. A claim in the chat log
scrolls away; `update_bite(status="done")` persists. Your human partner reads
it tomorrow with no transcript, and the next agent trusts it instead of
re-checking. So run the Gate Function above on whatever that bite's body says
to verify, and call `update_bite(status="done")` only once you have read the
output.

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
- Ticking a bite, moving a slice to `ready_to_ship`, or setting
  `status="shipped"`

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) —
`verification-before-completion`, extended so a board write counts as a claim
too.
