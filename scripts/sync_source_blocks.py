#!/usr/bin/env python3
"""Splice repo source files into the pages under claude/ verbatim.

Those pages explain a file and then reproduce it in full. A copy of a file
inside another file goes stale the moment someone edits the original, so the
copies are generated rather than pasted.

A page marks where a copy goes with a repo-relative path:

    <!--SRC:.claude/commands/wiki-ship.md-->

The marker, and anything previously emitted after it up to <!--/SRC-->, is
replaced with an escaped .cmd block holding the file verbatim. Re-running
refreshes every block, so a page cannot drift from the file it documents.

    python3 scripts/sync_source_blocks.py            # rewrite the pages
    python3 scripts/sync_source_blocks.py --check    # report only, exit 1 if stale

Only files inside the repo can be synced: a clone has to be able to run this.
Anything outside it (the machine's Claude config, for example) is a snapshot
hand-written into the page and labelled as one.

Pure stdlib, same as build_index.py.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE_DIR = ROOT / "claude"
CMD_DIR = ROOT / ".claude" / "commands"

MARKER = re.compile(
    r"<!--SRC:(?P<path>[^>\s]+?)-->(?:.*?<!--/SRC-->)?",
    re.DOTALL,
)

# the indentation the surrounding step bodies use
INDENT = " " * 8

# panel header label per extension, since these are not shell snippets
LANGS = {".md": "markdown", ".py": "python", ".json": "json", ".sh": "bash"}


def block(rel: str, source: str) -> str:
    """Build the .cmd panel holding one file verbatim."""
    body = html.escape(source.rstrip("\n"), quote=False)
    name = Path(rel).name
    lang = LANGS.get(Path(rel).suffix, "text")
    return (
        f"<!--SRC:{rel}-->\n"
        f'{INDENT}<div class="cmd" data-lang="{name}" data-src-lang="{lang}">{body}</div>\n'
        f"{INDENT}<!--/SRC-->"
    )


def render(page: str) -> tuple[str, list[str], list[str]]:
    """Return the page with every marker filled, plus what was found."""
    filled: list[str] = []
    problems: list[str] = []

    def sub(m: re.Match) -> str:
        rel = m.group("path")
        src = (ROOT / rel).resolve()
        # never reach outside the repo: a clone must be able to run this
        if not src.is_relative_to(ROOT):
            problems.append(f"{rel} resolves outside the repo")
            return m.group(0)
        if not src.exists():
            problems.append(f"{rel} does not exist")
            return m.group(0)
        filled.append(rel)
        return block(rel, src.read_text(encoding="utf-8"))

    return MARKER.sub(sub, page), filled, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="report whether the pages are current without writing to them",
    )
    args = ap.parse_args()

    pages = sorted(PAGE_DIR.glob("*.html"))
    if not pages:
        print(f"error: no pages found in {PAGE_DIR.relative_to(ROOT)}/", file=sys.stderr)
        return 1

    stale: list[Path] = []
    all_filled: list[str] = []
    all_problems: list[str] = []

    for page_path in pages:
        page = page_path.read_text(encoding="utf-8")
        out, filled, problems = render(page)
        all_filled.extend(filled)
        all_problems.extend(problems)

        if out == page:
            continue
        stale.append(page_path)
        if not args.check:
            page_path.write_text(out, encoding="utf-8")

    for problem in all_problems:
        print(f"warning: {problem}")

    # a command with no marker anywhere is a command nobody documented
    on_disk = {f".claude/commands/{p.name}" for p in CMD_DIR.glob("*.md")}
    undocumented = sorted(on_disk - set(all_filled))
    if undocumented:
        print("warning: command files not reproduced on any page:")
        for rel in undocumented:
            print(f"                {rel}")

    bad = bool(all_problems or undocumented)

    if args.check:
        if stale:
            print("STALE: these pages no longer match their source files:")
            for p in stale:
                print(f"                {p.relative_to(ROOT)}")
            print("   Run: python3 scripts/sync_source_blocks.py")
            return 1
        print(f"Current: {len(all_filled)} source blocks match their files.")
        return 1 if bad else 0

    if not stale:
        print(f"No change: {len(all_filled)} source blocks already current.")
        return 1 if bad else 0

    print(f"Spliced {len(all_filled)} source blocks across {len(stale)} page(s):")
    for rel in all_filled:
        lines = (ROOT / rel).read_text(encoding="utf-8").count("\n")
        print(f"                {rel} ({lines} lines)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
