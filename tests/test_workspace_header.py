"""The `.tuckit` file names the board; the helper turns it into a header.

The helper is a one-line program pasted into two manifests, run by a shell,
by two different agents. Everything that can go wrong with that -- quoting,
the folder it runs in, a file that is there but broken -- goes wrong silently
unless something runs the exact text the manifests carry. These tests do.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

import workspace  # noqa: E402

CLAUDE = json.loads((ROOT / "plugins/claude/.claude-plugin/plugin.json").read_text())
CODEX = json.loads((ROOT / "plugins/codex/.mcp.json").read_text())


def _run_claude(project: Path) -> dict:
    """As Claude Code runs it: through a shell, in the plugin folder, with
    ${CLAUDE_PROJECT_DIR} substituted into the string."""
    command = CLAUDE["mcpServers"]["tuckit"]["headersHelper"].replace(
        "${CLAUDE_PROJECT_DIR}", str(project)
    )
    out = subprocess.run(["sh", "-c", command], cwd=ROOT / "plugins" / "claude",
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def _run_codex(session: Path) -> dict:
    """As Codex runs it: through a shell, in the session folder, verbatim."""
    command = CODEX["mcpServers"]["tuckit"]["http_headers_helper"]
    out = subprocess.run(["sh", "-c", command], cwd=session,
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "src" / "deep").mkdir(parents=True)
    return root


CASES = {
    "plain": ('workspace = "acme"\n', {"X-Tuckit-Workspace": "acme"}),
    "with a comment": ('# which board\nworkspace = "acme-2"\n', {"X-Tuckit-Workspace": "acme-2"}),
    "no quotes": ("workspace = acme\n", None),
    "uppercase": ('workspace = "Acme"\n', None),
    "empty": ("", None),
}


@pytest.mark.parametrize("name", list(CASES))
@pytest.mark.parametrize("run", [_run_claude, _run_codex], ids=["claude", "codex"])
def test_both_manifests_and_the_readable_rule_agree(repo, name, run):
    body, expected = CASES[name]
    (repo / ".tuckit").write_text(body)
    start = repo / "src" / "deep"

    got = run(start)

    assert got == workspace.header(start)
    if expected is not None:
        assert got == expected
    else:
        # Broken is not absent: absent would let a one-workspace account land
        # on its only board without anyone noticing the file is wrong.
        value = got["X-Tuckit-Workspace"]
        assert value.startswith("!unreadable ") and value.endswith(".tuckit")


@pytest.mark.parametrize("run", [_run_claude, _run_codex], ids=["claude", "codex"])
def test_no_file_sends_no_header(repo, run):
    assert run(repo / "src") == {}


@pytest.mark.parametrize("run", [_run_claude, _run_codex], ids=["claude", "codex"])
def test_the_nearest_file_wins(repo, run):
    """A repository inside a folder that has its own `.tuckit` uses its own."""
    (repo.parent / ".tuckit").write_text('workspace = "outer"\n')
    (repo / ".tuckit").write_text('workspace = "inner"\n')
    assert run(repo / "src") == {"X-Tuckit-Workspace": "inner"}


def test_a_non_ascii_path_still_makes_a_sendable_header(tmp_path):
    """An HTTP header must be ASCII. Korean folder names are ordinary here."""
    folder = tmp_path / "프로젝트"
    folder.mkdir()
    (folder / ".tuckit").write_text("broken\n")
    value = _run_codex(folder)["X-Tuckit-Workspace"]
    value.encode("ascii")


def test_the_helper_survives_json_and_shell_quoting():
    """It is pasted into a JSON string and then a double-quoted shell argument."""
    for bad in ('"', "$", "`"):
        assert bad not in workspace.HELPER_SOURCE
    assert "\\\\" not in workspace.HELPER_SOURCE


# --- the primer line --------------------------------------------------------


def test_the_primer_names_the_board_and_the_file(repo, tmp_path):
    (repo / ".tuckit").write_text('workspace = "acme"\n')
    line = workspace.describe(repo / "src")
    assert "`acme`" in line and str(repo / ".tuckit") in line


def test_the_primer_says_what_to_do_when_nothing_names_a_board(repo):
    line = workspace.describe(repo / "src")
    assert ".tuckit" in line and 'workspace = "<slug>"' in line


def test_the_primer_says_a_broken_file_will_be_refused(repo):
    (repo / ".tuckit").write_text("workspace = acme\n")
    assert "refuse" in workspace.describe(repo / "src")


def test_emit_appends_the_board_to_the_primer(repo, tmp_path, monkeypatch):
    import importlib
    monkeypatch.setenv("TUCKIT_PLUGIN_STATE_DIR", str(tmp_path / "state"))
    (repo / ".tuckit").write_text('workspace = "acme"\n')
    emit = importlib.import_module("emit")
    out = subprocess.run(
        [sys.executable, str(ROOT / "plugins/codex/scripts/emit.py"),
         "--agent", "codex", "--event", "start", "--content", "primer"],
        input=json.dumps({"session_id": "s-1", "cwd": str(repo / "src")}),
        capture_output=True, text=True, check=True,
        env={"TUCKIT_PLUGIN_STATE_DIR": str(tmp_path / "state"), "PATH": "/usr/bin:/bin"},
    )
    text = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
    assert text.startswith(emit.load_content("primer"))
    assert "`acme`" in text


# --- a broken .tuckit stops the walk (review of TP-331) ---------------------


def _broken_entries(repo):
    """Each a `.tuckit` that is there but cannot be read as a board name."""
    yield "dangling symlink", lambda: (repo / ".tuckit").symlink_to(repo / "nowhere")
    yield "directory", lambda: (repo / ".tuckit").mkdir()
    yield "unreadable", lambda: ((repo / ".tuckit").write_text('workspace = "inner"\n'),
                                 (repo / ".tuckit").chmod(0))


@pytest.mark.parametrize("kind", ["dangling symlink", "directory", "unreadable"])
@pytest.mark.parametrize("run", [_run_claude, _run_codex], ids=["claude", "codex"])
def test_a_broken_file_is_not_skipped_for_a_parents_board(repo, kind, run):
    """Skipping it would carry the walk up to the parent's `.tuckit`, and the
    server would accept that board: a write that succeeds somewhere the
    repository never named."""
    (repo.parent / ".tuckit").write_text('workspace = "outer"\n')
    dict(_broken_entries(repo))[kind]()
    try:
        got = run(repo / "src")
        assert got == workspace.header(repo / "src")
        assert got["X-Tuckit-Workspace"].startswith("!unreadable ")
    finally:
        if (repo / ".tuckit").is_file():
            (repo / ".tuckit").chmod(0o644)


def test_claude_passes_the_project_folder_in_single_quotes():
    """Claude Code pastes the path into the string as raw text before a shell
    runs it. In double quotes a folder named `x$(cmd)` runs `cmd`."""
    helper = CLAUDE["mcpServers"]["tuckit"]["headersHelper"]
    assert helper.endswith(" '${CLAUDE_PROJECT_DIR}'")


def test_a_folder_name_cannot_run_a_command(tmp_path):
    # The helper runs in the plugin folder, so a relative `touch` lands there.
    marker = ROOT / "plugins" / "claude" / "tp331-injection-marker"
    project = tmp_path / "proj$(touch tp331-injection-marker)"
    project.mkdir()
    try:
        _run_claude(project)
        assert not marker.exists()
    finally:
        marker.unlink(missing_ok=True)
