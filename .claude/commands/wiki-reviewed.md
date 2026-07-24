---
description: Stamp a runbook as re-read, with a guard against sweeping dates in during a bulk edit
argument-hint: "<path.html> [more paths]"
---

Stamp the review date on: `$ARGUMENTS`

`<meta name="reviewed">` means *a human confirmed this procedure still works*. It is the one date a reader can trust. Treat it accordingly.

1. **Guard against a bulk edit first.** Run:
   ```bash
   git status --short -- '*.html'
   ```
   If more than two `.html` files are modified beyond the ones named in `$ARGUMENTS`, that is the signature of a restyle or a markup migration. Stop and ask Jack before going further. A sweeping change must never bump review dates, because that is the exact failure the field exists to prevent.

2. **Check the premise.** If it is not already clear from the conversation that Jack has actually re-read the procedure, ask. Do not stamp a date because a file was edited. A typo fix is not a review.

3. **Use the helper, never a hand edit.** It stamps the date and regenerates the index in one step:
   ```bash
   python3 scripts/mark_reviewed.py <paths>
   ```
   Pass `--date YYYY-MM-DD` only if Jack named a specific day. The helper adds the tag if the file lacks one.

4. **Show what is now stale:**
   ```bash
   python3 scripts/mark_reviewed.py --stale
   ```

5. **Remind him what to commit together:** the runbook, `index.html`, and `assets/js/nav-data.js`. Committing the runbook alone leaves the index disagreeing with the page.
