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
    "antigravity": "__REPO__/plugins/antigravity",
}


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
            written.append(target)
    return written


def build_agent(agent: str) -> list:
    """Generate plugins/<agent>/{content,scripts,skills}. Returns repo-rel paths."""
    token = AGENT_ROOT_TOKENS[agent]
    dst = PLUGINS / agent
    written = []

    written += _mirror_files(SHARED / "content", dst / "content")

    emit_dst = dst / "scripts" / "emit.py"
    emit_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SHARED / "scripts" / "emit.py", emit_dst)
    written.append(emit_dst)

    skills_src = SHARED / "skills"
    skills_dst = dst / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)
    authored = {p.name for p in skills_src.iterdir() if p.is_dir()}
    for stale in skills_dst.iterdir():
        if stale.is_dir() and stale.name not in authored:
            shutil.rmtree(stale)
    for skill_src in sorted(p for p in skills_src.iterdir() if p.is_dir()):
        skill_dst = skills_dst / skill_src.name / "SKILL.md"
        skill_dst.parent.mkdir(parents=True, exist_ok=True)
        skill_dst.write_text(
            (skill_src / "SKILL.md").read_text(encoding="utf-8").replace("{{ROOT}}", token),
            encoding="utf-8",
        )
        written.append(skill_dst)

    return [str(p.relative_to(REPO_ROOT)) for p in written]


def build() -> list:
    written = []
    for agent in AGENT_ROOT_TOKENS:
        written += build_agent(agent)
    return written


if __name__ == "__main__":
    for path in build():
        print(f"built {path}")
