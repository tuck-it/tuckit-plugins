---
name: breaking-down-a-slice
description: "Use when a tuckit slice has an approved spec and needs implementation steps — stage reads needs_steps — before touching any code. Writes the constraints and an ordered bite checklist onto the slice itself. The board is the plan, so there is no plan file."
---

# Breaking Down a Slice

## Overview

Write comprehensive implementation steps assuming the engineer has zero context
for this codebase and questionable taste. Document everything they need: which
files to touch for each bite, the code, the testing, docs they might need to
check, how to verify it. Give them the whole plan as bite-sized work. DRY.
YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset
or problem domain. Assume they don't know good test design very well.

In practice that engineer is a fresh agent session that will read **one bite and
its body**, and little else.

**Announce at start:** "I'm using breaking-down-a-slice to turn the spec into
steps on the board."

Vocabulary and stages: `__REPO__/plugins/antigravity/content/domain.md`.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Load the slice** — confirm it actually has an approved spec
2. **Write the constraints** — before any bite; this is the highest-value text
   you will write
3. **Scope check** — one plan, or several slices?
4. **Map the file structure** — what gets created, modified, and why
5. **Right-size the bites** — draw the boundaries before writing bodies
6. **Write the bites** — `add_bites`, in execution order, using the Bite
   Structure below
7. **Self-review** — spec coverage, placeholder scan, type consistency
8. **Read it back** — see the `## Steps` section the way the executor will
9. **Hand off** — offer the execution choice

## 1. Load the slice

`get_slice(<ref>)`. Confirm where it actually is:

- `needs_design` — stop. There is no approved design to break down; use
  `designing-a-slice`.
- `needs_steps` — this skill.
- `executing` — bites already exist. Read them before adding; extend the
  checklist, never restate it.

## 2. Constraints first — the highest-value text you will write

`update_slice(slice_id=…, constraints=…)` before you write a single bite.

This is the plan's global-constraints block, and it is a field rather than a
header: it renders on the board, and every agent that opens the slice is told to
treat it as binding.

What belongs there:

- **The project-wide requirements from the spec** — version floors, dependency
  limits, naming and copy rules, platform requirements — one line each, with
  exact values copied verbatim from the spec. **Every bite's requirements
  implicitly include this section.**
- **The landmine** — the thing that looks right and is wrong.
- **The invariants** that must still hold afterwards.
- **What "done" actually means** for this slice: which suite, which surface
  checked how, which environment.

Not a restatement of the spec.

Do it first because everything below is disposable: bites get checked off and
stop being read. Constraints outlive the work.

## 3. Scope Check

If the spec covers multiple independent subsystems, it should have been broken
into sibling slices during design. If it wasn't, do it now — see
"One slice, one plan" below. Each slice should produce working, testable
software on its own.

## 4. File Structure

Before defining bites, map out which files will be created or modified and what
each one is responsible for. This is where decomposition decisions get locked
in.

- Design units with clear boundaries and well-defined interfaces. Each file
  should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are
  more reliable when files are focused. Prefer smaller, focused files over large
  ones that do too much.
- Files that change together should live together. Split by responsibility, not
  by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large
  files, don't unilaterally restructure — but if a file you're modifying has
  grown unwieldy, including a split in the plan is reasonable.

This structure informs the bite decomposition. Each bite should produce
self-contained changes that make sense independently.

## 5. Bite Right-Sizing

A bite is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing bite boundaries: fold setup, configuration,
scaffolding, and documentation steps into the bite whose deliverable needs them;
split only where a reviewer could meaningfully reject one bite while approving
its neighbour. Each bite ends with an independently testable deliverable.

**Inside a bite, each step is one action (2-5 minutes):**

- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

That cycle is `writing-tests-first`, and the bite bodies you write are what tell
the executor to follow it.

## 6. Bite Structure

`add_bites(slice_id=…, bites=[{title, body}, …])`, in execution order.

**title** — imperative, names the deliverable.

**body** — markdown, and it *is* read back over MCP, so it is the working
instruction set. Use this structure:

````markdown
**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this bite uses from earlier bites — exact signatures]
- Produces: [what later bites rely on — exact function names, parameter
  and return types. A bite's implementer sees only their own bite; this
  block is how they learn the names and types neighbouring bites use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

The bite's own `status` is the tracked one — the boxes inside the body are the
executor's working list, not board state.

If a body only makes sense to someone who just read the whole spec, it is too
thin. The reader will not have read the whole spec.

## 7. No Placeholders

Every step must contain the actual content an engineer needs. These are **plan
failures** — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to bite N" (repeat the code — the executor may be reading bites out
  of order, and will not have the others open)
- Steps that describe what to do without showing how (code blocks required for
  code steps)
- References to types, functions, or methods not defined in any bite

## 8. Self-Review

After writing the complete checklist, look at the spec with fresh eyes and check
the bites against it. This is a checklist you run yourself — not a subagent
dispatch.

**1. Spec coverage:** Skim each section/requirement in the slice's spec. Can you
point to a bite that implements it? List any gaps.

**2. Placeholder scan:** Search your bite bodies for red flags — any of the
patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you
used in later bites match what you defined in earlier ones? A function called
`clearLayers()` in bite 3 but `clearFullLayers()` in bite 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move
on. If you find a spec requirement with no bite, add the bite.

## 9. One slice, one plan

If the spec really needs several independent plans — subsystems that ship and
verify separately — that is several slices, not one slice with forty bites.
Create the siblings now, give each its own spec, and have each spec name the
others by ref in one line. A checklist nobody can finish in one branch stops
telling you anything.

## 10. Read it back, then hand off

`get_slice(<ref>)` and read the `## Steps` section the way the executing agent
will see it.

Then offer the execution choice:

> **"Steps are on the board at `<ref>`. Two execution options:**
>
> **1. Subagent-driven (recommended when the bites are mostly independent)** — a
> fresh implementer per bite with a review between them, in this session.
>
> **2. This session, inline** — I already hold the context.
>
> **Which approach?"**

Option 1 is `delegating-a-slice`; option 2 is `executing-a-slice`.

## No plan file

Do not write a plan file — not `docs/…/plans/YYYY-MM-DD-*.md`, not anything like
it. The plan is the slice's constraints plus its bites, where the human already
looks and where the next session already reads. A plan file is a copy, and the
copy is what rots.

---

Forked from superpowers (MIT, © 2025 Jesse Vincent) — `writing-plans`, rewritten
so the plan is the board.
