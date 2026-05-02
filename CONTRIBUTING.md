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
<!-- styles, etc. -->
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

```sh
python3 scripts/build_index.py
open index.html
```

No dependencies — runs on macOS-default Python 3 and ubuntu-latest.
