# Meta-grid migration — identity strip + environment block

**Status: groundwork done, migration NOT started (0 / 21).**
Paused deliberately. Safe to leave in this state indefinitely.

Written 2026-07-13 so this can be picked up cold, by a future session or by a
future you, with no archaeology.

---

## Resume in one command

```bash
python3 scripts/migrate_meta.py --status
```

That prints exactly what's done and what's left. Progress is derived from the
files themselves, never from a checklist, so it cannot drift out of date.

Then:

```bash
# pilot one runbook first and LOOK at it in a browser
python3 scripts/migrate_meta.py --dry-run "aix/administration/aix_71_to_72_migration_nim.html"
python3 scripts/migrate_meta.py         "aix/administration/aix_71_to_72_migration_nim.html"
python3 scripts/build_index.py
./serve.sh          # then open the page in a PRIVATE window (see Gotchas)

# happy? do the rest
python3 scripts/migrate_meta.py --all
python3 scripts/build_index.py
```

---

## The problem being solved

The meta grid at the top of each runbook had grown to **~100 distinct labels,
most used exactly once**, and 6–12 cells per runbook. Jack's words: *"lots of
runbooks have bespoke squares in there and i dont like how inconsistent it is."*

The naive fix — cut it to three cells — would have **deleted ~130 cells of real
operational content**: host names, source/target OS levels, NIM masters,
maintenance windows, rollback methods, spare-disk requirements. That is the
pre-flight checklist you confirm at 2am *before* starting. Prettier, and worse.

So the fix is **separation, not deletion**.

## The design

**Identity strip** — `<div class="meta meta-identity">`, exactly three cells,
byte-identical in shape on every runbook. This is the consistency that was
wanted.

| Runbook ID | Operation | Last reviewed |
|---|---|---|
| `RB-PATCH-AIX-002` | Version migration · 7.1 → 7.2 · nimadm | 02 May 2026 · 2 MONTHS |

The first two are authored, from `scripts/runbook_meta.py`. The third is
appended at load by `chrome.js` from `<meta name="reviewed">` — the runbook
never writes it.

**Environment block** — `<div class="env">`, everything else, unchanged. A
quieter surface (`--surface`, no shadow, tighter cells) so it reads as
secondary to the identity strip. Its contents legitimately vary per runbook,
because they describe that runbook's environment. Inconsistency *there* is
correct; inconsistency in the identity strip was not.

## Why a half-finished migration is safe

This is the property that lets you stop at any point:

* A runbook is either **old** (one `.meta` grid holding everything) or **new**
  (`.meta.meta-identity` + `.env`).
* `runbook.css` styles **both**. `chrome.js` appends the reviewed cell to
  **either**.
* Therefore a partly-migrated wiki is merely *inconsistent* — exactly what it
  is today — and never *broken*.

`migrate_meta.py` is idempotent: it skips anything already carrying
`.meta-identity`, so re-running it is harmless.

## Decisions already made — do not re-litigate

* **RB-IDs: approved by Jack, 2026-07-13.** All 21, in
  `scripts/runbook_meta.py`. Scheme `RB-<DOMAIN>-<PLATFORM>-<NNN>`. The five
  that already existed are preserved exactly. Only 5 of 21 runbooks had an ID
  before; the other 16 are newly minted.
* **Bespoke cells are demoted, not deleted.** Jack chose this explicitly over
  both "collapse behind a toggle" and "actually delete it".
* The two `reference/` cheatsheets are **out of scope** — they don't use the
  shared asset library at all. That's a long-standing intentional exception.

## Still needs a human

* **The `operation` strings in `runbook_meta.py` are MY DRAFTS, not approved.**
  The IDs were signed off; the one-line summaries were not. Review them —
  ideally before running `--all`, since fixing them afterwards means editing
  21 files instead of one manifest.
* Nothing else. The IDs, the design and the tooling are settled.

## Gotchas

* **Check pages in a private window.** `assets/js/chrome.js` is a stable URL
  that keeps gaining behaviour, so Safari will happily serve you a cached copy
  and you will think the change is broken when it isn't. This has already
  wasted time once. Cmd+Option+R ("Reload Page From Origin") also works.
* Commit the runbooks, `index.html` and `assets/js/nav-data.js` together —
  `build_index.py` regenerates the latter two.

## Files

| File | Role |
|---|---|
| `scripts/runbook_meta.py` | **Data.** The 21 approved RB-IDs + operation lines. |
| `scripts/migrate_meta.py` | The idempotent migrator. `--status` / `--dry-run` / `--all`. |
| `assets/css/runbook.css` | `.meta-identity` and `.env` styles. Already in place, inert until markup uses them. |
| `assets/js/chrome.js` | Appends the Last reviewed cell. Needs no change — works with both shapes. |
