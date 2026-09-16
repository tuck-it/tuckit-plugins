#!/usr/bin/env python3
"""Dev-only guard: content must not hardcode tuckit's MCP tool catalog.

Only `get_project_state` (the stable entry point) may appear. When the product
checkout is beside this repo, the known-tool set is derived from its MCP server;
otherwise the script skips cleanly (a public plugin repo won't always have the
sibling). A checkout that IS present but has no server at the expected path is
an error rather than a skip: that means the path below went stale, which is what
happened when the product repo was renamed `tuckit/` -> `tuckit-saas/` and this
guard silently skipped for every run after the cutover.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "shared" / "content"
ENTRY_POINT = "get_project_state"
PRODUCT_REPO = "tuckit-saas"
SERVER_REL = Path(PRODUCT_REPO) / "tuckit" / "core" / "mcp" / "server.py"


def _find_server_py() -> Path:
    """Locate the sibling tuckit checkout's MCP server.

    Normally it sits next to this repo. Development happens in worktrees, which
    push the sibling further up — one level for `<workspace>/.worktrees/<name>/`
    and two for `<workspace>/<repo>/.worktrees/<name>/`, which is what
    `git worktree add` inside the repo produces. Both layouts are in use here,
    so both are searched: a guard that silently skips in the layout people
    actually work in is a guard that never runs. Returns the plain sibling path
    when none exists, so the skip message names the expected location.
    """
    bases = (REPO_ROOT.parent, REPO_ROOT.parent.parent, REPO_ROOT.parent.parent.parent)
    for base in bases:
        candidate = base / SERVER_REL
        if candidate.exists():
            return candidate
    # No server found. If the product checkout itself is there, the path above is
    # stale and the caller must fail instead of skipping.
    for base in bases:
        if (base / PRODUCT_REPO).is_dir():
            return base / SERVER_REL
    return REPO_ROOT.parent / SERVER_REL


SERVER_PY = _find_server_py()


def find_leaked_tool_names(content_text: str, known_tools: set) -> list:
    leaked = []
    for tool in sorted(known_tools):
        if tool == ENTRY_POINT:
            continue
        if re.search(rf"\b{re.escape(tool)}\b", content_text):
            leaked.append(tool)
    return leaked


# A tool is `@mcp.tool(...)` immediately followed by `async def <name>(`. The
# signature itself may continue on the next line (e.g. `ctx: Context,` below
# it), so anchor on the decorator rather than matching the parameter list.
#
# The parentheses take arguments. `@mcp.tool(structured_output=False)` is one
# of them, and a pattern requiring EMPTY parens silently dropped that tool from
# the catalog for five days -- which means the leak check could not have
# flagged its name, because it only searches for names it was handed.
TOOL_DECL = re.compile(r"@mcp\.tool\([^)]*\)\s+async def (\w+)\(")

# Counts declarations without reusing TOOL_DECL, so the two can disagree. The
# assertion this feeds used to compare TOOL_DECL's result against
# `text.count("@mcp.tool()")` -- the same spelling on both sides, so when the
# spelling was what had gone wrong, both sides were wrong by the same tool and
# the comparison read 14 == 14.
DECORATOR = "@mcp.tool("


def known_tools_from_server() -> set:
    return set(TOOL_DECL.findall(SERVER_PY.read_text(encoding="utf-8")))


def declared_tool_count() -> int:
    """How many tools the server declares, counted independently of TOOL_DECL."""
    return SERVER_PY.read_text(encoding="utf-8").count(DECORATOR)


def main() -> int:
    if not SERVER_PY.exists():
        if SERVER_PY.parents[3].is_dir():
            print(f"STALE: {SERVER_PY.parents[3]} is checked out but {SERVER_PY} does not exist")
            return 1
        print(f"skip: {SERVER_PY} not found ({PRODUCT_REPO} not checked out)")
        return 0
    known = known_tools_from_server()
    content = "\n".join(p.read_text(encoding="utf-8") for p in CONTENT_DIR.glob("*.md"))
    leaked = find_leaked_tool_names(content, known)
    if leaked:
        print(f"DRIFT: content hardcodes tool names beyond {ENTRY_POINT}: {leaked}")
        return 1
    print(f"ok: content references only {ENTRY_POINT}; {len(known)} tools known")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
