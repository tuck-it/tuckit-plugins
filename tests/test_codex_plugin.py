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
    assert data["skills"] == "./skills/"
    assert "hooks" not in data                   # Codex validator rejects a hooks field

def test_codex_plugin_hooks_snake_case_events_invoke_emit():
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
    assert "session_start" in hooks and "stop" in hooks
    blob = json.dumps(hooks)
    assert "${PLUGIN_ROOT}/scripts/emit.py" in blob
    assert "--agent codex" in blob
    assert "--event start" in blob and "--content primer" in blob
    assert "--event stop" in blob and "--content writeback" in blob

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
