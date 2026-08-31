"""Guard: a ref shown to a human carries its title.

A ref is an address, not a meaning. When a skill's example message names a
slice as a bare `TP-355`, the reader has to open the board to answer -- so they
answer without reading, and the approval is real while the understanding is
not. The skills taught exactly that: filing-the-inbox showed `TP-355 -> oss` as
the message to send.

Only quoted example messages are checked. A ref inside backticks or a fence is
an argument, a path or a commit subject, and a title there would be wrong.
"""
import re
from pathlib import Path

SHARED = Path(__file__).resolve().parent.parent / "shared"

REF = re.compile(r"\b[A-Z]{2,5}-\d+\b")
INLINE_CODE = re.compile(r"`[^`]*`")
# A title follows immediately: optional spaces, then an opening quote.
TITLE_AFTER = re.compile(r'^\s*["“‘\']')


def _strip_fences(text: str) -> str:
    out, inside = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return "\n".join(out)


def _quoted_blocks(text: str):
    """Yield (first_line_no, block_text) per run of consecutive '>' lines.

    Blocks, not lines: the counter-example this guard exists for spans four
    consecutive quoted lines, and a line-at-a-time reader sees only the first.
    """
    block, start = [], None
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(">"):
            if start is None:
                start = i
            block.append(line.lstrip().lstrip(">"))
        elif block:
            yield start, "\n".join(block)
            block, start = [], None
    if block:
        yield start, "\n".join(block)


def bare_refs(text: str):
    """Refs in example messages that reach a human without a title."""
    found = []
    for line_no, block in _quoted_blocks(_strip_fences(text)):
        prose = INLINE_CODE.sub(" ", block)
        for m in REF.finditer(prose):
            if not TITLE_AFTER.match(prose[m.end():]):
                found.append((line_no, m.group()))
    return found


def test_example_messages_name_the_slice_they_ask_about():
    offenders = []
    for md in sorted(SHARED.rglob("*.md")):
        for line_no, ref in bare_refs(md.read_text(encoding="utf-8")):
            offenders.append(f"{md.relative_to(SHARED)}:~{line_no} {ref}")
    assert offenders == [], (
        "these example messages show a bare ref to a human; give it its title "
        f"so they can answer without opening the board: {offenders}"
    )


def test_a_ref_in_code_is_left_alone():
    """A tool argument, a path and a commit subject all take a bare ref."""
    assert bare_refs("> Read `get_slice(TP-42)` first.") == []
    assert bare_refs("```\n[Scratch: .tuckit/work/TP-42/]\n```") == []


def test_a_titled_ref_passes_and_a_bare_one_does_not():
    assert bare_refs('> File: TP-355 "Retry duplicates the note" -> oss') == []
    assert [r for _, r in bare_refs("> File: TP-355 -> oss")] == ["TP-355"]
