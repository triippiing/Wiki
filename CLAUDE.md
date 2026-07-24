# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this is

A library of hand-written HTML runbooks for AIX/Linux administration, published via
GitHub Pages at <https://triippiing.github.io/Wiki/>. No framework, no bundler, no
dependencies. Writing a runbook means writing HTML.

This is its own git repo (`origin` = `triippiing/Wiki.git`, branch `main`). It sits
inside `~/Documents/AUTOMATION/`, which is *not* a repo. Nothing outside `Wiki/` is
version controlled, so never assume a parent-level git operation will work.

## Read CONTRIBUTING.md before authoring or restyling

`CONTRIBUTING.md` is the authoritative spec for page structure: required `<head>`
metadata, the identity strip and `.env` block, the RB-ID scheme, shared vs bespoke
CSS, and how to add a category. Read it rather than inferring the pattern from a
nearby runbook, which may predate the current shape.

## Generated files: never hand-edit

- `index.html`
- `assets/js/nav-data.js`

`scripts/build_index.py` writes both, and CI regenerates them on every push that
touches HTML. Manual edits are silently overwritten. To change the landing page's
layout, copy, or styling, edit the `STYLES` / `SCRIPT` / `TEMPLATE` constants inside
`build_index.py` instead.

## Verify locally before pushing

```sh
python3 scripts/build_index.py     # rebuild index.html + nav-data.js
./serve.sh                         # http://localhost:8765/  (optional port arg)
```

Never open a runbook from Finder. Under `file://` the browser blocks the shared
stylesheets in `assets/css/`, the page renders unstyled, and you will report a
working change as broken.

`assets/js/chrome.js` is a stable URL that keeps gaining behaviour, so it caches
aggressively. Check changes in a private window or with a cache-busting query
string before concluding anything about them.

## Reviewed dates: do not bump them for cosmetic work

`<meta name="reviewed">` means *a human confirmed this procedure still works*. It is
deliberately not derived from git, precisely so a repo-wide restyle cannot make
twenty stale runbooks look freshly checked.

**When a change touches many files (a theme, a shared component, a markup
migration), leave every `reviewed` date exactly as it is.** Only Jack bumps these,
and only after actually re-reading the procedure.

When it is legitimately time to stamp one, use the helper rather than editing the
tag by hand, since it regenerates the index in the same step:

```sh
python3 scripts/mark_reviewed.py <path.html>       # stamp today
python3 scripts/mark_reviewed.py --stale           # report what needs a look
```

## Pilot before bulk edits

For any change spanning multiple runbooks, copy one representative file into
`_sandbox/`, apply the change there, and get Jack's sign-off on that single page
before touching the rest. `_sandbox/` is in `build_index.py`'s `SKIP_DIRS`, so
pilots never reach the index or the sidebar.

## Writing style

- **No em dashes or en dashes** in any prose, comments, or page copy. Use commas,
  colons, or parentheses. They read as machine-written and Jack strips them.
- Keep RB-IDs out of `<title>` and `<h1>`. They belong in the identity strip and the
  footer, not in anything surfaced by browsers, search, or the index card.
- Prose in runbooks is plain and operational. Match the voice of the page you are in.
- Write code comments and notations that read like the surrounding code: match its
  comment density, naming, and idiom.

## Layout

| Path | What |
|---|---|
| `<category>/<subtag>/*.html` | The runbooks. Two folders deep, so assets link via `../../` |
| `assets/css/` | `tokens.css` (palette, fonts, dark theme), `runbook.css`, `sidebar.css` |
| `assets/js/` | `chrome.js` (page chrome, built at load), `nav-data.js` (generated) |
| `scripts/` | `build_index.py`, `mark_reviewed.py`, `runbook_meta.py`, `migrate_meta.py` |
| `meta/` | Pages about the wiki itself: contributing, design system, architecture |
| `reference/` | Cheatsheets on a deliberately different design system. See CONTRIBUTING.md |

`scripts/runbook_meta.py` is a record of allocated RB-IDs, not a live source. The
migration that used it has already run, so editing a string there changes nothing.
