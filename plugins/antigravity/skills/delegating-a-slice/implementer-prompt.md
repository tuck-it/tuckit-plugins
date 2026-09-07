# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

```
Subagent (general-purpose):
  description: "Implement <PIECE_LABEL> of <REF>"
  model: [MODEL — REQUIRED: choose per SKILL.md Model Selection; an omitted
         model silently inherits the session's most expensive one]
  prompt: |
    You are implementing one piece of tuckit slice <REF>.

    ## Your Requirements

    Call get_slice("<REF>") first. Its spec is what this slice is and why, its
    Constraints section binds you, and its `done_when` is what the finished
    branch has to make true — read all three before you start, and use the exact
    values in them verbatim.

    **Your piece is this:**

    [ASSIGNMENT — what this dispatch owns, in the controller's words. The board
    does not carry the split, so this is the only place it is written down.]

    Implement that and nothing else — the other pieces belong to other
    subagents. The `done_when` is the whole branch's target, not yours alone;
    you are not expected to satisfy it by yourself, and you must not change
    anything outside your piece in order to.

    Do not write to the board. The controller owns every board write for this
    slice.

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context, and
    the interfaces earlier pieces produced that the board cannot know]

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria
    - The approach or implementation strategy
    - Dependencies or assumptions
    - Anything unclear in your assignment

    **Ask them now.** Raise any concerns before starting work.

    ## Your Job

    Once you're clear on requirements:
    1. Implement exactly what your assignment specifies
    2. Write tests — follow `writing-tests-first` if the work calls for it
    3. Verify the implementation works
    4. Commit your work, with [slice ref] at the start of the subject line
    5. Self-review (see below)
    6. Report back

    Work from: [directory]

    **While you work:** If you encounter something unexpected or unclear, **ask
    questions**. It's always OK to pause and clarify. Don't guess or make
    assumptions.

    While iterating, run the focused test for what you're changing; run the
    full suite once before committing, not after every edit.

    ## Code Organization

    You reason best about code you can hold in context at once, and your edits
    are more reliable when files are focused. Keep this in mind:
    - Follow the file structure your assignment defines
    - Each file should have one clear responsibility with a well-defined
      interface
    - If a file you're creating is growing beyond your assignment's intent,
      stop and report it as DONE_WITH_CONCERNS — don't split files on your own
    - If an existing file you're modifying is already large or tangled, work
      carefully and note it as a concern in your report
    - In existing codebases, follow established patterns. Improve code you're
      touching the way a good developer would, but don't restructure things
      outside your piece.

    ## When You're in Over Your Head

    It is always OK to stop and say "this is too hard for me." Bad work is worse
    than no work. You will not be penalized for escalating.

    **STOP and escalate when:**
    - Your piece requires architectural decisions with multiple valid approaches
    - You need to understand code beyond what was provided and can't find
      clarity
    - You feel uncertain about whether your approach is correct
    - It involves restructuring existing code in ways the slice didn't anticipate
    - You've been reading file after file trying to understand the system
      without progress

    **How to escalate:** Report back with status BLOCKED or NEEDS_CONTEXT.
    Describe specifically what you're stuck on, what you've tried, and what kind
    of help you need. The controller can provide more context, re-dispatch with
    a more capable model, or split your piece into smaller ones.

    ## Before Reporting Back: Self-Review

    Review your work with fresh eyes. Ask yourself:

    **Completeness:**
    - Did I fully implement everything my assignment asked for?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate (match what things do, not how they work)?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing patterns in the codebase?

    **Testing:**
    - Do tests actually verify behavior (not just mock behavior)?
    - Did I follow TDD if required?
    - Are tests comprehensive?
    - Is the test output pristine (no stray warnings or noise)?

    If you find issues during self-review, fix them now before reporting.

    ## After Review Findings

    If the review of your piece finds issues, you will be resumed with the
    findings. Fix them, re-run the tests that cover the amended code, and append
    a fix report to your report file: what you changed, the covering tests you
    ran, the command, and the output. Reviewers will not re-run tests for you — your
    report is the test evidence. Then reply with the same short status contract
    as your first report.

    ## Report Format

    Write your full report to [REPORT_FILE]:
    - What you implemented (or what you attempted, if blocked)
    - What you tested and test results
    - **TDD Evidence** (if TDD was required here):
      - RED: command run, relevant failing output before implementation, and
        why the failure was expected
      - GREEN: command run and relevant passing output after implementation
    - Files changed
    - Self-review findings (if any)
    - Any issues or concerns

    Then report back with ONLY (under 15 lines — the detail lives in the report
    file):
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - Commits created (short SHA + subject)
    - One-line test summary (e.g. "14/14 passing, output pristine")
    - Your concerns, if any
    - The report file path

    If BLOCKED or NEEDS_CONTEXT, put the specifics in the final message itself —
    the controller acts on it directly.

    Use DONE_WITH_CONCERNS if you completed the work but have doubts about
    correctness. Use BLOCKED if you cannot complete your piece. Use NEEDS_CONTEXT
    if you need information that wasn't provided. Never silently produce work
    you're unsure about.
```

**Placeholders:**
- `[MODEL]` — REQUIRED: implementer model per SKILL.md Model Selection
- `<REF>` — REQUIRED: how the subagent finds the slice on the board. Never
  paste the spec, the constraints or the done_when in its place.
- `<PIECE_LABEL>` — REQUIRED: a short name for this piece, for the dispatch line
- `[ASSIGNMENT]` — REQUIRED: what this dispatch owns. The board carries the
  slice but not your split, so an empty assignment leaves the subagent to guess
  which part of the slice is its own — and it will guess the whole thing.
- `[REPORT_FILE]` — REQUIRED: `$WORK/report-<N>.md`
- `[slice ref]` — the slice's ref, from the `Ref:` line of `get_slice` and not
  the id you passed it. The implementer never sees the board, so if you do not
  put the ref in the prompt, its commits cannot carry one.
- `[directory]` — the worktree the implementer works from
