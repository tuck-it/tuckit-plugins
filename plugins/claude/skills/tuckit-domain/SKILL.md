---
name: tuckit-domain
description: Use when working in a tuckit-tracked workspace and you need tuckit's model (Area, Slice, Capture), who decides what, how to read project state, or how work moves from capture to promise to pull request.
---

Read `${CLAUDE_PLUGIN_ROOT}/content/domain.md` for the model, then apply it. Read project
state with `get_project_state` rather than git. Where a tool name below
disagrees with the live MCP tool list, the server is right.

This file adds only the tool surface that the reference deliberately does not
carry.

## Slices

`save_slice` creates (with `area_id`, required; `""` is refused) or updates.
`spec` and `done_when` are the promise; `assignee="me"` takes the slice.
`get_slice(<ref>)` reads one slice in full, decisions included.
`list_slices(query=…, assignee=…)` searches the workspace.

`append_decision(slice_id, body)` is append-only. Four moves: what was chosen
(one bold sentence), why, what was turned down and why, and what the choice
leans on. Say when a person overrode you.

`add_note` is for what happened (a PR link, why you stopped). `constraints` is
for what the next agent must not repeat.

## Captures

`create_capture(title, context="")` — the title in the words you would say it,
the context is what you SAW. There is no spec, priority, assignee or done_when
on a capture: each would be a claim nobody has made.

`list_captures()` reads the Inbox. **It is a different set from `list_slices`,
not a filter on it.**

`triage_capture(capture_id, decision, area_id=None)` — `"promote"` (needs
`area_id`), `"dismiss"` or `"restore"`. A promoted slice starts with an empty
spec.

## Relations

`link_slices(links, unlink=False)`, each link `{"from", "to", "kind", "note"}`.
`kind` defaults to `"blocks"`, read "from blocks to". Unlinking is the same tool
with `unlink=True`. The `note` is required: say why B cannot meet its own
done_when until A ships. `save_slice(status="shipped")` is refused while
something still blocks the slice.

## Evidence and images

`record_verification(slice_id, evidence)` writes what was observed and moves the
slice to `ready_to_ship`. `evidence=""` withdraws it.

`create_image_upload(sha256, byte_size, content_type="")` answers `{"url"}` if
those bytes are stored, or `{"upload_url", "expires_in"}` — POST the bytes there
to get the url. png, jpeg or webp, 2MB at most. Reference it as markdown in
evidence, a spec or a decision. Use one only when the claim can be seen on a
screen and nowhere else; pasted test output beats a screenshot of it.
