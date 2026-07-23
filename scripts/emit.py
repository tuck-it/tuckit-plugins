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


AGENTS = ("claude-code", "codex", "antigravity")


def build_start_payload(text: str, agent: str) -> dict:
    if agent == "claude-code":
        return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                       "additionalContext": text}}
    if agent == "codex":
        return {"additional_contexts": [text]}
    if agent == "antigravity":
        return {"injectSteps": [{"ephemeralMessage": text}]}
    raise ValueError(f"unknown agent: {agent}")


def build_stop_payload(text: str, agent: str) -> dict:
    if agent == "claude-code":
        return {"decision": "block", "reason": text}
    if agent == "codex":
        return {"continue": True, "systemMessage": text}
    if agent == "antigravity":
        return {"decision": "continue", "reason": text}
    raise ValueError(f"unknown agent: {agent}")


def allow_stop_payload(agent: str) -> dict:
    return {}


def extract_session_id(hook_input: dict) -> str:
    for key in ("session_id", "sessionId", "conversationId", "conversation_id", "id"):
        value = hook_input.get(key)
        if value:
            return str(value)
    return "no-session"
