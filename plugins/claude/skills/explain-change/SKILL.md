---
name: explain-change
description: Use when someone wants to actually understand a change an agent wrote — turns a branch, PR, merge, or commit range into a self-contained interactive HTML explainer that links each slice's recorded intent and ends in a quiz. Trigger on "explain this branch/PR/merge", "explain what we just shipped", "what did we actually build here", or before reviewing agent-written code.
---

# Explain Change

Make a rich, interactive explanation of one change: what it set out to do, what
the code actually does now, and whether the reader understood it.

Writing code is cheap; understanding it is not, and understanding cannot be
delegated to an agent. This skill exists to keep a human's understanding moving
at the same speed as the agent's output.

## The unit is a code range. Slices are the intent layer inside it.

The page's identity is **a range of commits** — something with a definite,
machine-readable boundary. Not a slice: a slice is often a *fraction* of a
commit, and a page scoped to one would spend its opening paragraph disowning
most of the diff it is looking at.

Take whatever names a range, in this order of preference:

1. An explicit range (`a8c8797..3a292d6`) — no inference needed, prefer it.
2. A branch or merge commit — use `<merge>^1..<merge>^2` for a merge, or
   `main..<branch>` for an unmerged one.
3. A PR number, via `gh pr view` — available, but do not assume it exists. Many
   repos merge local branches and never open one; check before relying on it.
4. Nothing — then default to the most recent merge on the current branch and
   **say so on the page**.

Then find the intent. Grep the range's commit messages for slice refs
(`git log --format=%B <range> | grep -oE '[A-Z]+-[0-9]+'`) and read each with
`get_slice`. A range usually carries several; treat every one as a first-class
subject of the page, not a footnote.

## What makes this different from explaining a diff

A diff only records what changed — intent has to be guessed from commit
messages. A slice has the intent written down *before* the code existed, in its
`spec` and `constraints`. Keep the two sources distinct:

- **tuckit** (`get_slice`, `list_bites`) — what we meant to build, and what a
  later agent was told not to get wrong.
- **git** — what actually exists now.

The gap between them is the most valuable thing on the page and the one section
a diff-only tool cannot produce. Give it real weight.

## 1. Ask who is reading before you write a word

The single largest variable in whether an explanation lands is what the reader
already knows. Do not guess it, and do not write for "a developer" in general —
ask, or take it as given from the request.

Then build the Background out of **the reader's** vocabulary, not the
subsystem's. Defining the terms a diff uses is a glossary, and a glossary makes
the reader assemble the model themselves — which is the work you were supposed
to do. The goal is to name what the mechanism already **is** in something they
own:

- A backend reader meeting htmx attribute inheritance does not need a tour of
  `hx-*`. They need one sentence: *this is dynamic scoping, and the bug is a
  caller's binding leaking into a callee that never asked for it.*
- A frontend reader meeting a database isolation level does not need MVCC first.
  They need: *this is a stale closure over a value that has since changed.*

Same diff, different reader, genuinely different Background section. If you
cannot name the reader, say on the page which audience you wrote for — an
explanation that hides its assumed reader cannot be judged by the one it fails.

**Write the page in the reader's own language**, not the repository's. Reading a
technical explanation in a second language spends working memory on translation
that was supposed to go to the material — the one budget this whole skill exists
to protect. Keep identifiers, file paths and quoted code verbatim; write
everything around them in their language.

## 2. Establish scope, and be honest about it

Resolve the range as above. Record every `(repo, base_sha, head_sha)` you
actually read — a change may span more than one repository.

If any part of the scope was inferred rather than given, **say so on the page**.
A reader who does not know what was covered cannot trust what they read. State
plainly when the range covers more or less than the slices linked to it.

Then explore around the change: callers, tests, adjacent modules. Explain the
system, not just the lines that moved.

## 3. Sections

- **Provenance** — a short header block, first thing on the page: every
  `(repo, base_sha..head_sha)` covered, how the range was determined, the slices
  linked, the generation date, and how far the current branch has moved since.
  This page describes those commits and nothing else, permanently. It is a
  snapshot, and it must say which moment it is a snapshot of.
