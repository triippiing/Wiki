# Meta-grid migration: identity strip + environment block

**Status: complete. All 21 runbooks migrated, 2026-07-14.**

`python3 scripts/migrate_meta.py --status` confirms this from the files themselves, never from a checklist, so it cannot drift out of date.

This is a record of a change that has already landed. It is kept because the reasoning behind the shape is not obvious from the markup, and because the same questions will come back the next time the top of a runbook gets reworked. The authoring rules that came out of it live in `CONTRIBUTING.md`, which is where you should look if you are writing a new runbook.

---

## The problem that was solved

The meta grid at the top of each runbook had grown to roughly 100 distinct labels, most of them used exactly once, and 6 to 12 cells per runbook. Jack's words: *"lots of runbooks have bespoke squares in there and i dont like how inconsistent it is."*

The naive fix, cutting it to three cells, would have deleted around 130 cells of real operational content: host names, source and target OS levels, NIM masters, maintenance windows, rollback methods, spare-disk requirements. That is the pre-flight checklist you confirm at 2am *before* starting. Prettier, and worse.

So the fix was separation, not deletion.

## The design

**Identity strip**, `<div class="meta meta-identity">`, exactly three cells, identical in shape on every runbook. This is the consistency that was wanted.

| Runbook ID | Operation | Last reviewed |
|---|---|---|
| `RB-PATCH-AIX-002` | Version migration · 7.1 → 7.2 · nimadm | 02 May 2026 · 2 MONTHS |

The first two are authored. The third is appended at load by `chrome.js` from `<meta name="reviewed">`, so the runbook never writes it.

**Environment block**, `<div class="env">`, holds everything else, unchanged. A quieter surface (`--surface`, no shadow, tighter cells) so it reads as secondary to the identity strip. Its contents legitimately vary per runbook, because they describe that runbook's environment. Inconsistency *there* is correct. Inconsistency in the identity strip was not.

## Decisions made, do not re-litigate

* **RB-IDs approved 2026-07-13, operation strings approved 2026-07-14.** Scheme is `RB-<DOMAIN>-<PLATFORM>-<NNN>`. The five IDs that already existed in runbooks were preserved exactly. The other 16 were newly minted.
* **Bespoke cells were demoted, not deleted.** Jack chose this explicitly over both "collapse behind a toggle" and "actually delete it".
* The two `reference/` cheatsheets were **out of scope**. They don't use the shared asset library at all, which is a long-standing intentional exception.

## Why the migration was safe to pause partway

It ran to completion in the end, but it was built so that it didn't have to, and that property is worth keeping for the next structural change:

* A runbook was either **old** (one `.meta` grid holding everything) or **new** (`.meta.meta-identity` plus `.env`).
* `runbook.css` styles **both**, and `chrome.js` appends the reviewed cell to **either**.
* So a partly-migrated wiki was merely *inconsistent*, which is what it already was, and never *broken*.

`migrate_meta.py` is idempotent. It skips anything already carrying `.meta-identity`, so re-running it is harmless.

## Living with the result

`scripts/runbook_meta.py` is now a **record of allocated IDs, not a live source**. The strings were baked into each runbook's markup when the migration ran, so editing an `operation` there does **not** propagate. Edit the runbook. Read the file to pick the next free number when you add a runbook.

Two things that cost time during the migration and will cost it again:

* **Check pages in a private window.** `assets/js/chrome.js` is a stable URL that keeps gaining behaviour, so Safari will serve a cached copy and you will think a change is broken when it isn't. Cmd+Option+R ("Reload Page From Origin") also works.
* **Commit the runbooks, `index.html` and `assets/js/nav-data.js` together.** `build_index.py` regenerates the latter two.

## Files

| File | Role |
|---|---|
| `scripts/runbook_meta.py` | The 21 allocated RB-IDs and operation lines. A record, not a live source. |
| `scripts/migrate_meta.py` | The idempotent migrator. `--status`, `--dry-run`, `--all`. Nothing left to migrate. |
| `assets/css/runbook.css` | `.meta-identity` and `.env` styles. |
| `assets/js/chrome.js` | Appends the Last reviewed cell. Works with both the old and new shapes. |
