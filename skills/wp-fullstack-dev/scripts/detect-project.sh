#!/usr/bin/env bash
# Project detector for the Sonny x Inkfire WordPress skill.
# @author Sonny x Inkfire
set -euo pipefail

target="${1:-.}"
cd "$target"

search_php() {
  local pattern="$1"
  local file

  if command -v rg >/dev/null 2>&1; then
    rg -l --glob '*.php' --glob '!vendor/**' --glob '!node_modules/**' --glob '!build/**' -- "$pattern" . >/dev/null 2>&1
    return
  fi

  while IFS= read -r -d '' file; do
    if grep -Eq -- "$pattern" "$file"; then
      return 0
    fi
  done < <(find . -type d \( -name vendor -o -name node_modules -o -name build \) -prune -o -type f -name '*.php' -print0)

  return 1
}

has_plugin_header() {
  search_php '^[[:space:]]*\*[[:space:]]+Plugin Name:'
}

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
elif has_plugin_header && search_php 'before_woocommerce_init|declare_compatibility|extends[[:space:]]+WC_|new[[:space:]]+WC_|WC\(\)->|wc_get_[a-z_]+\(|add_(action|filter)\([[:space:]]*.woocommerce_'; then
  echo "woocommerce"
elif has_plugin_header && search_php 'switch_to_blog[[:space:]]*\(|restore_current_blog[[:space:]]*\(|get_sites[[:space:]]*\(|add_site_option|network_admin_menu|Network:[[:space:]]*true'; then
  echo "multisite"
elif has_plugin_header && search_php 'WP_CLI::add_command|WP_CLI_Command'; then
  echo "wp-cli"
elif has_plugin_header; then
  echo "plugin"
else
  echo "unknown"
fi
