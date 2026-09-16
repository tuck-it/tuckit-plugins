import io
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared" / "scripts"))
import emit  # noqa: E402

def test_load_content_reads_and_strips():
    text = emit.load_content("primer")
    assert "get_project_state" in text
    assert text == text.strip()

def test_first_time_true_then_false(tmp_path):
    assert emit.first_time("sessABC", "primer", base=tmp_path) is True
    assert emit.first_time("sessABC", "primer", base=tmp_path) is False

def test_first_time_is_per_session_and_per_tag(tmp_path):
    assert emit.first_time("s1", "primer", base=tmp_path) is True
    assert emit.first_time("s2", "primer", base=tmp_path) is True      # different session
    assert emit.first_time("s1", "writeback", base=tmp_path) is True   # different tag
    assert emit.first_time("s1", "primer", base=tmp_path) is False     # repeat

def test_build_start_payload_per_agent():
    assert emit.build_start_payload("HELLO", "claude-code") == {
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "HELLO"}
    }
    # Codex takes the same wire as Claude Code. It used to be given
    # {"additional_contexts": [...]}, a field Codex has never had — the hook ran
    # and the primer was dropped on the floor with no error anywhere.
    assert emit.build_start_payload("HELLO", "codex") == {
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "HELLO"}
    }
    # agy is deliberately absent: `ephemeralMessage` is the only thing its
    # PreInvocation can inject and it does not survive the turn, so the
    # orientation ships as rules/AGENTS.md instead of a start hook.
    with pytest.raises(ValueError, match="rules/AGENTS.md"):
        emit.build_start_payload("HELLO", "antigravity")

def test_build_stop_payload_per_agent():
    assert emit.build_stop_payload("WB", "claude-code") == {
        "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": "WB"}}
    assert emit.build_stop_payload("WB", "antigravity") == {"decision": "continue", "reason": "WB"}


def test_codex_has_no_stop_payload():
    """Codex ships no Stop hook, so asking for its payload is a bug, not a case.

    The branch this replaces returned {"continue": True, "systemMessage": ...}.
    Codex accepts that and shows the text to the human; the model never sees
    it. Stop is the one Codex event with no `additionalContext`, and the only
    field on it that reaches the model is `decision: "block"` with a `reason`.
    Measured against codex-cli 0.154.0: `block` yields `hook: Stop Blocked` and
    one more model turn, `systemMessage` yields `hook: Stop Completed` and the
    turn ends.

    Blocking was the available fix and was turned down -- it costs a model turn
    every session, and a session that changed nothing follows the write-back
    text's own instruction to say nothing, which lands as an empty assistant
    turn and an empty --output-last-message. The primer already tells Codex to
    reconcile when the session ends.
    """
    with pytest.raises(ValueError, match="primer"):
        emit.build_stop_payload("WB", "codex")

def test_allow_stop_payload_is_empty():
    for agent in emit.AGENTS:
        assert emit.allow_stop_payload(agent) == {}

def test_extract_session_id_prefers_known_keys():
    assert emit.extract_session_id({"session_id": "abc"}) == "abc"
    assert emit.extract_session_id({"conversationId": "xyz"}) == "xyz"
    fallback = emit.extract_session_id({})
    assert fallback and fallback == str(os.getppid())

def test_build_payload_rejects_unknown_agent():
    import pytest
    with pytest.raises(ValueError):
        emit.build_start_payload("x", "bogus")


def _run(monkeypatch, tmp_path, argv, stdin_text=""):
    monkeypatch.setenv("TUCKIT_PLUGIN_STATE_DIR", str(tmp_path))
    buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", buf)
    rc = emit.main(argv, stdin_text=stdin_text)
    return rc, json.loads(buf.getvalue())


def test_main_claude_start_injects_primer(monkeypatch, tmp_path):
    rc, out = _run(monkeypatch, tmp_path,
                   ["--agent", "claude-code", "--event", "start", "--content", "primer"])
    assert rc == 0
    assert "get_project_state" in out["hookSpecificOutput"]["additionalContext"]


def test_agy_start_is_gone_from_the_hook_file_and_the_payloads():
    """Both halves have to go together. A hooks.json that still called
    `--event start` would now raise instead of printing an empty object, and a
    payload builder that still answered would resurrect the ephemeral primer
    the rule file replaced."""
    hooks = json.loads((ROOT / "plugins" / "antigravity" / "hooks.json").read_text())
    assert "--event start" not in json.dumps(hooks)
    with pytest.raises(ValueError):
        emit.build_start_payload("HELLO", "antigravity")


