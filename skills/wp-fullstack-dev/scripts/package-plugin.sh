#!/usr/bin/env bash
# Deployable ZIP packager for the Sonny x Inkfire WordPress skill.
# @author Sonny x Inkfire
set -euo pipefail

target="${1:-.}"
target="$(cd "$target" && pwd)"
slug="$(basename "$target")"
output="${2:-$(dirname "$target")/dist}"
mkdir -p "$output"
archive="$output/$slug.zip"
rm -f "$archive"

command -v zip >/dev/null || { echo "zip is required" >&2; exit 2; }

cd "$(dirname "$target")"
zip -rq "$archive" "$slug" \
  -x "$slug/.git/*" "$slug/.github/*" "$slug/.wp-env.json" \
     "$slug/node_modules/*" "$slug/vendor/*" "$slug/tests/*" "$slug/e2e/*" \
     "$slug/src/*" "$slug/test-results/*" "$slug/playwright-report/*" \
     "$slug/phpunit.xml*" "$slug/phpcs.xml*" "$slug/playwright.config.*" \
     "$slug/package-lock.json" "$slug/composer.lock" "$slug/*.log" \
     "$slug/*.bak" "$slug/*.bak-*" "$slug/*.bak.*" "$slug/*~" "$slug/*.orig" "$slug/*.rej" \
     "$slug/*error_log" "$slug/*.DS_Store" "$slug/*Thumbs.db"

echo "Created $archive"
