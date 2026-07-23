import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
AGENTS = list(build.AGENT_ROOT_TOKENS)


@pytest.mark.parametrize("agent", AGENTS)
def test_generated_content_matches_shared(agent):
    src = sorted((SHARED / "content").glob("*.md"))
    assert src, "no source content files found"
    for md in src:
        copy = ROOT / "plugins" / agent / "content" / md.name
        assert copy.is_file(), f"missing {copy} — run scripts/build.py"
        assert copy.read_bytes() == md.read_bytes(), \
            f"{copy} drifted from shared — run python3 scripts/build.py"


@pytest.mark.parametrize("agent", AGENTS)
def test_no_stale_content_files(agent):
    src_names = {p.name for p in (SHARED / "content").glob("*.md")}
    copy_names = {p.name for p in (ROOT / "plugins" / agent / "content").glob("*.md")}
    assert copy_names == src_names, f"stale files in plugins/{agent}/content — re-run build"


@pytest.mark.parametrize("agent", AGENTS)
def test_generated_emit_matches_shared(agent):
    src = (SHARED / "scripts" / "emit.py").read_bytes()
    copy = ROOT / "plugins" / agent / "scripts" / "emit.py"
    assert copy.is_file(), f"missing {copy} — run scripts/build.py"
    assert copy.read_bytes() == src, f"plugins/{agent}/scripts/emit.py drifted — run build"


@pytest.mark.parametrize("agent", AGENTS)
def test_skill_has_agent_token_and_no_placeholder(agent):
    text = (ROOT / "plugins" / agent / "skills" / "tuckit-domain" / "SKILL.md").read_text()
    assert "{{ROOT}}" not in text, "unrendered placeholder — run build"
    assert f"{build.AGENT_ROOT_TOKENS[agent]}/content/domain.md" in text
    assert "get_project_state" in text


def test_build_is_idempotent():
    assert build.build() == build.build()
