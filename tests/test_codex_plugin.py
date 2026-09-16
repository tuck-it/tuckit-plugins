import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "codex"

def test_codex_plugin_manifest_valid_and_hookless():
    data = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    assert data["name"] == "tuckit"
    assert data["version"]                       # strict semver string
    assert data["description"]
    assert data["author"]["name"]
    assert data["interface"]["displayName"]
    assert data["interface"]["capabilities"] == ["Interactive", "Write"]
    assert data["interface"]["defaultPrompt"] == [
        "Set up this project with tuckit.",
        "What should we work on next?",
        "Design the next Slice with me.",
    ]
    assert data["skills"] == "./skills/"
    assert "hooks" not in data                   # Codex validator rejects a hooks field

def test_codex_hooks_file_uses_the_shape_codex_actually_parses():
    """Codex plugin hooks.json is the Claude Code shape: a top-level object whose
    only fields are `description` and `hooks`, with PascalCase event names inside
    `hooks`. The snake_case names Codex prints in its own errors ("unknown field
    `session_start`") are internal serde identifiers, not the file format.

    This file shipped for four weeks with the events at the top level in
    snake_case. Codex refused to parse it on every startup and skipped the hooks,
    while the test that was supposed to guard it asserted the broken shape.
    """
    data = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
    assert set(data) <= {"description", "hooks"}, "Codex rejects any other top-level field"
    assert "hooks" in data
    assert set(data["hooks"]) == {"SessionStart", "UserPromptSubmit"}
    for entries in data["hooks"].values():
        for entry in entries:                       # each is a matcher group
            for hook in entry["hooks"]:
                assert hook["type"] == "command"


def test_codex_hooks_invoke_emit_with_the_codex_agent():
    blob = json.dumps(json.loads((PLUGIN / "hooks" / "hooks.json").read_text()))
    assert "${PLUGIN_ROOT}/scripts/emit.py" in blob
    assert "--agent codex" in blob
    assert "--event start" in blob and "--content primer" in blob
    assert "--event prompt" in blob and "--content door" in blob
    # No Stop: Codex's Stop wire cannot inject context, so the write-back
    # reminder rides the primer instead. See test_codex_has_no_stop_payload.
    assert "--event stop" not in blob

def test_marketplace_lists_codex_plugin():
    data = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text())
    entry = next(p for p in data["plugins"] if p["name"] == "tuckit")
    assert entry["source"]["path"] == "./plugins/codex"
    assert entry["policy"]["installation"] == "AVAILABLE"
    assert entry["policy"]["authentication"] in ("ON_INSTALL", "ON_USE")
    assert entry["category"]

def test_codex_manifest_references_bundled_mcp():
    data = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    assert data["mcpServers"] == "./.mcp.json"


def test_codex_mcp_json_wires_token_from_env_not_hardcoded():
    """Bundling the MCP removes the manual config.toml step. The public repo must
    carry no token — Codex reads it from the named env var at connect time."""
    server = json.loads((PLUGIN / ".mcp.json").read_text())["mcpServers"]["tuckit"]
    assert server["type"] == "streamable_http"
    assert "://" in server["url"]                       # a real remote endpoint (public, not a secret)
    assert server["bearer_token_env_var"] == "TUCKIT_MCP_TOKEN"
    # No hardcoded credential anywhere in the server entry.
    blob = json.dumps(server)
    assert "Bearer " not in blob
    assert "http_headers" not in server                 # would risk a committed token


def test_codex_skill_points_at_plugin_root_content():
    text = (PLUGIN / "skills" / "tuckit-domain" / "SKILL.md").read_text()
    assert "${PLUGIN_ROOT}/content/domain.md" in text
    assert "get_project_state" in text
