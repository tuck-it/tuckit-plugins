# Scoped Re-Review Prompt Template

Use this template when dispatching a re-review after a fix round. The
re-reviewer verifies the findings were addressed and checks the fix diff for new
breakage. It is not a fresh review — the full review already happened.

**Purpose:** Verify each finding from the previous review was addressed, and
that the fix itself broke nothing.

**Scopes:** this one template serves the same three scopes as the review that
produced the findings. Everything it says is common except the blocks marked
below, which differ by what the fix round belongs to.

| Scope | The fix round follows | Requirements come from | What follows this round |
|---|---|---|---|
| `bite` | a bite-scoped gate | the bite's body | the branch review, later |
| `branch` | the merge gate | the slice's spec | nothing |
| `ad-hoc` | a standalone review | whatever was stated, if anything | nothing |

**How the markers work:** `<!-- SCOPE: … -->` opens a block for the scopes it
names, and the block runs to the next marker or the next heading — unless the
marker sits directly above a heading, in which case it governs that whole
section. `<!-- SCOPE: all -->` reopens text every scope keeps, and `OPTIONAL` in
a marker means the block goes away entirely when you have nothing to fill it
with. Keep the blocks that name your scope, delete the rest, and delete every
marker before you dispatch: the reviewer should never learn that other scopes
exist.

```
Subagent (general-purpose):
  description: "Re-review <SCOPE_LABEL> fix round R"
  model: [MODEL — REQUIRED: choose per SKILL.md Model selection; an omitted
         model silently inherits the session's most expensive one]
  prompt: |
    You are re-reviewing a fix round. A previous review produced findings; an
    implementer has attempted to fix them. Your job is to verdict each finding
    and inspect the fix diff — nothing else.

    ## What Is Under Verification

    <!-- SCOPE: bite -->
    Call get_slice("<REF>") and list_bites(<SLICE_ID>). The item under
    verification is bite id <BITE_ID>; its body is what was requested.

    <!-- SCOPE: branch -->
    Call get_slice("<REF>"). What was requested is the slice's spec, and its
    Constraints section is binding. You are verifying a fix wave over the whole
    branch.

    <!-- SCOPE: ad-hoc -->
    [REQUIREMENTS] — what was requested. If nothing was stated, verify the
    findings only and say so.

    ## The Findings Under Verification

    [FINDINGS]

    ## The Fix

    Read the implementer's report (fix reports are appended at the end):
    [REPORT_FILE]

    **Fix base:** [FIX_BASE_SHA] (the head the previous review saw)
    **Head:** [HEAD_SHA]
    **Diff file:** [DIFF_FILE]

    Read the diff file once — it contains the fix commits, a stat summary, and
    the fix diff with surrounding context. Do not re-run git commands. If the
    diff file is missing, fetch the diff yourself:
    `git diff --stat [FIX_BASE_SHA]..[HEAD_SHA]` and
    `git diff [FIX_BASE_SHA]..[HEAD_SHA]`.

    Your review is read-only on this checkout. Do not mutate the working tree,
    the index, HEAD, or branch state in any way. Do not write to the board.

    ## Scope

    Your scope is the findings list and the fix diff. Verdict every finding.
    Inspect the fix diff for new problems the fix itself introduced. Do NOT
    re-review code the fix did not touch: if you notice an issue entirely
    outside the fix diff, report it under Out-of-Scope Observations — it does
    not block this round and does not extend the loop.

    <!-- SCOPE: bite -->
    A broad whole-branch review happens after every bite is complete.

    <!-- SCOPE: branch -->
    This fix wave closes the branch review. Nothing broader follows it, so an
    Out-of-Scope observation here reaches the controller and no one else —
    report it precisely enough to act on.

    <!-- SCOPE: ad-hoc -->
    No further review follows this one.

    ## Tests

    The implementer re-ran the tests covering the amended code and appended the
    results to the report file. Treat the report as unverified claims: confirm
    the fix report names the covering tests and shows their output, and verify
    the claims against the diff. Do not re-run the suite to confirm their
    report. Run a test only when reading the code raises a specific doubt that
    no existing run answers — and then a focused test, never a package-wide
    suite.

    ## Output Format

    Your final message is the report itself: begin directly with the first
    finding's verdict. Every line is a verdict, a finding with file:line, or a
    check you ran — no preamble, no process narration.

    ### Finding Verdicts

    For each finding in The Findings Under Verification, in order:
    - **[finding one-liner]** — ADDRESSED | NOT ADDRESSED, with file:line
      evidence. "Attempted" is not addressed: the specific defect must no longer
      exist.

    ### New Breakage in the Fix Diff

    Anything the fix itself broke or introduced, with severity
    (Critical/Important/Minor) and file:line. "None" if clean.

    ### Out-of-Scope Observations

    Issues you noticed entirely outside the fix diff. Non-blocking.

    <!-- SCOPE: bite -->
    The controller records these for the final review.

    <!-- SCOPE: branch, ad-hoc -->
    Nothing broader follows, so these reach whoever requested this review and
    no one else.

    <!-- SCOPE: all -->
    "None" if none.

    ### Verdict

    **Fix round:** [All findings addressed, no new Critical/Important breakage |
    Findings remain open] — list the open ones.
```

**Placeholders:**
- `[MODEL]` — REQUIRED: reviewer model per SKILL.md Model selection; scoped
  re-reviews of small fix diffs take a cheap-to-mid tier
- `[SCOPE_LABEL]` — REQUIRED: what the fix round belongs to, for the dispatch
  line — `bite 88`, `branch`, or `the reported findings`
- `<REF>` / `<SLICE_ID>` / `<BITE_ID>` — the same board address the implementer
  and the first reviewer worked from. All three are REQUIRED in `bite` scope;
  `branch` scope needs `<REF>` only; `ad-hoc` may have no slice at all
- `[REQUIREMENTS]` — `ad-hoc` scope: what was requested, if anything was stated
- `[FINDINGS]` — the Critical/Important findings and spec gaps from the previous
  review, copied verbatim, one per bullet
- `[REPORT_FILE]` — the implementer's report file (fix reports appended)
- `[FIX_BASE_SHA]` — the head the previous review saw
- `[HEAD_SHA]` — current commit
- `[DIFF_FILE]` — the review package the controller wrote over the fix range

**Re-reviewer returns:** per-finding verdicts (ADDRESSED / NOT ADDRESSED), new
breakage in the fix diff, out-of-scope observations, and a round verdict.
