# Contributing

How to add a new runbook so it appears on the [wiki landing page](https://triippiing.github.io/Wiki/).

## TL;DR

1. Save the file under `<category>/<subtag>/your-runbook.html`
2. Give it a `<title>`, a `<meta name="description">`, and a `<meta name="reviewed">` in `<head>`
3. Link the shared assets, and open with an identity strip (see below)
4. Commit and push to `main`

A GitHub Action regenerates `index.html` and `assets/js/nav-data.js` automatically, so your runbook appears as a card, and in the sidebar rail, within about 30 seconds.

## File location

Place the runbook in one of the existing category folders:

| Category  | Path         | Index accent    |
|-----------|--------------|-----------------|
| AIX       | `aix/`       | ochre           |
| Linux     | `linux/`     | sage            |
| Backup    | `backup/`    | rust            |
| Cohesity  | `cohesity/`  | faint           |
| Reference | `reference/` | muted           |
| VTL       | `vtl/`       | ink             |
| Security  | `security/`  | border          |

The second-level folder (`aix/lvm/`, `backup/tsm/`) becomes the card's sub-tag, shown as `aix · lvm`.

## Required `<head>` metadata

```html
<title>Your Runbook Title</title>
<meta name="description" content="One-sentence summary that becomes the card body on the index page.">
<meta name="reviewed" content="2026-07-14">
```

`build_index.py` reads all three. Without `<title>` it falls back to the filename. Without a description the card has no body paragraph. Without a review date the card reads `UNREVIEWED` and the build prints a warning.

## Optional: searchable keywords

To make the runbook findable by terms that aren't in its title, add:

```html
<meta name="keywords" content="vg lv jfs2 mklv crfs extendvg">
```

The landing page's live search checks title, category tag, filename, and these keywords.

## Minimum boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your Runbook Title</title>
<meta name="description" content="One-sentence summary.">
<meta name="reviewed" content="2026-07-14">
<meta name="keywords" content="optional space-separated search terms">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Public+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,600&family=Spectral:wght@600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/runbook.css">
<link rel="stylesheet" href="../../assets/css/sidebar.css">
<script src="../../assets/js/nav-data.js" defer></script>
<script src="../../assets/js/chrome.js" defer></script>
<style>
  /* bespoke classes only, see "Styling" below */
</style>
</head>
<body>
  <!-- runbook content -->
</body>
</html>
```

## The identity strip and the environment block

Every runbook opens with the same two blocks, in this order. This shape is live on all 21 runbooks and new ones should match it.

**The identity strip** (`.meta.meta-identity`) is exactly three cells and is identical in shape on every page. You author two of them. The third, Last reviewed, is appended at load by `chrome.js` from `<meta name="reviewed">`, so the markup never writes it:

```html
<div class="meta meta-identity">
  <div class="meta-cell"><div class="meta-label">Runbook ID</div><div class="meta-val mono">RB-PERF-AIX-001</div></div>
  <div class="meta-cell"><div class="meta-label">Operation</div><div class="meta-val info">Performance triage · CPU / memory / I/O</div></div>
  <!-- Last reviewed cell appended at load by chrome.js -->
</div>
```

**The environment block** (`.env`) holds everything else: hosts, OS levels, NIM masters, maintenance windows, rollback method, spare-disk requirements, whatever this particular procedure needs you to confirm before you start. Its contents vary per runbook, and that is correct, because they describe that runbook's environment. It sits on a quieter surface so it reads as secondary to the identity strip:

```html
<div class="env">
  <div class="env-head">Environment</div>
  <div class="env-grid">
    <div class="env-cell"><div class="env-label">Scope</div><div class="env-val info">Bottleneck triage</div></div>
    <div class="env-cell"><div class="env-label">Privilege</div><div class="env-val warn">root for kernel tools</div></div>
    <div class="env-cell"><div class="env-label">Primary Tools</div><div class="env-val">topas · vmstat · iostat</div></div>
  </div>
</div>
```

Value cells take the same semantic variants in both blocks: `info`, `ok`, `warn`, `mono`.

### Runbook IDs

The ID scheme is `RB-<DOMAIN>-<PLATFORM>-<NNN>`, and the existing allocations live in `scripts/runbook_meta.py`. Read that file to pick the next free number in your domain, then write the ID into the runbook's identity strip yourself. That file is a record of what has been allocated, not a live source: the migration that created it has already run, so editing a string there does not propagate into any page.

Keep the `Operation` line short, roughly 40 characters. It sits beside the ID and the review date, and the fuller description already appears as the page subtitle directly beneath.

**Keep the RB-ID out of the `<title>` and the `<h1>`.** Both are surfaced by browsers, search, and the index card, and the ID is noise in all three. It belongs in the identity strip and the footer, where it reads as reference metadata:

```html
<title>AIX Performance Triage</title>     <!-- no RB-ID -->
<header>
  <div class="logo-dot"></div>
  <h1>AIX Performance Triage</h1>          <!-- no RB-ID -->
</header>
```

## Last reviewed

```html
<meta name="reviewed" content="YYYY-MM-DD">
```

**Bump this when you have actually checked the procedure is still correct.** Not when you fix a typo, and not when a sweeping change (a restyle, a new shared component) touches the file. It is the one date a reader can trust, and it only means anything if it means *"a human confirmed this still works."*

It is deliberately **not** derived from git. A cosmetic commit across every runbook, which is exactly what the stone theme and the sidebar rollout both were, would reset every git date at once and make twenty stale runbooks look freshly checked. That is the precise failure this field exists to prevent.

`chrome.js` renders it as the third identity-strip cell, colour-coded by age: sage under 6 months, ochre 6 to 12, rust beyond 12 or if absent. Every card on the index shows the date too, staying quiet until it earns colour. `build_index.py` prints a warning for anything unreviewed for 12+ months or missing the tag. A missing date shows as `UNREVIEWED` rather than being quietly omitted.

### Bumping the date

Don't hand-edit the tag. Use the helper, which stamps the date and regenerates the index in one go:

```bash
python3 scripts/mark_reviewed.py aix/lvm/aix_lvm_basics.html   # stamp today
python3 scripts/mark_reviewed.py aix/administration/*.html     # several at once
python3 scripts/mark_reviewed.py --date 2026-06-01 vtl/*.html  # a specific day
python3 scripts/mark_reviewed.py --stale                       # what needs a look
```

It adds the tag if the runbook doesn't have one. Commit the runbook, `index.html` and `assets/js/nav-data.js` together.

## File naming

URLs work either way, but **hyphens are nicer than spaces** for sharing:

- `aix-rootvg-disk-replacement.html` gives `https://triippiing.github.io/Wiki/aix/lvm/aix-rootvg-disk-replacement.html`
- `AIX rootvg disk replacement.html` gives `…/AIX%20rootvg%20disk%20replacement.html`, which works, but is uglier

## Styling

Every runbook shares the same design language. The heavy lifting lives in `assets/`:

- **`css/tokens.css`** is the warm stone / ochre palette, the four-font stack (Source Serif 4, Spectral, Public Sans, IBM Plex Mono), reset, base `body` styles, and shared `@keyframes`. It also carries the dark theme (`:root[data-theme="dark"]`, with a `prefers-color-scheme` fallback for the no-JS case), so light and dark are a single token swap. Edit this to shift the design language across every runbook at once.
- **`css/runbook.css`** holds the shared components: `.crumb` breadcrumb, `.page-title`, `.badges`, `.wrap`, the `.meta` / `.meta-identity` strip, the `.env` block, `.phase-label`, the `.steps` / `.step` accordion, `.step-tag` semantic variants (`info`, `ok`, `caution`, `critical`), `.code-panel` and `.cmd`, `.note` variants (`info`, `caution`, `critical`, `verify`, `success`), `.warn-box`, `.controls` and `.ctrl-btn`, tables, and `footer`.
- **`css/sidebar.css`** is the 212px category rail (`.rail`) and its filter, plus the top-left control pill (`.wiki-controls`). On desktop the rail collapses fully in and out (`body.rail-collapsed`, remembered in `localStorage`) and the content reflows to full width; below 1080px it becomes an off-canvas drawer. Hidden in print.
- **`js/chrome.js`** builds the code-block header bar (language label plus a copy-icon button) around every `.cmd` at load, binds the step accordions and their deep links, appends the Last reviewed cell, injects the sidebar rail, and builds the control pill (home, sidebar toggle, theme toggle). It also resolves and persists the light/dark theme (`wiki-theme`) and the rail state (`wiki-rail`); the one sidebar button collapses the column on desktop and opens the drawer on narrow screens. Runbooks do **not** hand-write code-panel markup, a copy script, or any nav markup. Set `data-lang` on a `.cmd` to override the language label, which defaults to `shell`.
- **`js/nav-data.js`** is **generated, so don't edit it**. `build_index.py` writes it alongside `index.html`, and `chrome.js` reads `window.WIKI_NAV` from it to build the rail. A new runbook joins the sidebar automatically the next time the build runs, which CI does on push.

Runbooks live two folders deep (`aix/administration/foo.html`, `backup/tsm/bar.html`), so link with `../../`. A page one folder deep (`vtl/foo.html`) uses `../` instead. `chrome.js` works out the site root from its own `src`, so nav links resolve correctly from either depth with no configuration.

Load `tokens.css` first, because `runbook.css` and `sidebar.css` both depend on its `--*` variables. Load `nav-data.js` before `chrome.js`. Both are `defer`, which preserves order.

### Shared vs bespoke

Keep an inline `<style>` block **only** for classes specific to your runbook, usually content-shaped tables (`.finding-*`, `.tier-*`, `.primer-*`, `.flag-table`, `.summary-table`) or step-accent overrides:

```css
.step.ph-cpu  { border-left-color: var(--rust);  }
.step.ph-disk { border-left-color: var(--ochre); }
```

Always reference token variables (`var(--ochre)`, `var(--border)`, and so on). Never hard-code colours in bespoke rules. The palette is deliberately restrained: stone paper, one ochre accent, `--rust` for caution, `--sage` for verify, and mono for anything machine-readable. If you catch yourself copy-pasting the same bespoke component into a second runbook, promote it into `runbook.css` instead.

### Reference cheatsheets, an intentional exception

Pages under `reference/` (currently `tsm_restore_cheatsheet.html` and `FTP SCP RSYNC cheatsheet.html`) use a **different design system** on purpose. They are quick-lookup reference cards: light-mode, dense tool-block layout, everything visible at once, rather than step-through procedures. Forcing them into the runbook `.step` accordion would actively make them worse for their intended use.

If you add a new reference cheatsheet, model it on the existing two rather than the runbook library. If you add a *procedural* runbook to `reference/`, use the standard runbook layout instead.

## Adding a new category

If you want a category that doesn't exist yet, say `database/` or `monitoring/`:

1. Create the folder and drop the runbook in. It will appear under a section with a neutral accent.
2. To give it a proper name, ordering and accent, edit `scripts/build_index.py` and add an entry to the `CATEGORIES` dict near the top:

   ```python
   CATEGORIES = {
       # ...existing categories...
       "database": {"name": "Database", "accent": "ref", "order": 8},
   }
   ```

   `order` is the position on the landing page, and 1 to 7 are taken. Existing accents are `aix`, `linux`, `backup`, `cohesity`, `ref`, `vtl` and `sec`. To add a fresh one, define an `.accent-<name>` rule in the `STYLES` constant lower down the same file, pointing at a token colour.

## How the build works

- `scripts/build_index.py` walks the repo for `*.html` files, reads their metadata, and regenerates both `index.html` and `assets/js/nav-data.js`. It skips `.git/`, `.github/`, `node_modules/`, `scripts/`, `docs/`, `assets/`, `_sandbox/`, and `index.html` itself.
- `.github/workflows/build-index.yml` runs the script on every push that touches an HTML file or the build script.
- The action commits the regenerated files back with `[skip ci]` in the message, so there is no loop.
- Pure Python stdlib, no dependencies.

## Don't edit `index.html` or `nav-data.js` by hand

Both are regenerated on every push, and manual edits will be overwritten. To change the landing page's layout, hero copy, header, or styling, edit the template constants (`STYLES`, `SCRIPT`, `TEMPLATE`) in `scripts/build_index.py`.

## Testing locally before pushing

Rebuild the landing page and the nav data:

```sh
python3 scripts/build_index.py
```

**Don't open the runbook HTML from Finder.** That loads it under `file://`, which blocks the shared stylesheets in `assets/css/` from loading, since they live in a parent directory, and the page renders unstyled. Serve the wiki over http instead:

```sh
./serve.sh                                    # http://localhost:8765/
open http://localhost:8765/                   # or browse to a specific runbook
```

`serve.sh` is a one-line wrapper around `python3 -m http.server`. No dependencies, runs on macOS-default Python 3 and ubuntu-latest.

**Check pages in a private window.** `assets/js/chrome.js` is a stable URL that keeps gaining behaviour, so Safari will happily serve you a cached copy and you will conclude a change is broken when it isn't. Cmd+Option+R ("Reload Page From Origin") also works.
