import shutil
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


@pytest.mark.parametrize("agent", AGENTS)
def test_every_authored_skill_is_fanned_out(agent):
    """Guard: build.py must fan out ALL skills, not one hardcoded name."""
    authored = {p.name for p in (SHARED / "skills").iterdir() if p.is_dir()}
    assert len(authored) > 1, "this guard is vacuous with a single authored skill"
    built = {p.name for p in (ROOT / "plugins" / agent / "skills").iterdir() if p.is_dir()}
    assert built == authored, f"plugins/{agent}/skills out of sync — run build"
    for name in authored:
        text = (ROOT / "plugins" / agent / "skills" / name / "SKILL.md").read_text()
        assert "{{ROOT}}" not in text, f"unrendered placeholder in {name} — run build"


SKILLS = sorted(p.name for p in (SHARED / "skills").iterdir() if p.is_dir())


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("skill", SKILLS)
def test_every_shared_skill_file_is_generated(agent, skill):
    """Whole skill trees ship, not just SKILL.md — a skill may carry a reference
    doc or a page template, and one left behind fails at runtime with no
    build-time signal."""
    src_dir = SHARED / "skills" / skill
    dst_dir = ROOT / "plugins" / agent / "skills" / skill
    src_files = sorted(p.relative_to(src_dir) for p in src_dir.rglob("*") if p.is_file())
    dst_files = sorted(p.relative_to(dst_dir) for p in dst_dir.rglob("*") if p.is_file())
    assert dst_files == src_files, f"plugins/{agent}/skills/{skill} drifted — run build"

    for rel in src_files:
        rendered = (dst_dir / rel).read_bytes()
        if rel.suffix in build.TEXT_SUFFIXES:
            expected = (src_dir / rel).read_text(encoding="utf-8").replace(
                "{{ROOT}}", build.AGENT_ROOT_TOKENS[agent]
            )
            assert rendered.decode("utf-8") == expected, f"{rel} drifted — run build"
        else:
            assert rendered == (src_dir / rel).read_bytes(), f"{rel} drifted — run build"


def _authored_skill(root: Path):
    """A source skill that is more than one flat markdown file."""
    src = root / "skills" / "demo"
    (src / "refs").mkdir(parents=True)
    (src / "SKILL.md").write_text("root is {{ROOT}}\n", encoding="utf-8")
    (src / "refs" / "guide.md").write_text("see {{ROOT}}/content\n", encoding="utf-8")
    (src / "logo.png").write_bytes(b"\x89PNG\x00\xff\xfe")
    return src


def test_mirror_skills_ships_the_whole_tree(tmp_path, monkeypatch):
    """The repo's skills are single-file today, so the parametrized guards above
    cannot show that a second file would survive. This does."""
    _authored_skill(tmp_path)
    monkeypatch.setattr(build, "SHARED", tmp_path)
    dst = tmp_path / "out"

    build._mirror_skills(dst, "TOKEN")

    assert (dst / "demo" / "SKILL.md").read_text() == "root is TOKEN\n"
    # nested, and the token is substituted there too
    assert (dst / "demo" / "refs" / "guide.md").read_text() == "see TOKEN/content\n"
    # binary is copied, never decoded
    assert (dst / "demo" / "logo.png").read_bytes() == b"\x89PNG\x00\xff\xfe"


def test_mirror_skills_removes_what_the_source_deleted(tmp_path, monkeypatch):
    src = _authored_skill(tmp_path)
    monkeypatch.setattr(build, "SHARED", tmp_path)
    dst = tmp_path / "out"
    build._mirror_skills(dst, "TOKEN")

    (src / "refs" / "guide.md").unlink()
    (tmp_path / "skills" / "gone").mkdir()
    (tmp_path / "skills" / "gone" / "SKILL.md").write_text("x", encoding="utf-8")
    build._mirror_skills(dst, "TOKEN")
    shutil.rmtree(tmp_path / "skills" / "gone")
    build._mirror_skills(dst, "TOKEN")

    assert not (dst / "demo" / "refs" / "guide.md").exists(), "deleted file survived in the payload"
    assert not (dst / "gone").exists(), "deleted skill survived in the payload"
    assert (dst / "demo" / "SKILL.md").exists()


def test_build_is_idempotent():
    assert build.build() == build.build()
