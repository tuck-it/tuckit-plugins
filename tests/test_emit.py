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
