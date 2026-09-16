import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_drift  # noqa: E402

def test_flags_tool_name_other_than_entry_point():
    text = "call get_project_state, then list_slices and create_ticket"
    known = {"get_project_state", "list_slices", "create_ticket"}
    leaked = check_drift.find_leaked_tool_names(text, known)
    assert "list_slices" in leaked and "create_ticket" in leaked
    assert "get_project_state" not in leaked  # entry point is allowed

def test_clean_content_has_no_leaks():
    text = "read state via get_project_state; the MCP server lists the rest"
    known = {"get_project_state", "list_slices"}
    assert check_drift.find_leaked_tool_names(text, known) == []


@pytest.mark.skipif(
    not check_drift.SERVER_PY.exists(),
    reason="../tuckit-saas sibling repo not checked out",
)
def test_known_tools_from_server_matches_all_decorators():
    """Two readings of the same file, and they must agree.

    This used to compare the regex's result against `text.count("@mcp.tool()")`
    -- the same spelling on both sides. When the spelling was what had gone
    wrong (a tool declared `@mcp.tool(structured_output=False)`), both sides
    missed it identically and the assertion read 14 == 14 while the catalog was
    short one tool. `declared_tool_count` does not share the regex, so it can
    disagree with it.
    """
    known = check_drift.known_tools_from_server()
    assert len(known) == check_drift.declared_tool_count()
    # sanity check: these have multi-line signatures (ctx on the next line)
    # and were previously missed by the single-line-only regex.
    assert {"save_slice", "list_slices", "get_project_state"} <= known


@pytest.mark.skipif(
    not check_drift.SERVER_PY.exists(),
    reason="../tuckit-saas sibling repo not checked out",
)
def test_decorator_arguments_do_not_hide_a_tool():
    """A tool is a tool whether or not its decorator takes arguments."""
    text = check_drift.SERVER_PY.read_text(encoding="utf-8")
    bare_only = set(re.findall(r"@mcp\.tool\(\)\s+async def (\w+)\(", text))
    known = check_drift.known_tools_from_server()
    assert bare_only <= known
    # Not an equality: the point is that the wider pattern is a superset, and
    # it stays a correct test on the day every decorator happens to be bare.
    assert len(known) == check_drift.declared_tool_count()


@pytest.mark.skipif(
    not check_drift.SERVER_PY.exists(),
    reason="../tuckit-saas sibling repo not checked out",
)
def test_the_guard_actually_bites():
    """An empty catalog and a clean one are indistinguishable from the output.

    `find_leaked_tool_names` can only flag names it was handed, so a guard that
    knows nothing reports nothing and `check_drift.py` prints "ok" either way.
    Hand it a real tool name and check it comes back.
    """
    known = check_drift.known_tools_from_server()
    victim = sorted(known - {check_drift.ENTRY_POINT})[0]
    text = f"the agent should call {victim} at this point"
    assert check_drift.find_leaked_tool_names(text, known) == [victim]
    # and the same content reads clean against a catalog that knows nothing,
    # which is the failure mode this test exists to make visible.
    assert check_drift.find_leaked_tool_names(text, set()) == []


def test_a_decorator_the_pattern_cannot_read_shows_up_as_a_disagreement(monkeypatch, tmp_path):
    """The regex will go stale again; the count is what makes that loud.

    `[^)]*` stops at the first `)`, so a decorator holding a nested call --
    `@mcp.tool(annotations=Hint(readonly=True))` -- drops out of the catalog
    exactly the way `structured_output=False` did. That is not worth
    anticipating with a cleverer regex, because the next form will be different
    again. What matters is that the two readings disagree instead of agreeing
    on the wrong number.
    """
    server = tmp_path / "server.py"
    server.write_text(
        "@mcp.tool()\n"
        "async def list_slices(\n    ctx: Context,\n): ...\n"
        "@mcp.tool(annotations=Hint(readonly=True))\n"
        "async def get_slice(\n    ctx: Context,\n): ...\n",
        encoding="utf-8")
    monkeypatch.setattr(check_drift, "SERVER_PY", server)

    known = check_drift.known_tools_from_server()
    assert known == {"list_slices"}                 # the nested form is missed
    assert check_drift.declared_tool_count() == 2   # but it is still counted
    assert len(known) != check_drift.declared_tool_count()


def test_absent_sibling_skips_and_present_one_with_no_server_is_stale(monkeypatch, tmp_path, capsys):
    """Skip and STALE must stay distinguishable -- a guard that cannot tell
    "not checked out" from "path went stale" reports ok while reading nothing,
    which is how this one died at the 2026-08-27 rename."""
    missing = tmp_path / "nowhere" / check_drift.PRODUCT_REPO / "tuckit" / "core" / "mcp" / "server.py"
    monkeypatch.setattr(check_drift, "SERVER_PY", missing)
    assert check_drift.main() == 0
    assert "skip:" in capsys.readouterr().out

    stale = tmp_path / "here" / check_drift.PRODUCT_REPO / "tuckit" / "core" / "mcp" / "server.py"
    stale.parent.parent.parent.parent.mkdir(parents=True)   # the checkout exists
    monkeypatch.setattr(check_drift, "SERVER_PY", stale)
    assert check_drift.main() == 1
    assert "STALE:" in capsys.readouterr().out
