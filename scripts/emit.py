#!/usr/bin/env python3
"""Emit tuckit domain-knowledge context in each agent's hook JSON envelope.

Standard library only. Invoked by per-agent hook configs; also importable for
tests.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"


def load_content(name: str) -> str:
    return (CONTENT_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


def state_dir() -> Path:
    env = os.environ.get("TUCKIT_PLUGIN_STATE_DIR")
    if env:
        return Path(env)
    return Path(tempfile.gettempdir()) / "tuckit-plugin"


def first_time(session_id: str, tag: str, base: "Path | None" = None) -> bool:
    """True (and records) the first time we see (session_id, tag); False after."""
    base = base or state_dir()
    marker = base / f"{session_id}.{tag}"
    if marker.exists():
        return False
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("1", encoding="utf-8")
    return True
