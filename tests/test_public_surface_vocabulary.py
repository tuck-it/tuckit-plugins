"""The public surface must not describe a model the product no longer has.

This repository is the only public one, and four files in it are read by
someone deciding whether to install: the README, the MCP registry submission,
and the three marketplace manifests. Nothing checked their vocabulary, so when
TP-343 deleted the step layer the word survived in `server.json`
("Areas, slices and bites over MCP") and in all three plugin descriptions
("design->steps->execute->review->ship") for months. check_drift.py looks at
MCP tool NAMES in shared content and never looked here.

A dead noun on this surface is worse than a stale doc: it is the first
sentence a sceptical developer reads, and it describes an object they will
never find.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Nouns the product removed. Each is a real object that existed and does not
# any more, so no public sentence may name one.
#
# - bite (TP-343): the step layer. Nobody read a bite body, and counting them
#   let a slice reach ready_to_ship with nobody having said what done meant.
#   Replaced by done_when and recorded evidence.
# - ticket (TP-227 / the two-layer model): promote_ticket was the last
#   irreversible operation in the product.
# - plan: a slice's own spec and constraints hold what a plan used to. This
#   one is unenforced English, not a pattern: "a plan that nobody reads is a
#   third copy of the spec" is a true sentence about why the object is gone.
# - org (TP-338): renamed to workspace everywhere.
# - the area-less slice: a Slice always lives in an Area (area is required to
#   create one), and the Inbox holds Captures instead -- an unjudged title and
#   prose, promoted into an Area keeping its number, or dismissed, both
#   reversible. One verb for both "I noticed something" and "this is work" got
#   picked wrong constantly: 10 of the 16 things in one production Inbox had a
#   full spec written into them, so the board reported unjudged notes at stage
#   needs_done_when. "An Inbox slice" names what that fix removed. The regex is
#   short-range on purpose: "there is no Area for that first slice to live
#   under" is a true sentence about creating an Area first and must not fail.
DEAD_NOUNS = {
    "bite": r"\bbites?\b",
    "ticket": r"\btickets?\b",
    "promote_ticket": r"\bpromote_ticket\b",
    "the area-less slice": (r"\binbox\s+slices?\b"
                            r"|\bslices?\b[^.\n]{0,20}\bno area\b"
                            r"|\bareas?-?less\s+slices?\b"
                            r"|\bslices?\s+without\s+an?\s+area\b"),
    # The layer, not the English word: "there is no step layer" is a true
    # sentence the README is allowed to keep, while an arrow chain through
    # ->steps-> is the old workflow being advertised.
    "the step layer": r"->\s*steps\s*->",
    "org": r"\borgs?\b",
}


def _public_texts():
    """Every file a visitor reads, with the name to blame in a failure."""
    out = {}
    for rel in ("README.md", "NOTICE", "server.json"):
        p = ROOT / rel
        if p.is_file():
            out[rel] = p.read_text(encoding="utf-8")
    for p in sorted((ROOT / "docs").rglob("*.md")):
        out[str(p.relative_to(ROOT))] = p.read_text(encoding="utf-8")
    return out


def _manifest_descriptions():
    """Only the description field: a manifest's other keys are machinery, and
    the description is the sentence a marketplace renders."""
    out = {}
    for rel in ("plugins/antigravity/plugin.json",
                "plugins/claude/.claude-plugin/plugin.json",
                "plugins/codex/.codex-plugin/plugin.json"):
        p = ROOT / rel
        if p.is_file():
            out[rel] = json.loads(p.read_text(encoding="utf-8")).get("description", "")
    out["server.json"] = json.loads(
        (ROOT / "server.json").read_text(encoding="utf-8")).get("description", "")
    return out


def test_no_marketplace_description_names_a_dead_noun():
    for rel, text in _manifest_descriptions().items():
        for noun, pattern in DEAD_NOUNS.items():
            assert not re.search(pattern, text, re.I), \
                f"{rel} description still says {noun!r}: {text!r}"


def test_no_public_file_names_a_dead_noun():
    for rel, text in _public_texts().items():
        for noun, pattern in DEAD_NOUNS.items():
            hit = re.search(pattern, text, re.I)
            if hit:
                line = text[:hit.start()].count("\n") + 1
                raise AssertionError(f"{rel}:{line} still says {noun!r}")


def test_the_registry_version_tracks_the_claude_plugin():
    """docs/listing.md: "Keep `version` in step with the Claude plugin's
    plugin.json." It had drifted five minor versions behind, which is what a
    written rule with no check does."""
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    claude = json.loads(
        (ROOT / "plugins/claude/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert server["version"] == claude["version"], (
        f"server.json is {server['version']} and the Claude plugin is "
        f"{claude['version']}; docs/listing.md says they move together"
    )
