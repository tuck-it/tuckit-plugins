---
name: delegating-a-slice
description: "Use when a tuckit slice is ready to build — stage reads executing — and you have subagents available. Splits the work into dispatches, reviews each one before the next, runs a whole-branch review at the end, and records the evidence. Prefer this over executing-a-slice whenever the work splits cleanly."
---

# Delegating a Slice

Execute a slice by dispatching fresh implementer subagents, reviewing each piece
as it lands, then reviewing the whole branch, then showing the slice's
`done_when` was met.

**Why subagents:** they never inherit your session's history — you construct
exactly what each one needs, so it stays focused, and your own context stays
free for coordination.

**Core principle:** fresh subagent per piece + review each piece + broad final
review + evidence at the end.

Vocabulary and stages: `~/.gemini/config/plugins/tuckit/content/domain.md`.

**Announce at start:** "I'm using delegating-a-slice to implement <ref>."

**Narration:** between tool calls, narrate at most one short line.

**Continuous execution:** do not pause to check in between pieces. The only
reasons to stop are a BLOCKED you cannot resolve, ambiguity that genuinely
prevents progress, or the work being done. "Should I continue?" wastes your
partner's time — they asked you to execute the slice.

## When to Use

Use this over `executing-a-slice` when the work splits into parts that can be
built and judged separately, **and** you have subagents. Execute inline when the
work is one indivisible piece, or when you have none.

If the slice has no `done_when`, its stage reads `needs_done_when` and this is
the wrong skill — go to `designing-a-slice` first. You cannot review against a
target that does not exist, and neither can anybody you dispatch.

## Setup

Ensure the work happens in an isolated workspace: `git worktree add` a branch
off the base, following the repo's convention. **Never start implementation on a
main/master branch without your human partner's explicit consent.**

Read the slice once — `get_slice(<ref>, with_activity=true)` — and note two
things you will hand to every subagent you dispatch:

- **`constraints`** — every dispatch's requirements implicitly include it.
- **`done_when`** — the target the whole branch has to meet. Read it and ask
  whether the work could meet it and still be wrong. If yes, fix the target now
  with your partner, before dispatching anybody at it.

**Split the work yourself.** How many dispatches, and where the seams are, is
your call and it is ephemeral: it lives in your todo list and the scratch
directory below, **not on the board**. The board carries what outlives the
session — decisions, constraints, evidence — and a list of dispatches is not
that. Aim for pieces that are independently reviewable; a seam a reviewer cannot
judge on its own is not a seam.

**Scratch directory.** Implementer reports and review packages are files, not
board writes:

```bash
ROOT="$(git rev-parse --show-toplevel)"
WORK="$ROOT/.tuckit/work/<REF>"
mkdir -p "$WORK"
printf '*\n' > "$ROOT/.tuckit/.gitignore"
```

The self-ignoring `.gitignore` keeps every slice's scratch out of `git status`
without modifying a tracked file. One directory per slice ref, so a concurrent
run cannot read or overwrite your artifacts.

**Resuming after a compaction.** Conversation memory does not survive, and there
is no per-step status on the board to read it back from — so the record is
**git log on your branch** (subjects carry the ref) plus the report files in
`$WORK` and the slice's activity notes. Read all three before dispatching
anything. Re-dispatching work that is already committed is the most expensive
mistake this loop can make, and nothing structural stops you: only that look
does. Write a one-line `$WORK/progress.md` entry as each piece lands, so the
next you has something cheaper to read than a diff.

## Model Selection

Use the least powerful model that can do each job.

- **Mechanical work** (1-2 files, the approach already settled): cheapest tier.
- **Integration and judgment** (multi-file, pattern-matching, debugging):
  standard tier.
- **Design judgment or broad codebase understanding**: most capable. The final
  whole-branch review is one of these.
- **Fix-loop escalation (rounds 4-5)**: at least one tier above the implementer
  that got stuck.
- **Review tasks**: `requesting-a-review` owns this choice.

**Always specify the model explicitly.** An omitted model inherits your
session's — often the most expensive — which silently defeats this section.

**Turn count beats token price.** The cheapest models routinely take 2-3× the
turns on multi-step work and cost more overall. Use a mid-tier model as the
floor for reviewers and for implementers working from prose.

## The Loop

For each piece:

### 1. Dispatch the implementer

Record BASE (`git rev-parse HEAD`) first — the review package and fix-round
diffs need it.

