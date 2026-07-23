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
    reason="../tuckit sibling repo not checked out",
)
def test_known_tools_from_server_matches_all_decorators():
    text = check_drift.SERVER_PY.read_text(encoding="utf-8")
    known = check_drift.known_tools_from_server()
    assert len(known) == text.count("@mcp.tool()")
    # sanity check: these have multi-line signatures (ctx on the next line)
    # and were previously missed by the single-line-only regex.
    assert {"create_slice", "list_slices", "update_bite"} <= known
