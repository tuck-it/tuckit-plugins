#!/usr/bin/env python3
"""Generate each agent's self-contained plugin payload from the single source.

`shared/` is the authored source and mirrors a deployed payload's shape
(`content/`, `scripts/emit.py`, `skills/`). Each agent installs a self-contained
copy, so `build.py` fans the source out into `plugins/<agent>/`, substituting the
per-agent path token in the skill. Run it after editing anything under `shared/`.

Only the GENERATED subset is written (content, scripts/emit.py, skills). The
per-agent static files — manifests, hooks, commands, the AGENTS snippet — are
authored in place under plugins/<agent>/ and left untouched.
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED = REPO_ROOT / "shared"
PLUGINS = REPO_ROOT / "plugins"

# The path token each agent substitutes for `{{ROOT}}` in the skill body — i.e.
# where that agent finds this payload's `content/` at runtime.
AGENT_ROOT_TOKENS = {
    "claude": "${CLAUDE_PLUGIN_ROOT}",
    "codex": "${PLUGIN_ROOT}",
    # Antigravity has no plugin-root variable to expand, so the skill has to
    # name where `agy plugin install` puts a plugin: a literal path, under the
    # manifest's `name`. A skill body is read by the agent rather than by agy,
    # so a token agy alone understands would not help here anyway.
    "antigravity": "~/.gemini/config/plugins/tuckit",
}

# Formats the `{{ROOT}}` substitution may touch. Anything else is copied as
# bytes — a skill is free to ship images or fonts without them being decoded.
TEXT_SUFFIXES = {".md", ".html", ".css", ".js", ".json", ".py", ".txt", ".toml"}


def _mirror_files(src: Path, dst: Path) -> list:
    """Mirror files under src into dst, deleting stale files. Returns writes."""
    written = []
    dst.mkdir(parents=True, exist_ok=True)
    keep = {p.name for p in src.iterdir() if p.is_file()}
    for stale in dst.iterdir():
        if stale.is_file() and stale.name not in keep:
            stale.unlink()
    for f in sorted(src.iterdir()):
        if f.is_file():
            target = dst / f.name
            shutil.copyfile(f, target)
            shutil.copymode(f, target)
            written.append(target)
    return written


def _mirror_skills(dst_root: Path, token: str) -> list:
    """Render every shared/skills/<name>/ tree into dst_root, whole directory.

    A skill is more than its SKILL.md — it may carry a reference doc, a page
    template, or scripts — so the whole tree is mirrored rather than one known
    file. Each skill directory is rebuilt from scratch so a file deleted from
    the source cannot survive in a generated payload.

    `{{ROOT}}` is substituted only in text formats; binary assets are copied
    byte-for-byte so an image or font is never corrupted by a decode.

    File modes are carried over on both paths, because neither `write_text` nor
    `copyfile` does it: a skill may ship an executable helper, and a payload
    that silently lost `+x` fails at the user's install rather than here.
    """
    written = []
    src_root = SHARED / "skills"
    keep = {p.name for p in src_root.iterdir() if p.is_dir()}
    if dst_root.exists():
        for stale in dst_root.iterdir():
            if stale.is_dir() and stale.name not in keep:
                shutil.rmtree(stale)

    for skill_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        dst = dst_root / skill_dir.name
        if dst.exists():
            shutil.rmtree(dst)
        for src in sorted(skill_dir.rglob("*")):
            if not src.is_file():
                continue
            target = dst / src.relative_to(skill_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix in TEXT_SUFFIXES:
                target.write_text(
                    src.read_text(encoding="utf-8").replace("{{ROOT}}", token),
                    encoding="utf-8",
                )
            else:
                shutil.copyfile(src, target)
            shutil.copymode(src, target)
            written.append(target)
    return written


def build_agent(agent: str) -> list:
    """Generate plugins/<agent>/{content,scripts,skills}. Returns repo-rel paths."""
    token = AGENT_ROOT_TOKENS[agent]
    dst = PLUGINS / agent
    written = []

    written += _mirror_files(SHARED / "content", dst / "content")

    emit_src = SHARED / "scripts" / "emit.py"
    emit_dst = dst / "scripts" / "emit.py"
    emit_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(emit_src, emit_dst)
    shutil.copymode(emit_src, emit_dst)
    written.append(emit_dst)

    written += _mirror_skills(dst / "skills", token)

    return [str(p.relative_to(REPO_ROOT)) for p in written]


def build() -> list:
    written = []
    for agent in AGENT_ROOT_TOKENS:
        written += build_agent(agent)
    return written


if __name__ == "__main__":
    for path in build():
        print(f"built {path}")
