from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "shared" / "content"
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


# --- the hooks point instead of carrying (TP-257) -------------------------

SKILLS = Path(__file__).resolve().parent.parent / "shared" / "skills"

# What the always-on hook payload may cost. Both files are injected into every
# session's context whether or not that session touches the board, so anything
# written here is paid for by sessions that never needed it. They carried 925
# words between them before the substance moved into skills; this ceiling is
# what stops it drifting back.
MAX_INJECTED_WORDS = 250


def _named_skills(text: str) -> set[str]:
    """Skill names the content refers to, written as **`name`**."""
    import re

    return set(re.findall(r"\*\*`([a-z][a-z0-9-]+)`\*\*", text))


def test_hook_content_only_names_skills_that_exist():
    """A pointer to a skill that isn't there fails silently: the hook is just
    text, so a wrong name kills nothing and the checklist simply never runs."""
    for name in ("primer", "writeback"):
        text = (CONTENT / f"{name}.md").read_text(encoding="utf-8")
        for skill in _named_skills(text):
            assert (SKILLS / skill / "SKILL.md").is_file(), \
                f"{name}.md points at a skill that does not exist: {skill}"


def test_hook_content_points_at_the_reconcile_skill():
    """The write-back nudge is the only thing standing between a session and an
    unreconciled board. If it stops naming the skill, nothing else will."""
    text = (CONTENT / "writeback.md").read_text(encoding="utf-8")
    assert "reconciling-the-board" in text


def test_injected_hook_payload_stays_small():
    words = sum(
        len((CONTENT / f"{name}.md").read_text(encoding="utf-8").split())
        for name in ("primer", "writeback")
    )
    assert words <= MAX_INJECTED_WORDS, (
        f"primer + writeback = {words} words of always-on context "
        f"(ceiling {MAX_INJECTED_WORDS}). Move the substance into a skill "
        f"rather than raising this."
    )
