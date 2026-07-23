#!/usr/bin/env python3
"""Sync authored content + emitter into the self-contained Codex plugin.

The repo root is the authored single source; `plugins/tuckit/content/` and
`plugins/tuckit/scripts/emit.py` are GENERATED copies (Codex bundles only that
subtree, so it needs its own copy). Run this after editing the authored source.
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_CONTENT = REPO_ROOT / "content"
SRC_EMIT = REPO_ROOT / "scripts" / "emit.py"
DST = REPO_ROOT / "plugins" / "tuckit"


def sync() -> list:
    """Copy authored source into plugins/tuckit/. Returns repo-relative paths written."""
    written = []
    dst_content = DST / "content"
    dst_content.mkdir(parents=True, exist_ok=True)
    # Remove stale copies so a deleted source file cannot linger.
    for stale in dst_content.glob("*.md"):
        if not (SRC_CONTENT / stale.name).exists():
            stale.unlink()
    for md in sorted(SRC_CONTENT.glob("*.md")):
        target = dst_content / md.name
        shutil.copyfile(md, target)
        written.append(str(target.relative_to(REPO_ROOT)))
    dst_emit = DST / "scripts" / "emit.py"
    dst_emit.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC_EMIT, dst_emit)
    written.append(str(dst_emit.relative_to(REPO_ROOT)))
    return written


if __name__ == "__main__":
    for path in sync():
        print(f"synced {path}")
