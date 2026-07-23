import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_plugin_json_valid():
    data = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "tuckit"

def test_cc_hooks_invoke_emit_for_both_events():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]
    assert "SessionStart" in hooks and "Stop" in hooks
    blob = json.dumps(hooks)
    assert "scripts/emit.py" in blob
    assert "--event start" in blob and "--content primer" in blob
    assert "--event stop" in blob and "--content writeback" in blob
    assert "--agent claude-code" in blob

def test_codex_hooks_invoke_emit():
    hooks = json.loads((ROOT / "codex" / "hooks.json").read_text())
    blob = json.dumps(hooks)
    assert "SessionStart" in hooks and "Stop" in hooks
    assert "scripts/emit.py" in blob
    assert "--agent" in blob and "codex" in blob
    assert "__REPO__" in blob  # install-time placeholder documented in README

def test_antigravity_hooks_use_preinvocation_and_stop():
    hooks = json.loads((ROOT / "antigravity" / ".agents" / "hooks.json").read_text())
    blob = json.dumps(hooks)
    assert "PreInvocation" in hooks and "Stop" in hooks
    assert "scripts/emit.py" in blob
    assert "antigravity" in blob
    assert "__REPO__" in blob
