# tuckit domain reference

tuckit is where a product's decisions, roadmap and deferred work live. The
codebase is the truth about what the software IS today; tuckit is the record of
what was decided, when, and what is still owed: the reasoning that touched no
files, which git cannot reconstruct.

Every record is a snapshot of the moment it was written. When a spec and the
code disagree, neither is simply wrong: the code is what shipped, the spec is
what someone agreed to. Say so and ask which one is out of date.

People use the board on the web; agents use the same board over MCP. The tool
descriptions the server gives you are the reference for each field and
parameter. This file covers what they cannot: who decides what, and how work
moves.

## Who decides what

People decide three things. The workflow stops for a person only at these:

- **Direction**: which work exists and how much it matters (captures, slices,
  priorities).
- **The promise**: what a slice will deliver (`spec`) and how anyone would know
  it did (`done_when`). The developer who designs the slice approves both
  together, and the approval is recorded with their name. They own it.
- **Confirmation**: a teammate reviews the pull request. The merge is the
  confirmation.

Everything between the promise and the pull request, how to build it, is the
agent's call. It is recorded as decisions, shown before the code is written,
and open to challenge, but it does not wait for a yes.

## Stages

`stage` is derived on every read and says what a slice needs next. `status` is
only a person's decision (open, shipped, dropped). Read progress from `stage`.

- `needs_design`: no spec yet.
- `needs_done_when`: a spec but no done_when.
- `needs_approval`: the promise is written; nobody has approved it.
- `executing`: approved, and nothing has met it yet.
- `ready_to_ship`: evidence recorded.
- `shipped` / `dropped`: done.

Editing the spec or done_when of an approved slice clears the approval. The
slice goes back to `needs_approval` and the change is recorded as a decision.

## The workflow

1. **Capture**: something noticed becomes a capture, a title and what you saw.
   It claims nothing.
2. **Direction**: someone promotes it into an Area, dismisses it, or leaves it.
   **`tending-the-board`** proposes that in one batch.
3. **Promise, then design**: **`designing-a-slice`**. A vague request is
   questioned until it can be written as a spec and a done_when, the designer
   approves both, and the agent designs and records its decisions.
4. **Build, verify, open the PR**: **`building-a-slice`**, with
   **`reviewing-a-change`** before the evidence is written.
5. **Confirm**: a teammate reviews the PR (**`reviewing-a-change`** helps with
   that too). Once it is merged, anyone may mark the slice shipped.

At the end of a session, **`reconciling-the-board`** closes what became untrue.

**The small lane.** A typo, a version bump, a one-line fix with one obvious way
to do it: it still gets a slice, but the agent writes the one-line promise,
approves it as `self`, and does not stop to ask. The board shows it as
self-approved. The pull request review is the human step.

## Working on a shared board

- Designing and building can be two people. An approved slice can wait with no
  assignee until someone takes it. If its done_when looks wrong, ask the person
  on its `Approved:` line, not the person who asked you to build it.
- Take a slice by assigning it to yourself before you build it.
- A slice someone else holds is theirs: read it freely, but do not build it,
  change its promise or close it. Say who holds it. If it has to move (they
  asked, or it has sat still for weeks), hand it over with a reason; the reason
  is kept on the slice.
- A merged pull request is a fact anyone can act on: whoever sees it may mark
  that slice shipped.

## Writing for the board

A person opening the board sees many cards at once, and the pile itself is
pressure. Each card has to undo that: read on its own, it should be understood
at a glance and make the reader want to fix it. That is the standard for
everything you write here.

- **Title**: one plain sentence about one thing, the problem or the outcome, in
  words a person would say out loud. No code names, refs or abbreviations a
  teammate would have to look up. No second clause after a dash or a
  semicolon. At most 60 characters; the server refuses longer ones from agents.
- **Spec**: two to five short sentences for a teammate who never saw your
  conversation. Why it matters first, then what is in and what is out. No how.
- **done_when**: one observation, what someone would see and where, that could
  turn out false.
- **Capture**: what you saw and where, and what you expected instead.
- **Notes and decisions**: short sentences. Lead with the point. Spell out
  anything only you would know.
- Write in the language the board is already written in.

| Hard to read | Easy to read |
|---|---|
| `Session restore — hydrate order regression causes empty initial render (cache key mismatch)` | `Home screen is blank after logging in` |
| `세션 복원 시 hydrate 순서 문제로 초기 렌더가 비어 있음 — 캐시 키 불일치 …` | `로그인 후 첫 화면이 비어 보임` |
| `query_slices icontains path skips NFC normalization for CJK` | `Search misses Korean words` |
| spec: `Refactor the token refresh path to use the shared retry helper and add backoff.` | spec: `People get logged out mid-task when their session expires. They should stay signed in while they are active. Out of scope: changing how long a session lasts.` |
| done_when: `tests pass` | done_when: `An expired token gets HTTP 401, not an error inside a 200, and the client signs in again without a prompt.` |

## Asking a person something

A message asking a person to decide is finished only when they can answer it
without leaving the message:

- Give every ref its title.
- Options say what changes for them, not what you would build.
- Spell out any identifier they did not introduce.

Reversible decisions get one line each, batched. Irreversible ones lead with
what breaks and what cannot be undone.

## Reading state

Start every "where are we" question with `get_project_state`, not with git or
markdown files.
