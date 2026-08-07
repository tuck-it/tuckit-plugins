---
name: explain-change
description: Use when someone wants to actually understand a change an agent wrote — turns a branch, PR, merge, or commit range into a self-contained interactive HTML explainer that links each slice's recorded intent and ends in a quiz. Trigger on "explain this branch/PR/merge", "explain what we just shipped", "what did we actually build here", or before reviewing agent-written code.
---

# Explain Change

Make one change understandable: what it set out to do, what the code does now,
and whether the reader understood it. Writing code is cheap and understanding it
is not — and unlike the code, the understanding cannot be delegated to an agent.

## 1. Decide whether a page is the right output

A page is expensive to make and expensive to read. Most requests that sound like
this skill are not one.

**Answer in chat instead** when the ask is a question — *what did this branch
touch?*, *did we change the schema?* Read the range and reply. Build a page only
when someone will work through it more than once.

**Do not build one** when the range is a few commits with no mechanism to
explain; when it is renames, dependency bumps, or formatting; or when a page
already covers it (§2 says how to check) and nothing has changed since.

**Do build one** when an agent wrote code nobody has read, when the mechanism is
non-obvious enough that a diff misleads, or when someone is about to change this
code and would otherwise learn it by breaking it. The strongest moment is
**just before reviewing agent-written code** — review is where a team actually
transfers knowledge, and an explainer read first turns "looks fine" into a real
check. At that moment the summary and the intent-vs-shipped comparison often
carry the whole value; the rest of the page is optional.

If you decline, say so in one line and say what you would need for it to be
worth building. An explainer nobody needed is not neutral: it is one more
document competing with the code for the reader's trust.

## 2. Resolve the range, and find the intent inside it

The page's identity is **a range of commits** — something with a definite,
machine-readable boundary. Not a slice: a slice is often a *fraction* of a
commit, so a page scoped to one opens by disowning most of its own diff.

Take whatever names a range, in this order of preference:

1. An explicit range (`a8c8797..3a292d6`) — no inference needed, prefer it.
2. A branch or merge commit — `<merge>^1..<merge>^2` for a merge, or
   `main..<branch>` for an unmerged one.
3. A PR number, via `gh pr view` — available, but do not assume it exists. Many
   repos merge local branches and never open one; check before relying on it.
4. Nothing — then default to the most recent merge on the current branch.

**Uncommitted work has no range, and cannot have a page.** A working tree or a
staged diff gives Provenance no shas to name and nothing to check for being
pushed, and the page would claim to describe a moment that changes on the next
save — a cache with no validity key. Say so plainly and answer in chat instead
(§1), or offer to build one once the work is committed; a throwaway commit
message is enough, since a sha is all the identity this needs. Note that
**committed-but-unpushed is fully supported** — that is a linking question
(§7), not a range one, and everything except the permalinks still works.

Then gather the facts with commands, not impressions. Run these before writing
anything; every later section depends on what they return.

```sh
git log --oneline <base>..<head>                                  # what is in it
git diff --stat <base>...<head> | tail -1                         # how big — 3 dots
git log --oneline <head>..<base> | wc -l                          # drift, see below
git remote get-url origin                                         # permalink base
git branch -r --contains <head>                                   # empty ⇒ unpushed
git log --format=%B <base>..<head> | grep -oE '[A-Z]+-[0-9]+'     # slice refs
ls <output dir>/*explain*                                         # existing pages
```

**Three dots on the diff, two on the log — this is not a stylistic choice.**
`git log A..B` lists commits in B and not A, which is what you want. `git diff
A..B` compares the two endpoints, so if the branch was cut from an older `main`
everything that landed on `main` meanwhile appears in your diff *reversed* — as
deletions the branch never made. `git diff A...B` compares against the merge
base instead and shows only what the branch did. Measured on one repo's merges:
two dots reported 52 files / −1411 lines where three dots reported 6 / −85.

