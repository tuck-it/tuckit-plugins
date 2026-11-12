"""Which tuckit workspace a repository writes to, read from its `.tuckit` file.

One machine runs agent sessions in several repositories at once, each on its
own board. The repository names its board in a `.tuckit` file at its root:

    workspace = "<slug>"

and the plugin sends that slug to the server as the `X-Tuckit-Workspace`
header on every MCP request. The model never carries it, so an agent cannot
land on the wrong board by copying the wrong slug.

The header is produced by a helper command each agent runs when it connects.
Neither agent can point that command at a file inside the plugin (Codex
substitutes no plugin-root variable into MCP config, measured on codex-cli
0.166.0), so the helper is the one line in `HELPER_SOURCE`, inlined into both
manifests verbatim. `lookup()` below is the same rule in readable form, used
by the primer; tests run both over the same fixtures and require them to agree.

A `.tuckit` that exists but cannot be read is not treated as absent. Absent
means "no header", which for a person with one workspace silently picks it --
so a broken file would go unnoticed. Instead the helper sends a value that is
not a slug and names the file, and the server refuses it.

Standard library only.
"""
from __future__ import annotations

import re
from pathlib import Path

FILENAME = ".tuckit"
HEADER = "X-Tuckit-Workspace"
UNREADABLE = "!unreadable "

# The slug shape tuckit's workspace URLs use.
_LINE = re.compile(r'^\s*workspace\s*=\s*"([a-z0-9][a-z0-9-]{0,99})"[ \t]*(?:\r?\n|\Z)', re.M)

# The helper, as the one line both manifests carry inside `python3 -c "..."`.
# Written to survive two layers it is pasted into: a JSON string, and a shell
# double-quoted argument. So it holds no double quote (\x22 instead), no `$`
# (end of line is matched as a newline or \Z),
# no backtick, and no doubled backslash. Claude Code passes the project folder
# as argv[1] (its helper runs in the plugin folder); Codex passes nothing and
# runs it in the session folder.
HELPER_SOURCE = (
    "import json,pathlib,re,sys;"
    "d=pathlib.Path(sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else '.').resolve();"
    "f=next((p/'.tuckit' for p in [d,*d.parents] if (p/'.tuckit').is_file()),None);"
    "m=f and re.search(r'^\\s*workspace\\s*=\\s*\\x22([a-z0-9][a-z0-9-]{0,99})\\x22[ \\t]*(?:\\r?\\n|\\Z)',"
    "f.read_text(errors='replace'),re.M);"
    "print(json.dumps({} if f is None else {'X-Tuckit-Workspace':m.group(1) if m else "
    "'!unreadable '+str(f).encode('ascii','backslashreplace').decode()}))"
)


def helper_command(*, project_dir_arg: str = "") -> str:
    """The exact string a manifest carries. `project_dir_arg` is appended as
    the script's argv[1] -- Claude Code's `"${CLAUDE_PROJECT_DIR}"`."""
    command = f'python3 -c "{HELPER_SOURCE}"'
    return f"{command} {project_dir_arg}" if project_dir_arg else command


def find_file(start: Path) -> Path | None:
    start = start.resolve()
    for folder in (start, *start.parents):
        candidate = folder / FILENAME
        if candidate.is_file():
            return candidate
    return None


def lookup(start: Path) -> tuple[str | None, Path | None]:
    """(slug, file) for the repository containing `start`.

    (None, None)  -- no `.tuckit` anywhere above `start`.
    (None, file)  -- a `.tuckit` that does not name a workspace.
    (slug, file)  -- the board this repository writes to.
    """
    found = find_file(start)
    if found is None:
        return None, None
    match = _LINE.search(found.read_text(errors="replace"))
    return (match.group(1) if match else None), found


def header(start: Path) -> dict:
    """What the helper prints for `start`, computed the readable way."""
    slug, found = lookup(start)
    if found is None:
        return {}
    if slug is None:
        return {HEADER: UNREADABLE + str(found).encode("ascii", "backslashreplace").decode()}
    return {HEADER: slug}


def describe(start: Path) -> str:
    """One paragraph for the primer: which board this session is on, and from
    where -- or what to do when the repository names none."""
    slug, found = lookup(start)
    if found is not None and slug is not None:
        return (
            f"This session writes to the tuckit workspace `{slug}`, named by "
            f"`{found}`. If that is the wrong board, fix the file and start a "
            "new session; the connection reads it once, when it opens."
        )
    if found is not None:
        return (
            f"`{found}` exists but does not name a workspace, so tuckit will "
            "refuse every call from this session until it does. It needs one "
            'line: workspace = "<slug>". Ask your human partner which board '
            "this repository belongs to."
        )
    return (
        f"No `{FILENAME}` file was found from `{start}` upward, so this "
        "repository does not say which tuckit workspace it belongs to. If the "
        "account has more than one workspace, tuckit refuses calls until it "
        f"does: ask your human partner which board, then create `{FILENAME}` "
        'at the repository root containing workspace = "<slug>".'
    )
