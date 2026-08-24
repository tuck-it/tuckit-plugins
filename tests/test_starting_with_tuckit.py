from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "shared" / "skills"
NEW = SKILLS / "starting-with-tuckit" / "SKILL.md"
OLD = SKILLS / "adopting-a-project"


def _text() -> str:
    return NEW.read_text(encoding="utf-8")


def _frontmatter() -> str:
    return _text().split("---", 2)[1]


def test_starting_with_tuckit_replaces_adopting_a_project():
    assert NEW.is_file()
    assert not OLD.exists()
    assert "name: starting-with-tuckit" in _frontmatter()


def test_description_routes_first_use_and_excludes_existing_boards():
    description = _frontmatter().lower()
    assert "first" in description
    assert "no areas" in description
    assert "already" in description


def test_state_reads_precede_creation_instructions():
    text = _text()
    reads_complete_at = max(
        text.index("`get_project_state`"),
        text.index("`list_areas`"),
    )
    first_creation = min(
        text.index("`create_area`"),
        text.index("`create_slice`"),
    )
    assert reads_complete_at < first_creation