The drift count tells you when this matters: zero means the two forms agree.
Non-zero means the commit list and the diffstat describe different things, and a
diffstat that disagrees with its own commit list is the tell — reconcile them
before you write a word, because every size judgement below depends on it.

Record every `(repo, base_sha, head_sha)` you read; a change may span more than
one repository. **Anything you inferred rather than were given — the range, the
audience, which slices belong to it — goes in Provenance, in plain words.**

Three rules keep a growing pile of explainers legible to someone who did not
write them:

- **Prefer a boundary git can enumerate** — a merge, a release tag. It makes
  "which changes have an explainer" answerable later; an arbitrary sha pair does
  not. Use one anyway if that is what was asked for, but then Provenance must
  say why the range starts and ends there: *"everything in v0.22.0"*, *"the
  branch as merged"*, never a bare pair of hashes.
- **Look for an existing page first**, in both registries — the `add_note`
  records on the slices you link, and the output directory itself, whose
  filenames carry the range (§7). Neither is complete on its own: a page written
  for a range that linked no slice appears only in the directory. If a page
  already covers part of this range, extend or supersede it and say which. Two
  overlapping explainers with no stated relationship are worse than one.
- **One page, one coherent change.** If a range spans unrelated concerns, or
  more slices than a reader holds at once, split it along those boundaries and
  say so. A hundred commits in one page is a changelog.

Read each ref the grep returned with `get_slice`. A range usually carries
several; every one is a first-class subject of the page, not a footnote.

**Expect that grep to come back empty.** Plenty of repos never put refs in commit
messages, and a generator that stops there quietly degrades into a diff
explainer — losing the one thing this skill has that a diff tool does not. Fall
back to the board: search `list_slices` by the merge subject or the branch name,
and by the dates the range spans. Confirm a candidate against the diff before
trusting it, and record the link as inferred. If nothing matches, say so where
the intent section would have been — a range no one wrote intent for is a
finding, not a section to drop in silence.

Keep the two sources distinct — **tuckit**
(`get_slice`, `list_bites`) is what we meant to build and what a later agent was
told not to get wrong; **git** is what exists now. The gap between them is the
most valuable thing on the page.

## 3. Identify the reader

The largest variable in whether an explanation lands is what the reader already
knows. Do not guess it, and do not write for "a developer" in general — ask, or
take it as given from the request.

Build the Background out of **the reader's** vocabulary, not the subsystem's.
Defining the terms a diff uses is a glossary, and a glossary makes the reader
assemble the model themselves — which is the work you were supposed to do. Name
what the mechanism already **is** in something they own: a backend reader
meeting htmx attribute inheritance does not need a tour of `hx-*`, they need one
sentence — *this is dynamic scoping, and the bug is a caller's binding leaking
into a callee that never asked for it.* Same diff, different reader, genuinely
different Background.

**Write the page in the reader's own language**, not the repository's. Reading a
technical explanation in a second language spends working memory on translation
that was supposed to go to the material — the one budget this skill exists to
protect. Keep identifiers, paths and quoted code verbatim; write everything
around them in their language.

## 4. Explore before you write

Read outward from the diff: callers, tests, adjacent modules, the commit that
introduced the constraint being changed. Explain the system, not the lines that
moved. Say plainly when the range covers more or less than the slices linked to
it.

## 5. Sections

**Every causal claim needs a line you can point at, in every section — not just
the ones that quote code.** Sections built on citations tend to come out right;
the ones that explain *why* are where invention happens, because prose has no
empty citation slot to embarrass you. Before writing "this was hard, so they did
that", find the guard, the comment, the commit message or the spec that says so.
If there is none, write what you did find. *"The code simply refuses this path"*
with the `raise` quoted underneath beats a tidier mechanism you reasoned your
way to and cannot source — and the tidier one will be repeated back to you later
by a reader who trusted it.