**Do not paste the slice into the dispatch.** Give the subagent the ref and let
it call `get_slice` itself. The board is the single source of requirements: a
pasted copy costs your context, can drift from what the board says, and buys
nothing the subagent cannot fetch.

Your dispatch should contain: (1) one line on where this piece fits; (2) the
slice ref, introduced as "read it first — it is your requirements, including the
`done_when` this branch has to meet"; (3) **which part of the slice this
dispatch owns**, since the board does not carry your split; (4) interfaces and
decisions from earlier pieces the board cannot know; (5) your resolution of any
ambiguity you noticed; (6) the report-file path and the report contract.

- **Report file:** `$WORK/report-<N>.md`. The implementer writes its full report
  there and returns only status, commits, a one-line test summary, and concerns.
- A dispatch describes one piece, not the session's history. Do not paste
  accumulated prior summaries — a real session's dispatch hit 42k chars of which
  99% was pasted history.
- Record the implementer's agent identity — fix rounds 1-3 resume it.
- Never dispatch implementers in parallel (conflicts).

Template: [implementer-prompt.md](implementer-prompt.md)

### 2. Handle the report

**DONE:** write the review package and dispatch the reviewer. The implementer's
DONE is a claim, not evidence — the diff you read while writing that package is
the evidence. `verifying-before-claiming`'s "Agent completed → VCS diff shows
changes" row is exactly this moment.

**DONE_WITH_CONCERNS:** read the concerns first. Correctness or scope doubts get
addressed before review; observations get noted.

**NEEDS_CONTEXT:** provide what was missing and re-dispatch.

**BLOCKED:** assess. A context problem → more context, same model. Needs more
reasoning → more capable model. Too large → split it and say so. The spec itself
is wrong → escalate to your partner.

**Never** ignore an escalation or force the same model to retry unchanged.

### 3. Review the piece

Per-piece reviews are scoped gates; the broad review happens once, at the end.
Never skip one, and never accept a report missing either verdict — spec
compliance AND quality are both required. Implementer self-review does not
replace it.

Write the review package as `requesting-a-review` describes, using the BASE you
recorded — **never `HEAD~1`**, which silently drops all but the last commit.

- **Reviewer inputs:** the slice ref, what this piece was meant to do, the
  report file path, the diff file path, and the slice's `constraints` copied
  verbatim.
- The constraints block is the reviewer's attention lens. Copy exact values,
  exact formats, and stated relationships ("same layout as X").
- Do not ask a reviewer to re-run tests the implementer already ran on the same
  code.
- **Do not pre-judge findings.** If your prompt contains "do not flag", "don't
  treat X as a defect", or "at most Minor" — stop. You are sparing yourself a
  review loop. Let it be raised and adjudicate it below.

A reviewer may report "⚠️ Cannot verify from diff" — requirements living in
unchanged code. Resolve each yourself before moving on; you hold the context it
lacks. A confirmed gap is a failed spec review and enters the fix loop.

Template: [reviewer-prompt.md](../requesting-a-review/reviewer-prompt.md) —
`requesting-a-review` holds how to fill it.

### 4. The fix loop

Findings are routed by `receiving-a-review`. The rounds and the cap below are
this skill's: they say *when* to use those routes, not what they are.

The loop triggers on spec ❌, any Critical or Important finding, or a ⚠️ item you
confirmed.

Two routes leave immediately:

- **Minor findings** never enter the loop. Record them in
  `$WORK/deferred-minors.md` and point the final review at that list so it can
  triage which must be fixed before merge. A roll-up nobody reads is a silent
  discard.
- **A finding that contradicts the spec** is your partner's decision: present
  the finding and the spec text, ask which governs. Do not dismiss the finding
  because the spec mandates it, and do not dispatch a fix that contradicts the
  spec without asking.

Everything else enters. A round is one fix dispatch plus one scoped re-review.
**Five rounds maximum per piece.**

**Rounds 1-3 — resume the original implementer** with the open findings
verbatim; its context is intact. If your harness cannot message a live subagent,
dispatch a fresh one carrying the ref, the report-file path, and the findings —
the report file is the persistent memory either way.

**Rounds 4-5 — fresh implementer, more capable model**, framed as: "A prior
implementer attempted this [N] times; you own it now. Read the report file for
what was tried." A loop surviving three resumes usually means the implementer
cannot see its own problem.

**Every round:** the implementer fixes, re-runs the tests covering the amended
code, appends to the same report file, returns the short contract. Confirm the
fix report names the covering tests, the command, and the output before you
re-dispatch the reviewer.