- **The problem** — first, before any background and long before any mechanism.
  One concrete person trying to do one concrete thing, what went wrong for them,
  and what it cost — in the words they would use, not the codebase's. *"The OOB
  fragments were mis-ordered"* is a cause, and handing someone a cause before
  they feel the problem is answering a question they have not asked yet.
  A reader must be able to stop after this section and correctly explain **what
  was broken**, while still knowing nothing about **how**. If you cannot write
  this section without naming a function, you do not yet understand the change
  well enough to explain it.
- **Background** — the existing system this change lives in. Explore the
  surrounding code broadly. Give a beginner-friendly mental model first (marked
  skippable), then narrow to the exact components and prior behavior. Everything
  here must earn its place by being needed to understand the problem above —
  background with no problem to attach to is a glossary.
- **Intuition** — the core idea, before any implementation detail. Concrete toy
  examples. Diagrams liberally. The reader should be able to stop here and still
  have gained something.
- **Code** — a walkthrough of the real changes, grouped and ordered so the
  narrative flows. Not alphabetical. Prose around the snippets, with file and
  line references. When the range carries several slices, group by slice: that
  is the grouping the reader already has names for.
- **Intent vs. what shipped** — one part per linked slice: what its `spec`
  predicted, what its `constraints` demanded and whether they held, where the
  code diverged, and anything the spec never anticipated. Specs that turned out
  to be *wrong* are the most useful material here — an over-claimed cause or a
  rejected alternative teaches more than a plan that simply came true. This is
  the section the whole skill exists for; do not treat it as optional garnish.
- **Quiz** — five interactive multiple-choice questions, medium difficulty:
  hard enough that you must understand the substance to answer, never gotchas or
  phrase-matching. Test behavior, causality, and edge cases. Every wrong option
  should encode a misunderstanding someone could plausibly hold. Reveal feedback
  only after the reader picks, and explain *why*, for right and wrong alike.
  Vary which position holds the correct answer — do not let it settle into a
  pattern across the five.

## 4. Format

- One self-contained HTML file: inline CSS and JS, no external requests, works
  offline. One long page with section headers and a table of contents — not
  tabs. Basic responsive styling so it reads on a phone.
- Save it **outside the repository**, filename starting with today's date:
  `/tmp/YYYY-MM-DD-explain-<slug>.html`. These are disposable snapshots and must
  never land in version control.
- Write with the clarity of Martin Kleppmann — engaging, classic style, smooth
  transitions between sections.
- Diagrams: pick a small number of reusable families and use them throughout —
  a simplified version of the UI for interface changes, a data-flow diagram
  between components (always with example data). Never ASCII art; use plain HTML
  and CSS. Use callouts for key definitions and important edge cases.
- **Build a manipulable model when the mechanism has a knob.** A diagram shows a
  mechanism; a widget lets the reader *falsify their own model of it*. If the
  heart of the change is an ordering, an inherited value, a threshold, a
  predicate, or a state machine, build one small thing the reader can operate.
  Two rules make it worth its space:
  - **Derive the output from the same rule the code follows**, computed live
    from the controls. A hardcoded before/after is an animation, not a model —
    it cannot answer a question you did not anticipate.
  - **Let it be driven into the broken state and the fixed one.** The reader
    should be able to reproduce the bug, and to check that the fix does not
    break the case it was supposed to preserve.

  One or two per page, placed exactly where the prose would otherwise say
  "convince yourself that…". Keyboard-operable controls, never drag-only.
  Interactivity as decoration is worse than none: if operating it teaches
  nothing the caption does not already say, cut it.
- Code blocks must use `<pre>`. If you style a custom element instead, it **must**
  set `white-space: pre` or `pre-wrap`, or the browser collapses every newline
  into one line. Before saving, check each code block's CSS for this.
- Escape code-derived text for both HTML and JavaScript contexts, and do not
  leak quiz answers through DOM order, styling, or ARIA labels before selection.

## 5. Validate before you hand it over

Open the file and check, do not assume: the quiz responds to a click and reveals
feedback, every `<pre>` computes to `white-space: pre`/`pre-wrap`, the page does
not scroll horizontally, and nothing requests a remote asset.

## 6. Close the loop

Report the file path, and record it with `add_note` on **each** linked slice,
including the shas covered — so the next person knows an explainer exists and
exactly what it describes.

## Boundary

Some workspaces hold both public and private repositories. An explainer quotes
source directly, so it inherits the secrecy of whatever it explains: never write
one covering private code to a shared or public location.
