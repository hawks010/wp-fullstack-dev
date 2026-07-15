#!/usr/bin/env bash
# Evidence-based validator for the Sonny x Inkfire WordPress skill.
# @author Sonny x Inkfire
set -uo pipefail

target="${1:-.}"
run_e2e="${RUN_E2E:-0}"
failures=0
cd "$target" || exit 2

run() {
  local label="$1"
  shift
  printf 'RUN  %s\n' "$label"
  if "$@"; then
    printf 'PASS %s\n' "$label"
  else
    printf 'FAIL %s\n' "$label"
    failures=$((failures + 1))
  fi
}

has_npm_script() {
  node -e 'const scripts = require("./package.json").scripts || {}; process.exit(scripts[process.argv[1]] ? 0 : 1)' "$1"
}

printf 'RUN  Shipping hygiene\n'
junk="$(find . \( -path ./vendor -o -path ./node_modules -o -path ./.git \) -prune -o -type f \
  \( -name '*.bak' -o -name '*.bak-*' -o -name '*.bak.*' -o -name '*~' -o -name '*.orig' -o -name '*.rej' \
     -o -name 'error_log' -o -name 'debug.log' -o -name '.DS_Store' -o -name 'Thumbs.db' \) -print)"
if [[ -z "$junk" ]]; then
  printf 'PASS Shipping hygiene\n'
else
  printf '%s\n' "$junk"
  printf 'FAIL Shipping hygiene: remove backup and debug artifacts before release\n'
  failures=$((failures + 1))
fi

if command -v php >/dev/null && [[ -n "$(find . -type f -name '*.php' -not -path './vendor/*' -print -quit)" ]]; then
  run "PHP syntax" bash -c 'find . -type f -name "*.php" -not -path "./vendor/*" -not -path "./node_modules/*" -print0 | xargs -0 -n1 php -l'
else
  echo "SKIP PHP syntax: PHP or PHP files unavailable"
fi

if [[ -f composer.json ]]; then
  if command -v composer >/dev/null; then
    run "Composer validation" composer validate --strict
  else
    echo "SKIP Composer validation: composer unavailable"
  fi
  if [[ -x vendor/bin/phpcs && ( -f phpcs.xml.dist || -f phpcs.xml ) ]]; then
    run "PHPCS" vendor/bin/phpcs
  else
    echo "SKIP PHPCS: installed binary or configuration unavailable"
  fi
  if [[ -x vendor/bin/phpunit && ( -f phpunit.xml.dist || -f phpunit.xml ) ]]; then
    run "PHPUnit" vendor/bin/phpunit
  else
    echo "SKIP PHPUnit: installed binary or configuration unavailable"
  fi
  if [[ -x vendor/bin/phpstan && ( -f phpstan.neon.dist || -f phpstan.neon ) ]]; then
    run "PHPStan" vendor/bin/phpstan analyse --no-progress
  else
    echo "SKIP PHPStan: installed binary or configuration unavailable"
  fi
fi

if [[ -f package.json ]]; then
  if ! command -v npm >/dev/null; then
    echo "SKIP JavaScript checks: npm unavailable"
  elif [[ ! -d node_modules ]]; then
    echo "SKIP JavaScript checks: dependencies are not installed"
  else
    if has_npm_script build; then
      run "JavaScript build" npm run build
    else
      echo "SKIP JavaScript build: no build script"
    fi
    if has_npm_script lint; then
      run "JavaScript lint" npm run lint
    elif has_npm_script lint:js; then
      run "JavaScript lint" npm run lint:js
    else
      echo "SKIP JavaScript lint: no lint script"
    fi
    if has_npm_script test; then
      run "Jest" npm test -- --runInBand
    else
      echo "SKIP Jest: no test script"
    fi
    if has_npm_script test:e2e; then
      if [[ "$run_e2e" == "1" ]]; then
        run "Playwright" npm run test:e2e
      else
        echo "SKIP Playwright: set RUN_E2E=1 with a disposable test environment"
      fi
    fi
  fi
fi

if (( failures > 0 )); then
  printf '%d validation check(s) failed.\n' "$failures"
  exit 1
fi
echo "Validation completed without failures. Review SKIP lines before release."
