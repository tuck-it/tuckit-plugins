---
name: tuckit-domain
description: Use when working in a tuckit-tracked workspace and you need tuckit's model (Area/Slice/Bite), how to read project state, or the idea→slice→execute→ship workflow.
---

Read `${CLAUDE_PLUGIN_ROOT}/content/domain.md` for the full tuckit domain reference, then
apply it. Always read project state via the `get_project_state` MCP tool rather
than git. The live MCP tool list is whatever the tuckit server exposes in this
session — discover tools there rather than assuming a fixed set.
