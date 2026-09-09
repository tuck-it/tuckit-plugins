from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "shared" / "content"
# MCP tool names that must NOT be hardcoded in content (they drift over time).
FORBIDDEN_TOOL_NAMES = [
    "list_areas", "create_area", "list_slices", "save_slice",
    "add_note", "create_plan", "list_plans", "update_plan", "list_bites",
    "add_bites", "update_bite", "list_tickets", "create_ticket", "get_ticket",
    "update_ticket", "promote_ticket", "absorb_ticket", "release_ticket",
    "get_slice",
]

def _all_text():
    return "\n".join(p.read_text(encoding="utf-8") for p in CONTENT.glob("*.md"))

def test_content_files_exist():
    for name in ("primer", "door", "writeback", "domain"):
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
    for name in ("primer", "door", "writeback"):
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


# The door is charged differently from the other two: it fires on EVERY user
# prompt, not once a session, so a word here is paid for tens of times in one
# conversation. It is short because it is a signpost -- the substance it points
# at lives in skills that load only when they are needed.
MAX_DOOR_WORDS = 60


def test_the_door_is_short_enough_to_fire_every_prompt():
    words = len((CONTENT / "door.md").read_text(encoding="utf-8").split())
    assert words <= MAX_DOOR_WORDS, (
        f"door.md is {words} words and lands on every prompt "
        f"(ceiling {MAX_DOOR_WORDS}). Point at a skill instead of explaining."
    )


def test_the_door_sends_undesigned_work_to_the_design_skill():
    """The door exists because SessionStart lands once and then loses to
    whatever was said thirty turns later. If it stops naming the skill, it is
    a reminder to feel guilty rather than a route to take."""
    text = (CONTENT / "door.md").read_text(encoding="utf-8")
    assert "designing-a-slice" in text


def test_the_primer_names_the_skill_that_gates_implementation():
    """It named `reconciling-the-board` and `tuckit-domain` and never this one,
    so the only always-on text in the product pointed at how to tidy up after
    work and not at how to start it."""
    text = (CONTENT / "primer.md").read_text(encoding="utf-8")
    assert "designing-a-slice" in text


def test_the_primer_does_not_tell_agents_the_board_outranks_git():
    """It used to open with "not git". The scope made that defensible on a
    careful reading, and it is the first paragraph of every session -- a
    sentence that is only true if read carefully is a sentence that will be
    read wrong. The codebase is what the software IS; tuckit is why."""
    text = (CONTENT / "primer.md").read_text(encoding="utf-8")
    assert "not git" not in text
    # The one it replaced is still a real competitor, and still refused.
    assert "markdown file" in text


def test_the_workflow_names_the_skill_that_owns_each_step():
    """The workflow was six nouns. An agent that went looking for how work
    moves found the stages and no doors, which is most of why it never took
    one."""
    text = (CONTENT / "domain.md").read_text(encoding="utf-8")
    workflow = text.split("## The workflow")[1]
    for skill in ("designing-a-slice", "verifying-before-claiming",
                  "executing-a-slice", "delegating-a-slice",
                  "shipping-a-slice", "filing-the-inbox"):
        assert skill in workflow, f"the workflow never names {skill}"
        assert (SKILLS / skill / "SKILL.md").is_file(), skill


def test_no_plugin_ships_a_slash_command():
    """Every entry point is a skill.

    There was one command, /tuckit-sync, and it went stale: it kept instructing
    the agent to capture follow-ups on its own long after the checklist had
    grown an approval step. It lived outside shared/, so the build never
    regenerated it and no guard read it -- the two properties that let a second
    copy of anything drift unnoticed.

    Skills do not have that failure mode: one authored copy, generated into all
    three agents, and callable by a person or by the model. If a command ever
    earns its place again, delete this test on purpose rather than around it.
    """
    plugins = Path(__file__).resolve().parent.parent / "plugins"
    offenders = [p for p in plugins.glob("*/commands")]
    assert offenders == [], (
        f"hand-authored slash commands are back: {[str(p) for p in offenders]} — "
        f"make it a skill in shared/skills/ instead"
    )
