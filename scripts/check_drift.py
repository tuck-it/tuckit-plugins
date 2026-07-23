#!/usr/bin/env python3
"""Dev-only guard: content must not hardcode tuckit's MCP tool catalog.

Only `get_project_state` (the stable entry point) may appear. When ../tuckit is
checked out, the known-tool set is derived from its MCP server; otherwise the
script skips cleanly (a public plugin repo won't always have the sibling).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
ENTRY_POINT = "get_project_state"
SERVER_PY = REPO_ROOT.parent / "tuckit" / "tuckit" / "core" / "mcp" / "server.py"


def find_leaked_tool_names(content_text: str, known_tools: set) -> list:
    leaked = []
    for tool in sorted(known_tools):
        if tool == ENTRY_POINT:
            continue
        if re.search(rf"\b{re.escape(tool)}\b", content_text):
            leaked.append(tool)
    return leaked


def known_tools_from_server() -> set:
    text = SERVER_PY.read_text(encoding="utf-8")
    # tools are decorated with @mcp.tool() immediately followed by `async def <name>(`;
    # the signature itself may continue on the next line (e.g. `ctx: Context,` below it),
    # so we anchor on the decorator rather than trying to match the full parameter list.
    return set(re.findall(r"@mcp\.tool\(\)\s+async def (\w+)\(", text))


def main() -> int:
    if not SERVER_PY.exists():
        print(f"skip: {SERVER_PY} not found (tuckit not checked out)")
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
