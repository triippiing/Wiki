---
description: Preflight the wiki before pushing: rebuild the index, serve locally, verify the shared assets actually load
argument-hint: "[optional runbook path to also check]"
---

Preflight this repo. Do not commit anything, and do not push. This command only reports.

Work from the repo root (`Wiki/`).

1. **Rebuild the generated files.**
   ```bash
   python3 scripts/build_index.py
   ```
   Surface any warnings it prints verbatim, especially `UNREVIEWED` pages and anything unreviewed for 12+ months. Do not fix those here, just report them.

2. **Make sure a server is up.** Check whether anything is already listening on 8765:
   ```bash
   lsof -nP -iTCP:8765 -sTCP:LISTEN
   ```
   If nothing is, start `./serve.sh` in the background. If something is, reuse it rather than starting a second one.

3. **Verify the shared assets return 200 over http.** This is the whole point of the command. Under `file://` these silently fail and the page renders unstyled, so a visual check proves nothing.
   ```
   /
   /assets/css/tokens.css
   /assets/css/runbook.css
   /assets/css/sidebar.css
   /assets/js/nav-data.js
   /assets/js/chrome.js
   ```
   If `$ARGUMENTS` names a runbook, check that URL too (URL-encode spaces in the filename).

4. **Report which generated files moved:**
   ```bash
   git status --short
   ```
   Call out `index.html` and `assets/js/nav-data.js` specifically. Both are generated, so changes there are expected after step 1 and are not something to worry about.

5. **Summarise as a table** of path and HTTP code. Any non-200 is a failure: say so plainly, name the file, and stop rather than reporting the run as clean.

Two things to remember when interpreting the result:

- `assets/js/chrome.js` caches hard. If you are checking a change to it, add a cache-busting query string or the 200 you get back may be the old file.
- A 200 means the asset is reachable, not that the page looks right. Say what you verified, not more.
