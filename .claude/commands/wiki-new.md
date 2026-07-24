---
description: Scaffold a new runbook from the CONTRIBUTING spec, allocating the next free RB-ID
argument-hint: "<category>/<subtag> \"Runbook Title\""
---

Scaffold a new runbook: `$ARGUMENTS`

**Read `CONTRIBUTING.md` first**, specifically "Minimum boilerplate" and "The identity strip and the environment block". Build the file from that spec. Do not copy a nearby runbook: some predate the current shape, and you will propagate an old pattern.

1. **Collect what you need.** From `$ARGUMENTS` or by asking:
   - Category and sub-tag, which is the folder pair (`aix/lvm`, `backup/tsm`). Categories are `aix`, `linux`, `backup`, `cohesity`, `reference`, `vtl`, `security`.
   - Title, in plain prose.
   - One-sentence description, which becomes the card body on the index.
   - Optional keywords for the live search, for terms not already in the title.
   - The `Operation` line, roughly 40 characters, since it sits beside the ID and the date.

2. **Allocate the RB-ID.** The scheme is `RB-<DOMAIN>-<PLATFORM>-<NNN>`. Find what is taken:
   ```bash
   grep -ohrE 'RB-[A-Z]+-[A-Z]+-[0-9]+' . --include='*.html' | sort -u
   ```
   Pick the next free number in that domain and platform. Note that `scripts/runbook_meta.py` is a historical record, not a live source: editing it changes nothing, so do not bother.

3. **Write the file** at `<category>/<subtag>/<name>.html`. Hyphens in the filename, not spaces. Assets link via `../../` because runbooks sit exactly two folders deep.

   Requirements that are easy to get wrong:
   - `<meta name="reviewed">` is today's date, since you are writing the procedure now.
   - The identity strip has exactly two authored cells, Runbook ID and Operation. The third, Last reviewed, is appended at load by `chrome.js`. Do not write it into the markup.
   - **Keep the RB-ID out of `<title>` and `<h1>`.** It belongs in the identity strip and the footer only.
   - Value cells take `info`, `ok`, `warn`, `mono`.
   - Put bespoke CSS in the page's `<style>` block. Shared components belong in `assets/css/`.

4. **Rebuild the index:**
   ```bash
   python3 scripts/build_index.py
   ```

5. **Tell Jack to run `/wiki-check`** before pushing, and remind him the body is a skeleton: you scaffolded the structure, you did not write the procedure.
