---
name: tuckit-domain
description: Use when working in a tuckit-tracked workspace and you need tuckit's model (Area, Slice, Capture), how to read project state, or the capture→slice→verify→ship workflow.
---

Read `{{ROOT}}/content/domain.md` for the full tuckit domain reference, then
apply it. Always read project state via the `get_project_state` MCP tool rather
than git. The live MCP tool list is whatever the tuckit server exposes in this
session; where a name below disagrees with it, the server is right. What follows
is the part of the model that is easiest to get wrong, and the tools it runs
through.

## Captures

`content/domain.md` says what the three objects are and why the third one
exists. This file adds only the tool surface, which that reference deliberately
does not carry.

A Slice always lives in an Area: `area_id` is required when you create one with
`save_slice`, and `area_id=""` is refused rather than meaning anything.

`create_capture(title, context="")` — the title is one line in the words you
would say it, the context is what you SAW, in prose. There is deliberately no
`spec` argument, and no priority, assignee, stage or done_when anywhere on the
object: every one of those would be a claim nobody has made yet.

`list_captures(dismissed=False, limit=50)` reads the Inbox, newest first, with
`id`, `title`, `context`, `state`, `source`, `age_days` and `ref` (absent once
promoted) on each row. **It returns a different set from `list_slices`, not a
filter on it.** An agent that reads the board with `list_slices` and concludes
the Inbox is empty has not looked at the Inbox. `get_project_state.inbox` counts
captures, not slices.

`triage_capture(capture_id, decision, area_id=None)` — `decision` is
`"promote"`, `"dismiss"` or `"restore"`. `area_id` is required to promote and
ignored otherwise; `area_id=""` is refused. Promoting leaves the new slice's
spec empty, so the design written later replaces nothing.

## Relations between slices

`link_slices(links, unlink=False)`, where `links` is a list of
`{"from", "to", "kind", "note"}`. `from` and `to` take refs or ids; `kind`
defaults to `"blocks"` and reads "from blocks to". Unlinking is the same tool
with `unlink=True` — there is no separate unlink tool. The call is
all-or-nothing, so a failure changes nothing and a retry is safe, and relinking
a pair that already exists changes nothing. A link that would close a circle is
refused, and the error names the path.

The criterion and the reason the `note` is required are in `content/domain.md`,
and it reduces to this: record that A blocks B only when **B cannot meet its own
done_when until A ships**. Every link carries a written reason. You need nobody's
approval to write one, because unlinking takes it back.

`save_slice(status="shipped")` is refused while something still blocks the
slice.

## Images

`create_image_upload(sha256, byte_size, content_type="")` is the first of two
calls: it answers `{"url"}` when those bytes are already stored, or
`{"upload_url", "expires_in"}` — POST the bytes there and get back `{"url"}`.
Reference it as markdown, `![what the shot shows](<that url>)`, in `evidence`, a
spec or a decision. png, jpeg or webp only, never SVG, 2MB ceiling. The call
writes to no slice by itself, and the image belongs to the workspace rather than
to one slice.

Use one only where the claim is confirmable on a screen and nowhere else — a
render, a layout, a visual state. `verifying-before-claiming` owns when evidence
needs a picture; a screenshot of test output says less than the output pasted as
text.
