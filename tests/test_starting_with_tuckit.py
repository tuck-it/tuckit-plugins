from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "shared" / "skills"
NEW = SKILLS / "starting-with-tuckit" / "SKILL.md"
OLD = SKILLS / "adopting-a-project"
AGENTS = ("claude", "codex", "antigravity")


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


@pytest.mark.parametrize("agent", AGENTS)
def test_generated_plugins_ship_only_starting_with_tuckit(agent):
    skills = ROOT / "plugins" / agent / "skills"
    assert (skills / "starting-with-tuckit" / "SKILL.md").is_file()
    assert not (skills / "adopting-a-project").exists()


def test_primer_routes_an_empty_board_without_owning_the_safety_gate():
    primer = (ROOT / "shared" / "content" / "primer.md").read_text(
        encoding="utf-8"
    )
    assert "starting-with-tuckit" in primer
    assert "no Areas" in primer


def test_readme_exposes_one_first_use_skill_name():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "starting-with-tuckit" in readme
    assert "adopting-a-project" not in readme
