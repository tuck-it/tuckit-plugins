import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "plugins" / "claude"


def test_plugin_json_valid():
    data = json.loads((CLAUDE / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "tuckit"


def test_marketplace_json_points_at_claude_plugin():
    data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    names = [p["name"] for p in data["plugins"]]
    assert "tuckit" in names
    entry = next(p for p in data["plugins"] if p["name"] == "tuckit")
    assert entry["source"] == "./plugins/claude"  # plugin lives in its own subdir


def test_cc_hooks_invoke_emit_for_both_events():
    hooks = json.loads((CLAUDE / "hooks" / "hooks.json").read_text())["hooks"]
    assert "SessionStart" in hooks and "Stop" in hooks
    blob = json.dumps(hooks)
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/emit.py" in blob
    assert "--event start" in blob and "--content primer" in blob
    assert "--event stop" in blob and "--content writeback" in blob
    assert "--agent claude-code" in blob


def test_antigravity_hooks_use_preinvocation_and_stop():
    hooks = json.loads(
        (ROOT / "plugins" / "antigravity" / ".agents" / "hooks.json").read_text()
    )
    blob = json.dumps(hooks)
    assert "PreInvocation" in hooks and "Stop" in hooks
    assert "__REPO__/plugins/antigravity/scripts/emit.py" in blob
    assert "antigravity" in blob
