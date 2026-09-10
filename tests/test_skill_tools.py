"""Guard: the skills name MCP tools deliberately, so renames stay loud.

`shared/content/` may not name tools at all (test_content) — it is prose that
has to survive the catalog changing. Skills are the opposite: one that tells the
agent to "discover the tools yourself" cannot drive a pipeline, so they name
them outright.

The trade for that is this test. Every tool the skills name must exist in the
sibling tuckit checkout's live catalog, and every live tool the skills name must
be listed here first. When tuckit renames or drops a tool, this goes red instead
of the skills quietly instructing agents to call something that is gone — which
is exactly what happened to `create_plan`.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_drift  # noqa: E402

SKILLS = Path(__file__).resolve().parent.parent / "shared" / "skills"

# Tools the skills are allowed to name, because the workflow depends on them.
SKILL_TOOLS = {
    "get_project_state",
    "list_areas",
    "create_area",
    "list_slices",
    "get_slice",
    "save_slice",
    "append_decision",
    "record_verification",
    "add_note",
    "append_priority_policy",
}

requires_tuckit = pytest.mark.skipif(
    not check_drift.SERVER_PY.exists(),
    reason="../tuckit sibling repo not checked out",
)


def _skills_text():
    """Every markdown a skill ships, not just its SKILL.md.

    The prompt templates are where a skill actually tells a subagent which tool
    to call, and they outlived a tool rename once because this glob stopped at
    SKILL.md: `list_bites` sat in two reviewer templates while all three tests
    here were green.
    """
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(SKILLS.rglob("*.md")))


def test_every_allowlisted_tool_is_actually_used():
    """A stale allowlist entry would silently widen what the next test permits."""
    text = _skills_text()
    unused = [t for t in sorted(SKILL_TOOLS) if not re.search(rf"\b{t}\b", text)]
    assert unused == [], f"allowlisted but not named by any skill: {unused}"


@requires_tuckit
def test_skills_only_name_tools_that_exist():
    known = check_drift.known_tools_from_server()
    gone = sorted(SKILL_TOOLS - known)
    assert gone == [], f"skills instruct agents to call tools tuckit no longer exposes: {gone}"


@requires_tuckit
def test_unlisted_tools_do_not_leak_into_skills():
    """Naming a tool is a decision; it goes through the allowlist above."""
    known = check_drift.known_tools_from_server()
    leaked = check_drift.find_leaked_tool_names(_skills_text(), known - SKILL_TOOLS)
    assert leaked == [], f"skills name tools that are not in SKILL_TOOLS: {leaked}"
