#!/usr/bin/env python3
"""Emit tuckit domain-knowledge context in each agent's hook JSON envelope.

Standard library only. Invoked by per-agent hook configs; also importable for
tests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

# emit.py lives at <payload>/scripts/emit.py and reads <payload>/content/.
# This holds both in the authored `shared/` source and in every generated
# per-agent copy under plugins/<agent>/, so the resolution never changes.
PAYLOAD_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PAYLOAD_ROOT / "content"


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
    # No known id key present. A shared constant here (e.g. "no-session") would
    # make every id-less session collide on the same state-dir marker, so the
    # 2nd+ such session would find the marker already "used" and silently lose
    # the once-per-session write-back/primer behavior. Use the parent process
    # id instead: it's stable for the lifetime of this agent session (one
    # invoking process) but distinct across separate sessions/processes.
    return str(os.getppid())


def main(argv=None, stdin_text: str = "") -> int:
    parser = argparse.ArgumentParser(description="Emit tuckit hook context.")
    parser.add_argument("--agent", required=True, choices=AGENTS)
    parser.add_argument("--event", required=True, choices=("start", "stop"))
    parser.add_argument("--content", required=True, choices=("primer", "writeback"))
    args = parser.parse_args(argv)

    try:
        hook_input = json.loads(stdin_text) if stdin_text.strip() else {}
    except json.JSONDecodeError:
        hook_input = {}
    session_id = extract_session_id(hook_input)
    text = load_content(args.content)

    if args.event == "start":
        # Antigravity has no SessionStart; PreInvocation fires every turn, so
        # inject the primer only on the first invocation of this session.
        if args.agent == "antigravity" and not first_time(session_id, "primer"):
            print(json.dumps({}))
            return 0
        print(json.dumps(build_start_payload(text, args.agent)))
        return 0

    # event == "stop": remind exactly once per session, then allow stopping.
    if first_time(session_id, "writeback"):
        print(json.dumps(build_stop_payload(text, args.agent)))
    else:
        print(json.dumps(allow_stop_payload(args.agent)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], stdin_text=sys.stdin.read()))
