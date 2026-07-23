from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "content"
# MCP tool names that must NOT be hardcoded in content (they drift over time).
FORBIDDEN_TOOL_NAMES = [
    "list_areas", "create_area", "list_slices", "create_slice", "update_slice",
    "add_note", "create_plan", "list_plans", "update_plan", "list_bites",
    "add_bites", "update_bite", "list_tickets", "create_ticket", "get_ticket",
    "update_ticket", "promote_ticket", "absorb_ticket", "release_ticket",
    "get_slice",
]

def _all_text():
    return "\n".join(p.read_text(encoding="utf-8") for p in CONTENT.glob("*.md"))

def test_content_files_exist():
    for name in ("primer", "writeback", "domain"):
        assert (CONTENT / f"{name}.md").is_file(), name

def test_primer_names_get_project_state():
    assert "get_project_state" in (CONTENT / "primer.md").read_text(encoding="utf-8")

def test_content_does_not_hardcode_tool_catalog():
    text = _all_text()
    leaked = [t for t in FORBIDDEN_TOOL_NAMES if t in text]
    assert leaked == [], f"content hardcodes drift-prone tool names: {leaked}"
