import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "plugins" / "claude"
ANTIGRAVITY = ROOT / "plugins" / "antigravity"

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


# --- agy plugin package ----------------------------------------------------
# The shape below is agy's, not Claude Code's, and the two are close enough to
# look interchangeable while behaving nothing alike. It is documented in the
# CLI's own bundled skill — `builtin/skills/agy-customizations/docs/hooks.md`,
# which the web docs do not cover — and was confirmed against agy 1.1.13.
#
# Nothing about it fails loudly. `agy plugin install` prints "hooks : N
# processed" for a file it has not parsed; the parse happens at session start
# and a bad one becomes a single log warning; and a file that parses but names
# no event registers zero handlers and reports nothing at all. Every wrong
# shape below installs clean and does nothing, so these tests are the only
# place the shape is actually checked.

# agy runs a hook with the working directory set to the directory holding
# hooks.json, which for the package is the plugin root. That relative path is
# what makes the package installable anywhere: agy has no plugin-root variable
# (`CLAUDE_PLUGIN_ROOT` and every `*_PLUGIN_ROOT` spelling are absent from the
# binary), so an absolute path would have to guess the install location.
AGY_EMIT = "python3 scripts/emit.py"


def _agy_hook_files():
    return [ANTIGRAVITY / "hooks.json"]


def test_agy_plugin_json_names_the_plugin():
    data = json.loads((ANTIGRAVITY / "plugin.json").read_text())
    assert data["name"] == "tuckit"


def test_agy_hooks_key_on_hook_name_then_event():
    """agy's top-level keys are hook NAMES; the event lives one level down.
    Keying on the event directly parses without complaint and registers
    nothing, because `PreInvocation` is read as a hook named "PreInvocation"
    whose unrecognised fields are dropped."""
    for path in _agy_hook_files():
        hooks = json.loads(path.read_text())
        events = {e for spec in hooks.values() if isinstance(spec, dict) for e in spec}
        assert events == {"PreInvocation", "Stop"}, f"{path.name}: {events}"
        for name, spec in hooks.items():
            assert "command" not in spec, f"{path.name}: {name} keyed on event"


def test_agy_hook_handlers_take_a_command_string_not_an_argv_list():
    """Handlers are flat lists of objects for PreInvocation/Stop, and `command`
    is a shell string (run through `sh -c`) — an argv array is dropped."""
    for path in _agy_hook_files():
        for name, spec in json.loads(path.read_text()).items():
            for event, handlers in spec.items():
                assert isinstance(handlers, list), f"{path.name}: {name}/{event}"
                for handler in handlers:
                    assert isinstance(handler["command"], str), f"{path.name}: {name}"


def test_agy_hooks_reject_the_claude_wrapper_key():
    """A top-level "hooks" key is Claude Code's envelope. agy fails the WHOLE
    file on it (`invalid hook "hooks": command hook must specify 'command'`),
    so one stray key kills every other hook in the file."""
    for path in _agy_hook_files():
        assert "hooks" not in json.loads(path.read_text())


def test_agy_hooks_invoke_emit_for_both_events():
    blob = json.dumps(json.loads((ANTIGRAVITY / "hooks.json").read_text()))
    assert "PLUGIN_ROOT" not in blob
    assert f"{AGY_EMIT} --agent antigravity --event start --content primer" in blob
    assert f"{AGY_EMIT} --agent antigravity --event stop --content writeback" in blob


def test_agy_ships_no_workspace_agents_copy():
    """The `.agents/` copy is gone on purpose: it needed an absolute path
    substituted by hand, and `agy plugin install` needs none. Reintroducing it
    would restore a second install path that drifts from this one."""
    assert not (ANTIGRAVITY / ".agents").exists()


def test_agy_mcp_config_is_a_separate_file_and_carries_no_credential():
    """agy reads MCP from mcp_config.json only; `mcpServers` inlined in
    plugin.json is silently skipped (`mcpServers : skipped (not found)`).
    Auth is OAuth in the browser, so nothing here may carry a credential."""
    assert "mcpServers" not in json.loads((ANTIGRAVITY / "plugin.json").read_text())

    servers = json.loads((ANTIGRAVITY / "mcp_config.json").read_text())["mcpServers"]
    assert servers["tuckit"]["serverUrl"] == PUBLIC_MCP_URL
    blob = json.dumps(servers).lower()
    for marker in ("bearer ", "authorization", "secret", "password", "token", "api_key"):
        assert marker not in blob, f"mcp_config must not carry {marker!r}"
