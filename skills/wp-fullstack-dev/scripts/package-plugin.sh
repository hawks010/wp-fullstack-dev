#!/usr/bin/env bash
# Deployable ZIP packager for the Sonny x Inkfire WordPress skill.
# @author Sonny x Inkfire
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 2; }

exec python3 "$script_dir/package-plugin.py" "$@"
