---
description: Pilot a bulk change on one representative runbook in _sandbox/ before touching the rest
argument-hint: "<representative-file.html> <what to change>"
---

Pilot a change before applying it broadly: `$ARGUMENTS`

This exists because sweeping edits across many runbooks are hard to review after the fact and expensive to undo. One file, reviewed properly, catches the problem the other twenty would have inherited.

**The rule: nothing outside `_sandbox/` gets touched until Jack signs off.** If you find yourself opening a second real runbook, you have broken the point of this command.

1. **Pick the representative file.** If `$ARGUMENTS` does not name one, propose one and explain why it represents the set: it should be typical in structure, not the simplest page in the repo. A pilot on the easiest file proves nothing.

2. **Copy it into the sandbox:**
   ```bash
   mkdir -p _sandbox
   cp "<file>" "_sandbox/<name>.html"
   ```
   `_sandbox/` is in `build_index.py`'s `SKIP_DIRS`, so pilots never reach the index or the sidebar rail.

3. **Apply the change to the sandbox copy only.**

4. **Serve it and give Jack the URL:**
   ```bash
   ./serve.sh
   ```
   then the `http://localhost:8765/_sandbox/<name>.html` link. Never ask him to open it from Finder: `file://` blocks the shared CSS and the page will look broken for reasons unrelated to your change.

5. **Stop and wait.** Report what you changed and what he should look at specifically. Do not proceed to the other files, and do not offer to, until he has said the pilot looks right.

6. **After sign-off**, apply the same change to the real files. Remember that a bulk change like this must not touch any `<meta name="reviewed">` date, no matter how many files it modifies.
