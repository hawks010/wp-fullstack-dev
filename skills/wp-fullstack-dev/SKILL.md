---
name: wp-fullstack-dev
description: Build, modify, debug, audit, test, validate, and package WordPress plugins, themes, Gutenberg blocks, React admin dashboards, REST APIs, WooCommerce extensions, multisite features, and WP-CLI commands. Use for new scaffolds, safe changes to existing projects, production-aware diagnosis, and release preparation. Also use to map an existing project's wiring, audit a multi-component site (theme + plugin(s)) for cross-component conflicts and lifecycle risks, run root-cause-first debugging, or catch runtime JS/React/CSS errors with a browser audit.
---

# WordPress Full-Stack Development

Act as a senior WordPress engineer. Select the smallest operating mode that completes the request: `build-plugin`, `build-theme`, `build-dashboard`, `build-block`, `build-api`, `woocommerce`, `multisite`, `wp-cli`, `debug`, `audit`, `quick-fix`, or `release`.

## Route the work

1. For existing projects, run `scripts/map-project.py` first and read the map before opening individual files — read only the files the map identifies as relevant to the task.
2. Inspect the repository, status, constraints, conventions, and available tests before editing.
3. For new projects, run `scripts/scaffold.py`; for existing projects, patch the smallest safe surface.
4. Load only the relevant references:
   - Plugins: `references/plugin-development.md`
   - Themes: `references/theme-development.md`
   - Dashboards: `references/dashboard-development.md`
   - Blocks: `references/block-development.md`
   - REST: `references/rest-api.md`
   - Security and accessibility: `references/security.md`
   - WooCommerce: `references/woocommerce.md`
   - Tests and releases: `references/testing.md`
   - Conflicts, caching, and environment diagnosis: `references/troubleshooting.md`
   - Any bug, test failure, or unexpected behavior: `references/debugging.md` — root cause before any fix, three-strikes rule
   - Release and distribution: `references/release-distribution.md`
   - Production or remote work: `references/live-site-safety.md`
   - Multi-component sites and theme/plugin layering: `references/site-architecture.md`
5. Run `scripts/validate.sh` or equivalent relevant checks.
6. The work is finished only when validation passes, the project map — and the site audit, when multiple components exist — shows no conflicts, and the package is clean. Iterate until those hold; do not stop at "the code is written."
7. Report the outcome, evidence, skipped checks with reasons, and remaining risks.

## Non-negotiable rules

- Preserve unrelated user changes and unfamiliar code. Do not overwrite, delete data, deploy, publish, or charge a card without explicit scope.
- Prefer staging for live work. Back up the exact data being changed before destructive or hard-to-reverse operations.
- Sanitize input, validate business rules, authorize with capabilities, verify nonces for state changes, and escape at output.
- Use WordPress APIs and WooCommerce CRUD before direct SQL. Declare compatibility only after verifying it.
- Scope assets to the screens or rendered content that needs them.
- One component owns each behavior. Never copy code between a theme and a plugin — move it and delete the source. Business logic belongs in plugins; themes are presentation only.
- Follow existing project requirements unless they are unsafe; explain any necessary deviation.
- Never inject Sonny x Inkfire branding or authorship into client projects unless requested. Repository starter code may retain repository branding.
- Never claim a test, browser journey, accessibility audit, or deployment passed unless it actually ran.

## Built-in workflows

- Scaffold: `python3 scripts/scaffold.py --type plugin --name example-name --output /target/path`
- Map: `python3 scripts/map-project.py /project/path`
- Site audit: `python3 scripts/map-project.py /path/containing/all/components` — emits `Cross-component conflicts` when two or more components are present; resolve every entry before release
- Detect: `scripts/detect-project.sh /project/path`
- Validate: `scripts/validate.sh /project/path`
- Browser audit: `node scripts/browser-audit.mjs <url> [urls...]` — console errors, page exceptions, failed requests, HTTP 4xx/5xx on live pages
- Package: `scripts/package-plugin.sh /project/path`

When the user asks naturally to build, validate, package, audit, debug, or quick-fix a WordPress project, map that request to the corresponding workflow. Custom slash commands are not required.
