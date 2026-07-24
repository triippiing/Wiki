---
description: Commit, push, watch the build-index workflow, and confirm the Pages deploy landed
argument-hint: "[commit message]"
---

Ship the current work. Commit message: `$ARGUMENTS`

1. **Show what is about to go out** before doing anything:
   ```bash
   git status --short
   git diff --stat
   git rev-parse --abbrev-ref HEAD
   ```

2. **Check for accidental review-date changes:**
   ```bash
   git diff -- '*.html' | grep -E '^[-+].*meta name="reviewed"'
   ```
   If review dates changed and this is not a deliberate `/wiki-reviewed` run, stop and ask. A restyle must not bump them.

3. **Commit.** If `$ARGUMENTS` is empty, propose a message from the actual diff and confirm it. Follow the existing history's style (`feat:`, `fix:`, `docs:`, `build:`). No em dashes in the message: a hook blocks them in files, but not in commit messages, so this one is on you.

4. **Push to `main`. Never force push.**

   ```bash
   git push origin main
   ```

   This machine has no cached GitHub credentials and the remote URL deliberately carries no token, so a plain push often fails with `could not read Username for 'https://github.com'`. When it does, authenticate from the environment variable rather than putting a token on the command line or into the remote URL:

   ```bash
   git -c credential.helper='!f(){ echo username=triippiing; echo "password=$GITHUB_PERSONAL_ACCESS_TOKEN"; };f' push origin main
   ```

   `GITHUB_PERSONAL_ACCESS_TOKEN` comes from `~/.claude/settings.json`. **Never echo, print, or interpolate that variable anywhere its value would be displayed.** It lands in the session transcript if you do, which then needs scrubbing. Only ever reference it inside the helper above.

5. **Watch CI.** Pushing anything matching `**.html` or `scripts/build_index.py` fires `build-index.yml`, which regenerates `index.html` and `assets/js/nav-data.js` and commits them back with `[skip ci]`.

   **`gh` is not installed on this machine.** Do not call `gh run watch`. Use the API:

   ```bash
   curl -s -H "Authorization: Bearer $GITHUB_PERSONAL_ACCESS_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/triippiing/Wiki/actions/runs?per_page=3" \
   | python3 -c "
   import json,sys
   for r in json.load(sys.stdin).get('workflow_runs',[])[:3]:
       print(f\"{r['name']:26} {r['head_sha'][:7]} status={r['status']} conclusion={r['conclusion']}\")
   "
   ```

   Two workflows respond to a push: `Build index` and `pages build and deployment`. Wait for both to reach `completed`. On failure, fetch and show the failing job's log rather than summarising it.

6. **Pull any CI commit back down** so the local tree does not fall behind:
   ```bash
   git fetch origin && git log --oneline HEAD..origin/main
   git pull --ff-only
   ```
   If the index was already rebuilt locally before committing, CI finds no diff and makes no commit. That is the normal, quiet case.

7. **Confirm the deploy actually serves the new content.** A 200 is not proof: Pages serves the previous build until deployment finishes, so check the content, not just the status code.

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://triippiing.github.io/Wiki/
   ```

   Then verify something specific to this change is live, cache-busting the request:
   ```bash
   curl -s "https://triippiing.github.io/Wiki/?cb=$RANDOM" | grep -c '<some string from your change>'
   ```
   If the Pages run is still `in_progress`, say so and poll rather than reporting either success or failure.

Report what actually happened at each step. If CI failed, say so with the output. Do not describe the ship as complete until the workflow passed **and** the live site serves the new content.