- **Provenance** — a short header block, first thing on the page: every
  `(repo, base_sha..head_sha)` covered, why the range starts and ends there, the
  slices linked, the generation date, and how far the branch has moved since. It
  is a snapshot, and must say which moment it is a snapshot of. State what it
  **excludes** as plainly as what it covers: neighboring commits that no page
  explains, and — always — that explainers are written for changes worth
  explaining, not for every commit. A reader who has read three of them must not
  come away believing they have seen the system.
- **The problem** — first, before any background and long before any mechanism.
  One concrete person trying to do one concrete thing, what went wrong, and what
  it cost — in their words, not the codebase's. A cause handed to someone who
  does not yet feel the problem answers a question they have not asked. A reader
  must be able to stop here and correctly explain **what was broken** while
  still knowing nothing about **how**. If you cannot write this section without
  naming a function, you do not yet understand the change well enough.
- **Background** — the existing system this change lives in. A beginner-friendly
  mental model first (marked skippable), then the exact components and prior
  behavior. Everything here must earn its place by being needed to understand
  the problem above; background with no problem to attach to is a glossary.
- **Intuition** — the core idea, before any implementation detail. Concrete toy
  examples, diagrams liberally. The reader should be able to stop here and still
  have gained something.
- **Code** — a walkthrough of the real changes, grouped and ordered so the
  narrative flows, never alphabetical. When the range carries several slices,
  group by slice: the reader already has names for those. Write each group as
  **claim → evidence → exception** rather than as a conclusion: what this code
  establishes, the lines and tests that show it, and the path where it does not
  hold. Conclusions teach this change; showing which lines carried the signal
  teaches the reader to read the next one without you.
- **Intent vs. what shipped** — one part per linked slice: what its `spec`
  predicted, what its `constraints` demanded and whether they held, where the
  code diverged, what the spec never anticipated. A diff records only what
  changed, so intent must be guessed from commit messages; a slice has it
  written down *before the code existed*. This is the one section a diff-only
  tool cannot produce, and it is the reason this skill exists — not garnish.
  Specs that turned out **wrong** are the best material in it.
- **What you can no longer assume** — whenever the reader has seen this code
  before. Sentences that were true before this range and are false after, stated
  as beliefs rather than diffs: *"a Ticket's permissions always matched its
  Slice's"* — no longer true, here is the new rule and its one exception. A
  returning reader's problem is stale knowledge, not missing knowledge, and a
  Background written for a newcomer never corrects it. Skip for a first-time
  reader.
- **Quiz** — five interactive multiple-choice questions, medium difficulty: hard
  enough to require the substance, never gotchas or phrase-matching. At least
  two must be the questions the job actually asks — *if this behaved wrongly,
  where would you look first?*, *what breaks if you change this?* — so the
  reader performs the knowledge instead of recognizing it. Every wrong option
  should encode a plausible misunderstanding. Reveal feedback only after the
  reader picks, explaining *why* for right and wrong alike, and vary which
  position holds the correct answer.

## 6. Make the reader do the work

Prose that only tells produces a reader who agrees with everything and predicts
nothing. Where you would otherwise write "note that…", hand the work over
instead — at most twice a page, and often once. A forced second one is
decoration.

- **Ask before you answer.** Pose the question the next paragraph resolves —
  *why was the unique constraint not enough on its own?* — and put the answer
  behind a click. The end quiz scores understanding; a question mid-prose builds
  it.
- **Build a manipulable model when the mechanism has a knob** — an ordering, an
  inherited value, a threshold, a predicate, a state machine. A diagram shows a
  mechanism; a widget lets the reader falsify their own model of it. Four rules
  make it worth its space:
  - **Model the thing the page itself calls the point**, not the thing that was
    easiest to transcribe. A pure function you copied over in five minutes is a
    smell: nobody holds a wrong model of a five-branch `if`, so operating it
    confirms instead of falsifying. Aim at whatever you were least sure of —
    building it forces you to go find the line that settles the question, which
    is also how the widget keeps the surrounding prose honest.
  - **Controls are the reader's verbs, not the schema's fields.** *"File it"*,
    *"change your mind"* — never `bites_total`. Knobs named after columns make
    the reader translate their own experience into your tables, which is the
    glossary failure of §3 committed in the interaction layer instead of the
    prose.
  - **Derive the output live from the same rule the code follows** — a
    hardcoded before/after is an animation, and cannot answer a question you did
    not anticipate.
  - **Let it be driven into both the broken state and the fixed one**, so the
    reader can reproduce the bug and check that the fix preserves what it
    should.

