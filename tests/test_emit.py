import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
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
    assert emit.build_start_payload("HELLO", "codex") == {"additional_contexts": ["HELLO"]}
    assert emit.build_start_payload("HELLO", "antigravity") == {
        "injectSteps": [{"ephemeralMessage": "HELLO"}]
    }

def test_build_stop_payload_per_agent():
    assert emit.build_stop_payload("WB", "claude-code") == {"decision": "block", "reason": "WB"}
    assert emit.build_stop_payload("WB", "codex") == {"continue": True, "systemMessage": "WB"}
    assert emit.build_stop_payload("WB", "antigravity") == {"decision": "continue", "reason": "WB"}

def test_allow_stop_payload_is_empty():
    for agent in emit.AGENTS:
        assert emit.allow_stop_payload(agent) == {}

def test_extract_session_id_prefers_known_keys():
    assert emit.extract_session_id({"session_id": "abc"}) == "abc"
    assert emit.extract_session_id({"conversationId": "xyz"}) == "xyz"
    assert emit.extract_session_id({}) == "no-session"

def test_build_payload_rejects_unknown_agent():
    import pytest
    with pytest.raises(ValueError):
        emit.build_start_payload("x", "bogus")
