import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "plugins" / "claude"

# The one endpoint we deliberately commit: tuckit Cloud, the default for
# everyone who isn't self-hosting. It is public and carries no credential.
PUBLIC_MCP_URL = "https://app.tuckit.dev/mcp"


def test_plugin_json_valid():
    data = json.loads((CLAUDE / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "tuckit"


def test_cc_plugin_bundles_mcp_via_user_config():
    """The MCP server is wired from userConfig so installing the plugin also
    connects tuckit's MCP. Auth is OAuth in the browser, so the manifest needs
    a URL knob and no credential of any kind."""
    data = json.loads((CLAUDE / ".claude-plugin" / "plugin.json").read_text())

    uc = data["userConfig"]
    # Optional, because the default already points at tuckit Cloud — only a
    # self-hoster has to touch it.
    assert uc["mcp_url"]["required"] is False
    assert uc["mcp_url"]["default"] == PUBLIC_MCP_URL
    # OAuth replaced the pasted token; a token knob must not come back.
    assert "mcp_token" not in uc

    server = data["mcpServers"]["tuckit"]
    assert server["type"] == "http"
    assert server["url"] == "${user_config.mcp_url}"
    assert "headers" not in server, "OAuth carries auth; no header to send"


def test_cc_plugin_hardcodes_no_secret_or_private_endpoint():
    """Guard: the public manifest must never carry a credential, and the only
    URL it commits is the public tuckit Cloud endpoint."""
    blob = (CLAUDE / ".claude-plugin" / "plugin.json").read_text()
    data = json.loads(blob)

    server = data["mcpServers"]["tuckit"]
    assert "://" not in server["url"], "MCP url must be a placeholder, not a literal endpoint"
    # No headers today. If any return, each must resolve from userConfig.
    for name, value in server.get("headers", {}).items():
        assert "${user_config." in value, f"{name} header must come from userConfig"

    # Scan the server block, not the whole file: the prose descriptions talk
    # about tokens and authorization on purpose, and must stay free to do so.
    servers_blob = json.dumps(data["mcpServers"]).lower()
    for marker in ("bearer ", "authorization", "secret", "password", "token", "api_key"):
        assert marker not in servers_blob, f"mcpServers must not carry {marker!r}"

    # Every committed URL is the public endpoint, with no user:pass@ embedded.
    urls = re.findall(r"https?://[^\"\s]+", blob)
    assert set(urls) == {PUBLIC_MCP_URL}, f"unexpected URL committed: {urls}"
    assert "@" not in PUBLIC_MCP_URL


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