Keyboard-operable controls, never drag-only. Interactivity as decoration is
worse than none: if operating it teaches nothing the caption already says, cut
it.

## 7. Format

- One self-contained HTML file: inline CSS and JS, no external requests, works
  offline. One long page with section headers and a table of contents — not
  tabs. Basic responsive styling so it reads on a phone.
- Save it **outside the repository**, one fixed directory, named for the date
  and the range: `/tmp/YYYY-MM-DD-explain-<base>-<head>-<slug>.html`. The shas
  in the filename are what makes the directory searchable when no slice was
  linked. These are disposable snapshots and must never land in version control.
- Write with the clarity of Martin Kleppmann — engaging, classic style, smooth
  transitions between sections.
- Diagrams: a few reusable families used throughout, always with example data.
  Never ASCII art; plain HTML and CSS. Callouts for key definitions and edge
  cases.
- **Every pointer must predict, and must not rot.** The label says what the
  reader gets by following it — *"the only test that exercises the permission
  exception"*, not *"related files"*. The href is pinned to a sha, never to a
  branch: `blob/<sha>/<path>#L10-L24` still shows the lines you meant next year,
  while `blob/main/...#L10-L24` quietly starts pointing at something else. Build
  the host and owner from `git remote get-url origin` (strip the `.git`,
  normalize an SSH remote); put a commit link and a
  `compare/<base>...<head>` link in Provenance, plus the PR if one exists. Every
  file, line range and sha you name in prose should be clickable.
- **Link nothing the §2 commands did not confirm is on the remote.** Unpushed
  work has no permalink, and a link to a local-only sha is a 404 wearing a
  confident label. When the range is unpushed, name the shas as plain text and
  say in Provenance that they are not published yet.
- Code blocks must use `<pre>`. If you style a custom element instead, it **must**
  set `white-space: pre` or `pre-wrap`, or the browser collapses every newline
  into one line.
- Escape code-derived text for both HTML and JavaScript contexts, and do not
  leak quiz answers through DOM order, styling, or ARIA labels before selection.

## 8. Verify, then record

Open the file and check, do not assume: the quiz responds to a click and reveals
feedback, every `<pre>` computes to `white-space: pre`/`pre-wrap`, hidden answers
stay hidden until asked for, the page does not scroll horizontally, and nothing
requests a remote asset.

**Report the substance in chat, not just a path.** Five lines or so: what the
change does, the one thing that would surprise the reader, and anything the page
could not establish. A reader who must open a file to learn whether it is worth
opening has been given one more thing to look through, which is the cost this
skill exists to remove. The page is where the detail lives, not the gate to it.

Then record it with `add_note` on **each** linked slice, including the shas
covered — so the next person knows an explainer exists and exactly what it
describes. When the range linked no slice, say that in your report: the page
exists, nothing on the board points at it, and its filename is the only record
that it was ever written.

## Boundary

**A wrong explainer is worse than none.** It is read by the next agent as
readily as by a person, so an invented mechanism or a misread constraint
propagates into code, not just into someone's head. Teams that meet a few
confidently wrong pages stop trusting the whole set — including the correct
ones. Prefer saying "the range does not show this" to writing a clean sentence
you cannot point at a line for, and never smooth over a gap in what you found.

Some workspaces hold both public and private repositories. An explainer quotes
source directly, so it inherits the secrecy of whatever it explains: never write
one covering private code to a shared or public location. Its links carry the
repository's paths and existence even to a reader who cannot open them, and the
quoted code does not stop being private because the link 404s for them.