**The re-review is scoped** to the fix range (FIX_BASE = the head the previous
review saw) — [re-review-prompt.md](../requesting-a-review/re-review-prompt.md).
Each finding comes back ADDRESSED or NOT ADDRESSED, plus new breakage in the fix
diff only. New Critical/Important breakage joins the open list; out-of-scope
observations go to deferred minors and never extend the loop.

**Never fix findings yourself in the controller session** — controller fixes
skip review and pollute your context.

**The breaker.** When round 5 still leaves findings open, stop dispatching and
adjudicate each one yourself, writing every ruling to `$WORK/rulings.md`:

- **Reviewer wrong, or contestable** → park it with the ruling that says why the
  code stands. The final review sees both sides.
- **Real but nothing builds on it** → park it the same way, marked real and
  deferred.
- **Real and load-bearing** — a later piece builds on it, or it reveals a defect
  in the spec → **STOP.** `add_note` on the slice with the finding, the spec text
  it collides with, and the fix history, and report to your partner. Parking a
  structural failure lets everything downstream build on it.

Adjudicate only at the cap. Adjudicating earlier to end a loop is pre-judging
with a different name. Every adjudication is written; a silent discard is
forbidden.

### 5. Move on

When the review is clean — or every open finding is parked with a ruling at the
cap — append a line to `$WORK/progress.md` and dispatch the next piece.

**Never start the next piece while a review has open Critical/Important issues
that are neither fixed nor parked-with-ruling at the cap.**

Along the way: anything you are not doing now becomes a capture
(`create_capture`, so it lands in the Inbox) — not a `TODO` comment, not a line
in your closing message. Any decision you had to make becomes `append_decision`.
Any landmine becomes a `constraints` append. And if a piece turns out not to be
buildable until another slice ships — the bar being that this slice cannot meet
its **own `done_when`** until that one lands — record a `blocks` link with a
note, exactly as `executing-a-slice` describes.

## Final Review

Use `requesting-a-review` with scope `branch`, passing the deferred-minors list
as that scope's optional input. Dispatch it on the most capable model available.

If it returns findings, dispatch **ONE** fix subagent with the complete list —
not one fixer per finding. Per-finding fixers each rebuild context and re-run
suites; a real session's final-review fix wave cost more than all its
implementation combined. Then run exactly one scoped re-review of the fix wave.
Adjudicate residuals as in the breaker. There is no second fix wave — residual
load-bearing findings surface to your partner at `shipping-a-slice`.

## Finish

Three things cross from the scratch directory to the board — and only these
three:

1. **Rulings** — consolidate `$WORK/rulings.md` into **one** `add_note`. One
   note, not one per finding.
2. **Deferred minors that survived triage** — `create_capture`, one per
   surviving item. The ones the final review said nobody will do are dropped
   explicitly in the same note, not silently.
3. **Constraints you discovered** — appended to `constraints`. Notes say what
   happened to you; constraints say what the next person must not repeat.

Then **meet the `done_when` yourself and record it.** Do not delegate this and
do not assemble it out of subagent reports: every one of those is a claim about
a piece, and the target is about the whole. Run it, look at it, and write what
you saw with `record_verification` — `verifying-before-claiming` owns what
counts. That call is what moves the slice to `ready_to_ship`.

Then delete the scratch directory (`rm -rf "$WORK"`) — git history and the board
are the record now. Sibling directories belong to other slices; leave them
alone.

Terminal state: `shipping-a-slice`.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Close enough on spec compliance" | Reviewer found spec gaps = not done. Fix, or hit the cap and adjudicate — those are the only exits. |
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. Resume the implementer. |
| "One more round will converge" | Past the cap, rounds don't converge — the failure is structural. Adjudicate and route. |
| "This finding is obviously wrong, I'll drop it" | You adjudicate only at the cap, and every ruling is written down. |
| "The fix was small, skip the re-review" | Unreviewed fixes are how regressions land. |
| "I'll paste the slice in — it's faster" | It is a second copy of the requirements that can disagree with the board. Send the ref. |
| "The implementers all reported green, so the done_when is met" | Every report is a claim about one piece. The target is about the whole, and you are the only one positioned to check it. |
| "I'll put my split on the board so it's visible" | It is visible in your todo list for the hour it matters. The board is for what outlives the session. |
| "The scratch files are the record" | They are process. The record is git, the consolidated note, and the evidence. Scratch gets deleted. |

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) —
`subagent-driven-development`, rewritten so the target, not a checklist, is
what every dispatch aims at.
