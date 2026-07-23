import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import sync_codex_plugin as sync  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "tuckit"

def test_codex_plugin_content_matches_source():
    src = sorted((ROOT / "content").glob("*.md"))
    assert src, "no source content files found"
    for md in src:
        copy = PLUGIN / "content" / md.name
        assert copy.is_file(), f"missing synced copy {copy} — run scripts/sync_codex_plugin.py"
        assert copy.read_bytes() == md.read_bytes(), \
            f"{copy} drifted from source — run python3 scripts/sync_codex_plugin.py"

def test_codex_plugin_has_no_extra_content_files():
    src_names = {p.name for p in (ROOT / "content").glob("*.md")}
    copy_names = {p.name for p in (PLUGIN / "content").glob("*.md")}
    assert copy_names == src_names, "stale files in plugins/tuckit/content — re-run the sync"

def test_codex_plugin_emit_matches_source():
    src = (ROOT / "scripts" / "emit.py").read_bytes()
    copy = PLUGIN / "scripts" / "emit.py"
    assert copy.is_file(), "missing synced emit.py — run scripts/sync_codex_plugin.py"
    assert copy.read_bytes() == src, "plugins/tuckit/scripts/emit.py drifted — run scripts/sync_codex_plugin.py"

def test_sync_is_idempotent():
    assert sync.sync() == sync.sync()
