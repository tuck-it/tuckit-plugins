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
        # Codex's SessionStart hook takes the same wire as Claude Code's, down
        # to the camelCase keys. The snake_case names in Codex's own docs and
        # error messages ("unknown field `session_start`") are its internal
        # serde identifiers, not the JSON a hook writes or reads.
        return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                       "additionalContext": text}}
    if agent == "antigravity":
        # agy has no start event that can inject context that lasts. Its
        # `PreInvocation` carries only an `ephemeralMessage` — a transient
        # system step the model stops seeing almost immediately — so the
        # orientation ships as `rules/AGENTS.md`, which agy loads for as long
        # as the plugin is enabled. Nothing should call this.
        raise ValueError("antigravity is oriented by rules/AGENTS.md, not a start hook")
    raise ValueError(f"unknown agent: {agent}")


def build_prompt_payload(text: str, agent: str) -> dict:
    """The door, injected as each request arrives.

    SessionStart lands once, at position zero of a conversation that may run
    for hours; by the thirtieth turn it is competing with a direct instruction
    from three lines ago and losing. This is the only event that fires at the
    moment work is actually asked for, which is the moment the board gets
    skipped.
    """
    if agent in ("claude-code", "codex"):
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                       "additionalContext": text}}
    if agent == "antigravity":
        # agy's pre-turn event carries only an `ephemeralMessage`. A one-turn
        # lifetime would actually suit a per-prompt reminder -- but the schema
        # is unverified here, and a hook agy accepts and ignores reports
        # nothing, so the door ships in rules/AGENTS.md, which is always
        # loaded, rather than in a hook that may quietly do nothing.
        raise ValueError("antigravity carries the door in rules/AGENTS.md, not a hook")
    raise ValueError(f"unknown agent: {agent}")


def build_stop_payload(text: str, agent: str) -> dict:
    if agent == "claude-code":
        # `decision: "block"` would also keep the turn going, but Claude Code
        # routes it through its blocking-error path and renders the reminder
        # under a red "Stop hook error:" label — it reads like the hook failed.
        # A Stop hook's additionalContext injects the text AND sets the
        # continue-the-conversation flag on its own, with no error framing.
        return {"hookSpecificOutput": {"hookEventName": "Stop",
                                       "additionalContext": text}}
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
    parser.add_argument("--event", required=True, choices=("start", "prompt", "stop"))
    parser.add_argument("--content", required=True,
                        choices=("primer", "door", "writeback"))
    args = parser.parse_args(argv)

    try:
        hook_input = json.loads(stdin_text) if stdin_text.strip() else {}
    except json.JSONDecodeError:
        hook_input = {}
    session_id = extract_session_id(hook_input)

    if args.event == "start":
        # SessionStart fires on every source: startup, resume, clear AND
        # compact. Ungated, a long session gets the whole primer pushed back
        # into the context compaction has just freed. Gate on the session id,
        # not on a source matcher in hooks.json: a mistyped matcher string
        # matches no source at all, so the primer would never be injected and
        # nothing would say so. first_time fails the other way -- its worst
        # case is one extra injection, which is the behaviour it replaces.
        # This is inside the start branch, so it covers claude-code and codex
        # alike; antigravity is oriented by rules/AGENTS.md and never gets here.
        if not first_time(session_id, "primer"):
            # Same empty envelope the stop path prints when it has already
            # reminded. Nothing is loaded, because nothing is emitted.
            print(json.dumps({}))
            return 0
        print(json.dumps(build_start_payload(load_content(args.content), args.agent)))
        return 0

    text = load_content(args.content)

    if args.event == "prompt":
        # Every prompt, deliberately. Once per session is what SessionStart
        # already does, and a reminder that fired once is the state this was
        # written to fix.
        print(json.dumps(build_prompt_payload(text, args.agent)))
        return 0

    # event == "stop": remind exactly once per session, then allow stopping.
    if first_time(session_id, "writeback"):
        print(json.dumps(build_stop_payload(text, args.agent)))
    else:
        print(json.dumps(allow_stop_payload(args.agent)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], stdin_text=sys.stdin.read()))
