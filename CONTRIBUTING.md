# Contributing

How to add a new runbook so it appears on the [wiki landing page](https://triippiing.github.io/Wiki/).

## TL;DR

1. Save the file under `<category>/<subtag>/your-runbook.html`
2. Make sure it has a `<title>` and `<meta name="description">` in `<head>`
3. Commit and push to `main`

A GitHub Action regenerates `index.html` automatically — your new runbook appears as a card within ~30s.

## File location

Place the runbook in one of the existing category folders:

| Category    | Path         | Index accent |
|-------------|--------------|--------------|
| AIX         | `aix/`       | cyan         |
| Linux       | `linux/`     | amber        |
| Backup      | `backup/`    | green        |
| Reference   | `reference/` | purple       |
| VTL         | `vtl/`       | red          |
| Security    | `security/`  | grey         |

The second-level folder (e.g. `aix/lvm/`, `backup/tsm/`) becomes the card's sub-tag (`aix · lvm`).

## Required `<head>` metadata

```html
<title>Your Runbook Title — Short Tagline</title>
<meta name="description" content="One-sentence summary that becomes the card body on the index page.">
```

The build script reads both. Without `<title>` it falls back to the filename. Without `<meta description>` the card just won't have a description paragraph.

## Optional: searchable keywords

To make the runbook findable by terms not in its title, add:

```html
<meta name="keywords" content="vg lv jfs2 mklv crfs extendvg">
```

The landing page's live search filter checks: title, category tag, filename, and these keywords.

## Minimum boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your Runbook Title — Short Tagline</title>
<meta name="description" content="One-sentence summary.">
<meta name="keywords" content="optional space-separated search terms">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/runbook.css">
<style>
  /* bespoke classes only — see "Styling" below */
</style>
</head>
<body>
  <!-- runbook content -->
</body>
</html>
```

## File naming

URLs work either way, but **hyphens are nicer than spaces** for sharing:

- `aix-rootvg-disk-replacement.html` → `https://triippiing.github.io/Wiki/aix/lvm/aix-rootvg-disk-replacement.html`
- `AIX rootvg disk replacement.html` → `…/AIX%20rootvg%20disk%20replacement.html` (works, but uglier)

## Styling

Every runbook shares the same design language. The heavy lifting lives in two stylesheets under `assets/css/`:

- **`tokens.css`** — colour palette, typography, reset, base `body` styles, shared `@keyframes`. Edit this to shift the design language across every runbook at once.
- **`runbook.css`** — shared components: `header` + `.logo-dot` + `.badge`, `.wrap`, `.meta` grid, `.phase-label`, `.steps` / `.step` accordion, `.step-tag` semantic variants (`info` / `ok` / `caution` / `critical`), `.cmd` code blocks + `.copy-btn`, `.note` variants, `.warn-box`, `.controls` / `.ctrl-btn`, `footer`.

Runbooks live two folders deep (`aix/administration/foo.html`, `backup/tsm/bar.html`), so link with `../../`:

```html
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/runbook.css">
```

Load `tokens.css` first — `runbook.css` depends on its `--*` variables.

### Shared vs bespoke

Keep an inline `<style>` block **only** for classes specific to your runbook — usually content-shaped tables (`.finding-*`, `.tier-*`, `.primer-*`, `.flag-table`, `.summary-table`) or step-accent overrides:

```css
.step.ph-cpu  { border-left-color: var(--amber); }
.step.ph-disk { border-left-color: var(--cyan);  }
```

Always reference token variables (`var(--cyan)`, `var(--border)`, …) — never hard-code colours in bespoke rules. If you catch yourself copy-pasting the same bespoke component into a second runbook, promote it into `runbook.css` instead.

Existing runbooks still carry their full inline `<style>` block from before the library existed. Migrate them opportunistically when you touch a page — no need for a big-bang cleanup.

### Reference cheatsheets — an intentional exception

Pages under `reference/` (currently `tsm_restore_cheatsheet.html`, `FTP SCP RSYNC cheatsheet.html`) use a **different design system** on purpose. They're quick-lookup reference cards — light-mode, dense tool-block layout, everything visible at once — not step-through procedures. Forcing them into the runbook `.step` accordion would actively make them worse for their intended use.

If you add a new reference cheatsheet, model it on the existing two rather than the runbook library. If you add a *procedural* runbook to `reference/`, use the standard runbook layout instead.

## Title convention (RB-IDs)

If your runbook has an RB-ID (e.g. `RB-AIX-042`), **do not** put it in the `<title>` element or the sticky-header `<h1>`. Those are surfaced by browsers, search, and the wiki index card — the ID adds noise there. Show it inside the `.meta` grid and the `footer`, where it belongs as reference metadata:

```html
<title>AIX Performance Triage</title>       <!-- no RB-ID -->
<!-- ... -->
<header>
  <div class="logo-dot"></div>
  <h1>AIX Performance Triage</h1>            <!-- no RB-ID -->
</header>
<div class="meta">
  <div class="meta-cell">
    <div class="meta-label">RB-ID</div>
    <div class="meta-val">RB-AIX-042</div>
  </div>
  <!-- ... -->
</div>
```

## Adding a new category

If you want a category that doesn't exist yet (e.g. `database/`, `monitoring/`):

1. Just create the folder and drop the runbook in — it will appear under a section with a neutral grey accent.
2. To give it a proper name and accent color, edit `scripts/build_index.py` and add an entry to the `CATEGORIES` dict near the top:

   ```python
   CATEGORIES = {
       # ...existing categories...
       "database": {"name": "Database", "accent": "ref", "order": 7},
   }
   ```

   Existing accents: `aix` (cyan), `linux` (amber), `backup` (green), `ref` (purple), `vtl` (red), `sec` (grey). Add a new color in the CSS (`STYLES` constant) if you want a fresh one.

## How the build works

- `scripts/build_index.py` walks the repo for `*.html` files (skipping `.git/`, `.github/`, `scripts/`, `docs/`, and `index.html` itself), reads metadata, and regenerates `index.html`.
- `.github/workflows/build-index.yml` runs the script on every push that touches an HTML file or the build script.
- The action commits the regenerated `index.html` back with `[skip ci]` in the message — no infinite loops.
- Pure Python stdlib, no dependencies.

## Don't edit `index.html` by hand

It's regenerated on every push. Manual edits will be overwritten. To change the layout, hero copy, header, or styling, edit the template constants (`STYLES`, `SCRIPT`, `TEMPLATE`) in `scripts/build_index.py`.

## Testing locally before pushing

Rebuild the landing page:

```sh
python3 scripts/build_index.py
```

**Don't `open` the runbook HTML from Finder** — Safari opens it under `file://`, which blocks the shared stylesheets in `assets/css/` from loading (they live in a parent directory). Serve the wiki over http:// instead:

```sh
./serve.sh                                    # http://localhost:8765/
open http://localhost:8765/                   # or browse to a specific runbook
```

`serve.sh` is a one-line wrapper around `python3 -m http.server`. No dependencies — runs on macOS-default Python 3 and ubuntu-latest.
