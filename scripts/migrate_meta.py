#!/usr/bin/env python3
"""Migrate a runbook's meta grid to identity strip + environment block.

    python3 scripts/migrate_meta.py --status              # what's left
    python3 scripts/migrate_meta.py --dry-run <path>      # show the rewrite
    python3 scripts/migrate_meta.py <path> [<path> ...]   # do it
    python3 scripts/migrate_meta.py --all                 # everything remaining

RESUMABLE BY DESIGN. Migration state is derived from the files themselves
(a migrated grid carries .meta-identity), never from a checklist that could
drift. Re-running is safe: already-migrated files are skipped. Stopping
half-way is safe: chrome.js and runbook.css render BOTH the old and the new
shape, so a partly-migrated wiki is merely inconsistent, not broken.

See docs/META_GRID_MIGRATION.md.

What it does, per runbook:
  · the identity strip gets exactly two authored cells — Runbook ID and
    Operation — from scripts/runbook_meta.py. chrome.js appends the third
    (Last reviewed) at load.
  · EVERY other cell moves, unchanged, into a secondary .env block. Nothing
    is discarded: these are pre-flight facts (host, versions, windows,
    rollback, spare disk), not decoration.

Pure stdlib.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from runbook_meta import RUNBOOKS  # noqa: E402

CELL_RE = re.compile(
    r'<div class="meta-cell[^"]*">\s*'
    r'<div class="meta-label">(?P<label>[\s\S]*?)</div>\s*'
    r'<div class="meta-val(?P<cls>[^"]*)">(?P<val>[\s\S]*?)</div>\s*'
    r'</div>',
    re.IGNORECASE,
)

# Superseded by the manifest — dropped rather than moved to .env.
IDENTITY_LABELS = {"runbook id", "operation"}

MIGRATED_MARK = "meta-identity"


def find_grid(text: str) -> tuple[int, int] | None:
    """Byte span of the <div class="meta"> … matching </div> block."""
    m = re.search(r'[ \t]*<div class="meta">', text)
    if not m:
        return None
    i = m.end()
    depth = 1
    for tag in re.finditer(r'<(/?)div\b', text[i:]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            end = i + tag.end()
            end = text.find(">", end - 1) + 1
            return m.start(), end
    return None


def render(rb_id: str, operation: str, env_cells: list[tuple[str, str, str]]) -> str:
    ident = (
        '  <div class="meta meta-identity">\n'
        f'    <div class="meta-cell"><div class="meta-label">Runbook ID</div>'
        f'<div class="meta-val mono">{html.escape(rb_id)}</div></div>\n'
        f'    <div class="meta-cell"><div class="meta-label">Operation</div>'
        f'<div class="meta-val info">{operation}</div></div>\n'
        '    <!-- Last reviewed cell appended at load by chrome.js -->\n'
        '  </div>'
    )
    if not env_cells:
        return ident

    rows = "\n".join(
        f'      <div class="env-cell"><div class="env-label">{label}</div>'
        f'<div class="env-val{cls}">{val}</div></div>'
        for label, cls, val in env_cells
    )
    env = (
        '\n\n  <div class="env">\n'
        '    <div class="env-head">Environment</div>\n'
        '    <div class="env-grid">\n'
        f'{rows}\n'
        '    </div>\n'
        '  </div>'
    )
    return ident + env


def migrate(path: Path, dry_run: bool = False) -> str:
    rel = path.relative_to(ROOT).as_posix()
    entry = RUNBOOKS.get(rel)
    if not entry:
        return f"!! not in runbook_meta.py — skipped: {rel}"
    rb_id, operation = entry

    text = path.read_text(encoding="utf-8")
    if MIGRATED_MARK in text:
        return f" · already migrated: {rel}"

    span = find_grid(text)
    if not span:
        return f"!! no <div class=\"meta\"> grid found — skipped: {rel}"
    start, end = span
    grid = text[start:end]

    cells = list(CELL_RE.finditer(grid))
    if not cells:
        return f"!! grid found but no .meta-cell parsed — skipped: {rel}"

    env_cells = [
        (c.group("label").strip(), c.group("cls").rstrip(), c.group("val").strip())
        for c in cells
        if c.group("label").strip().lower() not in IDENTITY_LABELS
    ]
    dropped = len(cells) - len(env_cells)

    new_text = text[:start] + render(rb_id, operation, env_cells) + text[end:]

    if dry_run:
        print(f"\n─── {rel}")
        print(f"    {rb_id} · {operation}")
        print(f"    {len(cells)} cells → 2 identity (+1 at load), "
              f"{len(env_cells)} to .env, {dropped} superseded\n")
        print(render(rb_id, operation, env_cells))
        return f" ~ dry-run: {rel}"

    path.write_text(new_text, encoding="utf-8")
    return f" ✓ migrated: {rel}  ({len(cells)} cells → 2 + {len(env_cells)} env)"


def status() -> int:
    done, todo = [], []
    for rel in sorted(RUNBOOKS):
        p = ROOT / rel
        if not p.exists():
            todo.append((rel, "MISSING FILE"))
            continue
        (done if MIGRATED_MARK in p.read_text(encoding="utf-8") else todo).append(
            (rel, RUNBOOKS[rel][0])
        )

    total = len(RUNBOOKS)
    print(f"meta-grid migration: {len(done)} / {total} done, {len(todo)} remaining\n")
    if done:
        print("  migrated:")
        for rel, rb_id in done:
            print(f"    ✓ {rb_id:<17} {rel}")
    if todo:
        print("\n  remaining:")
        for rel, rb_id in todo:
            print(f"    · {rb_id:<17} {rel}")
        print("\n  resume with:  python3 scripts/migrate_meta.py --all")
    else:
        print("  Nothing left. Rebuild the index and commit.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--status", action="store_true", help="show progress and exit")
    ap.add_argument("--all", action="store_true", help="migrate everything remaining")
    ap.add_argument("--dry-run", action="store_true", help="print the rewrite, change nothing")
    args = ap.parse_args()

    if args.status:
        return status()

    if args.all:
        paths = [ROOT / rel for rel in sorted(RUNBOOKS)]
    elif args.paths:
        paths = [p if p.is_absolute() else Path.cwd() / p for p in args.paths]
    else:
        ap.error("give a runbook path, or --all, or --status")

    for p in paths:
        print(migrate(p.resolve(), dry_run=args.dry_run))

    if not args.dry_run:
        print("\nNow: python3 scripts/build_index.py   (then check the page, then commit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
