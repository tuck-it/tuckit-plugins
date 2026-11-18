# Reviewer Prompt

Fill the bracketed slots and dispatch. Delete the `[REQUIREMENTS]` line when
there is a slice, and the `get_slice` line when there is not.

```
Subagent (general-purpose):
  description: "Review [WHAT] (spec + quality)"
  model: [MODEL — required; an omitted model inherits the session's]
  prompt: |
    You are reviewing a change: first whether it does what was asked, then
    whether it is well built. Report what you find; you decide nothing about
    what happens next.

    ## What was asked

    Call get_slice("<REF>"). Its spec says what was promised, its done_when
    says how anyone would know, and its decisions say how the author chose to
    build it. Judge against all three, and challenge a decision you think is
    wrong rather than assuming it is settled.
    [REQUIREMENTS — when there is no slice: what the requester stated. If
    nothing was stated, review for defects only and say so.]

    Constraints that bind this work, verbatim:
    [CONSTRAINTS]

    ## The change

    Base: [BASE]   Head: [HEAD]

    Read the diff between them once. Look outside the diff only to check a
    risk you can name, and name it in the report. Do not re-run the full suite; run a focused test only for a
    specific doubt. Do not modify the checkout and do not write to the board.

    ## What to look for

    Against the promise:
    - Missing: asked for, not built, or claimed but not there.
    - Extra: built but not asked for.
    - Misread: the right thing built the wrong way.
    - Anything the done_when could pass while the work is still wrong.

    In the code:
    - Errors handled or swallowed? Edge cases the spec names covered?
    - Tests that check real behaviour, not mocks, and that would fail if the
      behaviour broke. A test that asserts nothing is Important.
    - One clear job per file; nothing this change made needlessly large.
    - Schema or contract changes: is there a migration or compatibility path
      for anything already deployed?

    Severity: Critical breaks something or loses data. Important means the
    work cannot be trusted until fixed. Polish is Minor.

    ## Report

    Start directly with the verdict on the promise. Cite file:line for every
    finding.

    ### Promise
    ✅ met | ❌ [what is missing, extra or misread]
    ⚠️ cannot verify from the diff: [what, and what to check]

    ### Issues
    #### Critical
    #### Important
    #### Minor
    For each: file:line, what is wrong, why it matters, how to fix if not
    obvious.

    ### Verdict
    Approved | Needs fixes — one or two sentences why.
```

**For a fix round**, dispatch the same template with the previous Critical and
Important findings pasted under a `## Findings to verify` heading, the base
set to the head the first review saw, and this instruction: verdict each
finding ADDRESSED or NOT ADDRESSED with file:line, report anything the fix
itself broke, and do not re-review code the fix did not touch.
