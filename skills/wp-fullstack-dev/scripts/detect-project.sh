#!/usr/bin/env bash
# Project detector for the Sonny x Inkfire WordPress skill.
# @author Sonny x Inkfire
set -euo pipefail

target="${1:-.}"
cd "$target"

if [[ -f theme.json && -d templates ]]; then
  echo "block-theme"
elif [[ -f style.css ]] && grep -Eqi '^[[:space:]]*Theme Name:' style.css; then
  echo "classic-theme"
elif compgen -G "*/block.json" >/dev/null || [[ -f block.json ]] || [[ -f src/block.json ]]; then
  echo "block"
elif [[ -d wp-content && -f wp-config.php ]]; then
  echo "wordpress-site"
elif [[ -f package.json ]] && grep -Eq '"@wordpress/components"|"@wordpress/api-fetch"' package.json; then
  echo "dashboard-plugin"
elif rg -l --glob '*.php' '^[[:space:]]*\*[[:space:]]+Plugin Name:' . >/dev/null 2>&1; then
  echo "plugin"
else
  echo "unknown"
fi