def test_main_codex_start_injects_primer_on_the_wire_codex_reads(monkeypatch, tmp_path):
    """Codex's SessionStart output is `hookSpecificOutput.additionalContext`.
    Any other top-level key is ignored silently, so asserting the primer text is
    *somewhere* in the payload would pass on a payload Codex throws away."""
    rc, out = _run(monkeypatch, tmp_path,
                   ["--agent", "codex", "--event", "start", "--content", "primer"])
    assert rc == 0
    assert list(out) == ["hookSpecificOutput"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "get_project_state" in out["hookSpecificOutput"]["additionalContext"]


@pytest.mark.parametrize("agent", ["claude-code", "codex"])
def test_start_injects_the_primer_once_per_session(monkeypatch, tmp_path, agent):
    """SessionStart fires on startup, resume, clear AND compact, so an ungated
    primer is re-injected into the context that compaction has just freed. The
    second start of the same session prints the empty envelope; a different
    session still gets the primer. Both agents share this branch."""
    same = json.dumps({"session_id": f"START-{agent}"})
    _, first = _run(monkeypatch, tmp_path,
                    ["--agent", agent, "--event", "start", "--content", "primer"], same)
    _, again = _run(monkeypatch, tmp_path,
                    ["--agent", agent, "--event", "start", "--content", "primer"], same)
    _, other = _run(monkeypatch, tmp_path,
                    ["--agent", agent, "--event", "start", "--content", "primer"],
                    json.dumps({"session_id": f"OTHER-{agent}"}))

    assert "get_project_state" in first["hookSpecificOutput"]["additionalContext"]
    assert again == {}
    assert "get_project_state" in other["hookSpecificOutput"]["additionalContext"]


def test_start_and_stop_are_gated_separately(monkeypatch, tmp_path):
    """One tag per hook. Sharing a marker would let whichever fired first
    silence the other for the rest of the session."""
    stdin = json.dumps({"session_id": "S12"})
    _, start = _run(monkeypatch, tmp_path,
                    ["--agent", "claude-code", "--event", "start", "--content", "primer"], stdin)
    _, stop = _run(monkeypatch, tmp_path,
                   ["--agent", "claude-code", "--event", "stop", "--content", "writeback"], stdin)
    assert start["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert stop["hookSpecificOutput"]["hookEventName"] == "Stop"


def test_the_codex_stop_wire_is_read_off_the_binary_not_guessed():
    """What let the wrong Stop payload ship for weeks was a subset assertion
    over our own dict: the test named four of the six fields Codex accepts and
    passed, while the two it omitted -- `decision` and `reason` -- were the
    only ones that reach the model.

    So assert the wire itself, from the source that settles it. Codex embeds
    its hook JSON schemas in the binary; `strings <codex> | grep -A40
    'stop.command.output'` prints this one. The web docs do not carry it.
    """
    stop_wire = {"continue", "decision", "reason",
                 "stopReason", "suppressOutput", "systemMessage"}
    injecting = {"decision", "reason"}      # the only fields the model sees
    assert injecting < stop_wire
    assert "hookSpecificOutput" not in stop_wire   # unlike SessionStart
    assert "additionalContext" not in stop_wire    # unlike UserPromptSubmit


def test_main_stop_reminds_once_then_allows(monkeypatch, tmp_path):
    stdin = json.dumps({"session_id": "S9"})
    _, first = _run(monkeypatch, tmp_path,
                    ["--agent", "claude-code", "--event", "stop", "--content", "writeback"], stdin)
    _, second = _run(monkeypatch, tmp_path,
                     ["--agent", "claude-code", "--event", "stop", "--content", "writeback"], stdin)
    assert first["hookSpecificOutput"]["hookEventName"] == "Stop"
    assert "board" in first["hookSpecificOutput"]["additionalContext"].lower()
    assert second == {}


def test_claude_stop_payload_avoids_the_blocking_error_path(monkeypatch, tmp_path):
    """The reminder must not surface as a "Stop hook error:" — see build_stop_payload."""
    stdin = json.dumps({"session_id": "S10"})
    _, payload = _run(monkeypatch, tmp_path,
                      ["--agent", "claude-code", "--event", "stop", "--content", "writeback"], stdin)
    assert "decision" not in payload
    assert "reason" not in payload


# --- the door: the only event that fires when work is asked for -----------


@pytest.mark.parametrize("agent", ["claude-code", "codex"])
def test_prompt_payload_is_the_wire_each_agent_reads(agent):
    out = emit.build_prompt_payload("knock", agent)
    assert out["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert out["hookSpecificOutput"]["additionalContext"] == "knock"


def test_agy_has_no_prompt_hook_because_its_only_pre_turn_event_is_ephemeral():
    """A one-turn lifetime would actually suit a per-prompt reminder. The
    reason it still ships in rules/AGENTS.md is that agy accepts a hook file
    it has not parsed and reports nothing either way, so an unverified schema
    here would install clean and do nothing."""
    with pytest.raises(ValueError):
        emit.build_prompt_payload("knock", "antigravity")


def test_the_door_fires_on_every_prompt_not_once_a_session(tmp_path):
    """Once per session is what SessionStart already does, and a reminder that
    fired once at position zero is the state this was built to fix."""
    import io, json as _json
    from contextlib import redirect_stdout

    seen = []
    for _ in range(3):
        buf = io.StringIO()
        with redirect_stdout(buf):
            emit.main(["--agent", "claude-code", "--event", "prompt",
                       "--content", "door"],
                      stdin_text=_json.dumps({"session_id": "same-session"}))
        seen.append(_json.loads(buf.getvalue()))

    assert all(p["hookSpecificOutput"]["additionalContext"] for p in seen)
