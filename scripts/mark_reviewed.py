#!/usr/bin/env python3
"""Stamp a runbook as reviewed today, then regenerate the index.

    python3 scripts/mark_reviewed.py aix/lvm/aix_lvm_basics.html
    python3 scripts/mark_reviewed.py aix/administration/*.html
    python3 scripts/mark_reviewed.py --date 2026-06-01 vtl/*.html
    python3 scripts/mark_reviewed.py --stale          # list what needs a look

Only run this when you have actually checked the procedure is still correct.
The date is worthless — worse than worthless, it is misleading — if it is
bumped for cosmetic edits. See CONTRIBUTING.md.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_index import (  # noqa: E402
    STALE_MONTHS,
    extract_meta,
    fallback_title,
    months_since,
    parse_reviewed,
    walk_html_files,
)

REVIEWED_TAG = re.compile(r'[ \t]*<meta\s+name=["\']reviewed["\'][^>]*>\n?', re.IGNORECASE)
DESC_TAG = re.compile(r'([ \t]*<meta\s+name=["\']description["\'][^>]*>\n)', re.IGNORECASE)
TITLE_TAG = re.compile(r'([ \t]*<title>[\s\S]*?</title>\n)', re.IGNORECASE)


def stamp(path: Path, when: date) -> tuple[bool, str]:
    """Set the reviewed date on one runbook. Returns (changed, note)."""
    text = path.read_text(encoding="utf-8")
    previous = parse_reviewed(text)
    tag = f'<meta name="reviewed" content="{when.isoformat()}">\n'

    if previous == when:
        return False, f"already {when}"

    if REVIEWED_TAG.search(text):
        text = REVIEWED_TAG.sub(tag, text, count=1)
    else:
        # Anchor after <meta name="description">, else after <title>.
        anchor = DESC_TAG.search(text) or TITLE_TAG.search(text)
        if not anchor:
            return False, "no <title> or <meta description> to anchor to — skipped"
        text = text.replace(anchor.group(1), anchor.group(1) + tag, 1)

    path.write_text(text, encoding="utf-8")
    was = previous.isoformat() if previous else "unreviewed"
    return True, f"{was} → {when}"


def list_stale() -> int:
    rows = []
    for path in walk_html_files(ROOT):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        title, _, _ = extract_meta(text)
        reviewed = parse_reviewed(text)
        age = months_since(reviewed) if reviewed else None
        rows.append((age if age is not None else 10_000, rel, title or fallback_title(rel), reviewed, age))

    rows.sort(reverse=True)
    print(f"{'AGE':>10}  {'REVIEWED':<12} RUNBOOK")
    for _, rel, title, reviewed, age in rows:
        if reviewed is None:
            mark, when, ago = "!!", "—", "unreviewed"
        else:
            mark = "!!" if age >= STALE_MONTHS else ("· " if age >= 6 else "  ")
            when, ago = reviewed.isoformat(), f"{age} months"
        print(f"{mark}{ago:>8}  {when:<12} {rel}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="runbook .html files")
    ap.add_argument("--date", default=None, metavar="YYYY-MM-DD",
                    help="date to stamp (default: today)")
    ap.add_argument("--stale", action="store_true",
                    help="list every runbook by review age and exit")
    ap.add_argument("--no-build", action="store_true",
                    help="skip regenerating index.html")
    args = ap.parse_args()

    if args.stale:
        return list_stale()

    if not args.paths:
        ap.error("give at least one runbook path, or --stale to see what needs reviewing")

    when = date.fromisoformat(args.date) if args.date else date.today()
    if when > date.today():
        ap.error(f"{when} is in the future")

    changed = 0
    for path in args.paths:
        if not path.exists():
            print(f"  !! not found: {path}")
            continue
        did, note = stamp(path, when)
        print(f"  {'✓' if did else '·'} {path}  ({note})")
        changed += did

    if changed and not args.no_build:
        print(flush=True)  # flush before the subprocess writes to the same fd
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_index.py")], check=True)
        print("\nCommit the runbook(s), index.html and assets/js/nav-data.js together.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
