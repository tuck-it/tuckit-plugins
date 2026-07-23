import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "plugins" / "claude"


def test_plugin_json_valid():
    data = json.loads((CLAUDE / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "tuckit"


def test_cc_plugin_bundles_mcp_via_user_config():
    """The MCP server is wired from userConfig so installing the plugin also
    connects tuckit's MCP — with no credentials or URL committed to the repo."""
    data = json.loads((CLAUDE / ".claude-plugin" / "plugin.json").read_text())

    uc = data["userConfig"]
    assert uc["mcp_url"]["required"] is True
    assert uc["mcp_token"]["required"] is True
    assert uc["mcp_token"]["sensitive"] is True  # token goes to the OS keychain

    server = data["mcpServers"]["tuckit"]
    assert server["type"] == "http"
    assert server["url"] == "${user_config.mcp_url}"
    assert server["headers"]["Authorization"] == "Bearer ${user_config.mcp_token}"


def test_cc_plugin_hardcodes_no_secret_or_endpoint():
    """Guard: the public manifest must never carry a real URL or token."""
    blob = (CLAUDE / ".claude-plugin" / "plugin.json").read_text()
    server = json.loads(blob)["mcpServers"]["tuckit"]
    # Every credential-bearing value must be a userConfig placeholder, not a literal.
    assert "://" not in server["url"], "MCP url must be a placeholder, not a real endpoint"
    for value in server["headers"].values():
        assert "${user_config." in value, "auth headers must come from userConfig"


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
