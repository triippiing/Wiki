#!/usr/bin/env bash
# Serve the wiki over http:// so runbook pages can load the shared CSS
# under assets/css/. Opening runbooks directly via Finder uses file://,
# and Safari blocks cross-directory resource loads under that scheme.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8765}"
echo "Serving Wiki at http://localhost:${PORT}/"
python3 -m http.server "$PORT"
