# Changelog

## [3.9.1] - 2026-07-15
### Changed
- Synced descriptions across surfaces with the v3.6–3.9 capability set ahead of merging to `main`: `SKILL.md` frontmatter (used for routing), `README.md` (install instructions, "What ships", "Why this repository exists"), and `.agents/plugins/marketplace.json` now describe the site-audit mapper, lifecycle-risk detection, parallel-implementation detection, debugging methodology, and browser runtime audit.
- `.codex-plugin/plugin.json` version corrected to 3.9.0 (had drifted behind two feature releases).

## [3.9.0] - 2026-07-15
### Fixed
- `scripts/detect-project.sh` now requires structural evidence instead of word mentions: WooCommerce classification needs real API usage (`before_woocommerce_init`, `declare_compatibility`, `extends WC_`, `wc_get_*()`, or hooking a `woocommerce_*` hook), and multisite needs real calls (`switch_to_blog()`, `get_sites()`, `add_site_option`, `network_admin_menu`, or a `Network: true` header). Plugins that merely *mention* those words — compatibility scanners listing them as patterns — no longer misclassify.

### Added
- `scripts/map-project.py` `Parallel implementations` section: flags sibling files or directories that differ only by a staleness token (`admin/` vs `admin-new/`, `functions.php` vs `functions-old.php`, `-legacy`, `-backup`, `-v2`, …) — patch-on-patch inside a single component, where two implementations coexist with no single owner.

### Tests
- Detector regression for scanner-vocabulary mentions; parallel-tree detection positive and false-positive cases.

## [3.8.0] - 2026-07-15
### Fixed
- `scripts/map-project.py` is now comment-aware: PHP/JS comments are blanked (offset-preserving) before scanning. Previously an apostrophe inside a docblock ("don't") opened a phantom string that desynced class-body extraction — silently downgrading constant-based REST routes to `<unresolved:>` — and commented-out `add_action`/`add_shortcode`/`update_option` lines were indexed as live registrations. Plugin/theme headers (which live in comments) and file hashing still use the original text; PHP `#[Attribute]` syntax is preserved.

### Added
- `references/rest-api.md`: deliberately-public endpoint rules — `__return_true` is acceptable only with a real in-handler gate (hashed bearer token, signed expiring URL, or provider signature), upload endpoints need type/size allowlists, and every `permission_callback: __return_true` row in a project map is a named review obligation.

### Tests
- Three comment-handling regressions: docblock-apostrophe constant resolution, commented-out calls excluded from the map, and slashes inside string literals preserved.

## [3.7.1] - 2026-07-15
### Changed
- Synced all three platform surfaces with the v3.6–3.7 capabilities. Claude Code and Codex share `SKILL.md` and the scripts directly; the ChatGPT Custom GPT surface cannot run scripts, so the debugging methodology (iron law, four phases, stop signs, three-strikes rule) and the component-ownership/layering/hygiene rules are now written into `chatgpt/instructions.md` and `chatgpt/knowledge.md` (new sections 16–17) as manual procedure.
- `.codex-plugin/plugin.json` bumped to 3.7.0 with the mapper, site audit, debugging, and browser-audit capabilities described, plus debug and site-audit default prompts.

## [3.7.0] - 2026-07-15
### Added
- `references/debugging.md`: systematic debugging methodology — root cause before any fix, four mandatory phases, stop signs, and a three-strikes rule (three failed fixes means the architecture is the suspect). Includes per-layer instrumentation guidance for PHP (`WP_DEBUG_LOG`, Query Monitor, PHPStan), REST/AJAX (direct curl), JavaScript/React/CSS (browser audit, reconnaissance-then-action), and structure (the project map). Adapted from obra/superpowers `systematic-debugging` and anthropics/skills `webapp-testing`.
- `scripts/browser-audit.mjs`: loads pages headlessly via Playwright and reports console errors and warnings, uncaught page exceptions, failed requests, and HTTP 4xx/5xx responses per URL — runtime evidence for JS/React/CSS debugging with PASS/FAIL per page.
- `scripts/map-project.py` `Lifecycle risks` section: flags plugins that persist options or custom tables without any `uninstall.php`/`register_uninstall_hook` (the uninstall contract must be an explicit decision), and plugins that schedule cron/Action Scheduler events without any unschedule call anywhere.
- `scripts/validate.sh` now runs PHPStan when `vendor/bin/phpstan` and a `phpstan.neon(.dist)` config are present.

### Changed
- `SKILL.md`: debugging reference wired into routing for any bug or unexpected behavior; browser-audit workflow added.

## [3.6.0] - 2026-07-15
### Added
- `scripts/map-project.py` site-audit mode: pointing the mapper at a directory containing two or more components (plugins/themes) now emits a `Cross-component conflicts` section reporting duplicate hook registrations (same hook and callback in more than one component), byte-identical files shipped by multiple components, functions and constants defined in more than one component (fatal-redeclaration and drift risk), and options written by more than one component (contested ownership). A clean site states "None detected" explicitly rather than staying silent.
- `scripts/validate.sh` shipping-hygiene gate: validation now fails, naming each artifact, when a project ships backup files (`*.bak`, `*.bak-*`, `*~`, `*.orig`, `*.rej`), `error_log`/`debug.log` dumps, or OS litter (`.DS_Store`, `Thumbs.db`); dependency directories are exempt.
- `references/site-architecture.md`: ownership rules for multi-component sites — behavior lives in plugins, themes are presentation-only, move-don't-copy, one owner per hook/function/constant/option, real capability checks instead of hardcoded ownership stubs, and migration-shim removal discipline.
- `scripts/test_validate.py` covering the hygiene gate, wired into CI.

### Changed
- `SKILL.md`: new site-audit workflow entry, a one-owner-per-behavior non-negotiable rule, the site-architecture reference in routing, and an explicit definition of done — validation passing, a conflict-free map/site audit, and a clean package — to anchor iterate-until-finished loops.
- `scripts/package-plugin.sh` now excludes backup and debug artifacts from release archives.

## [3.5.2] - 2026-07-15
### Fixed
- `scripts/map-project.py`: REST `methods` and `permission_callback` are now read from each route's own argument array instead of a fixed 15-line window, so an unprotected route can no longer inherit a neighboring route's permission callback or HTTP methods — previously an open endpoint within 15 lines of a protected one was reported as protected (a security false negative for anyone auditing route protection from the map).
- `scripts/map-project.py`: a `methods` value that ends its array without a trailing comma no longer captures the closing `) );` as literal text (`'GET' ) );` → `'GET'`), via a bracket/quote-aware value extractor shared with `permission_callback`.
- `scripts/map-project.py`: class constants used in REST route arguments now resolve per class body rather than file-wide first-wins, so two classes in one file sharing a constant name (e.g. both defining `NS`) each resolve to their own value instead of the first class's.
- `scripts/map-project.py`: `register_block_type()` dynamic detection now inspects only that call's own arguments, so a static block registered near a dynamic one is no longer mislabeled `dynamic: yes`.

### Tests
- Four regressions covering each fix: adjacent-route metadata isolation, per-class constant resolution, trailing `methods` value capture, and static-vs-dynamic block adjacency.

## [3.5.1] - 2026-07-15
### Fixed
- `scripts/map-project.py`: REST routes registered with a class constant namespace or route (e.g. `register_rest_route( self::NAMESPACE, '/settings', … )`) are now indexed instead of silently dropped. The mapper resolves same-file string class constants for `self::NAME`/`ClassName::NAME` references, and any argument it still cannot resolve is emitted with an `<unresolved: …>` marker rather than omitting the route entirely — an empty section no longer reads as "no REST routes here". This restores the `## REST routes` section for the bundled `dashboard-plugin-starter`, whose controller uses `self::NAMESPACE` for all three endpoints.

### Tests
- Added a regression test that maps the real `assets/dashboard-plugin-starter` (not a synthetic fixture) and asserts its three `myapp/v1/*` routes are indexed, plus a test that an unresolvable route argument produces a marked row instead of being dropped.

## [3.5.0] - 2026-07-15
### Added
- `references/troubleshooting.md` covering plugin/theme conflict isolation, caching and stale-state diagnosis, hosting environment variance, and `dbDelta()` formatting gotchas.
- `references/release-distribution.md` covering WordPress.org SVN deployment, `readme.txt` conventions, self-hosted/premium update mechanisms, and versioning discipline.
- Cart/Checkout blocks extension guidance in `references/woocommerce.md`, alongside the existing HPOS coverage.
- `scripts/map-project.py`: a dependency-free static project mapper that indexes files, hooks (registered/fired/cross-referenced hook graph), REST routes, post types/taxonomies, blocks, shortcodes, WP-CLI commands, and database touchpoints, so an agent can orient itself in an unfamiliar project by reading one compact map instead of the full tree.
- `scripts/test_map_project.py` regression coverage for the mapper, wired into CI.

### Changed
- `SKILL.md` routing now runs the project map before individual-file inspection on existing projects, and lists the two new references.

## [3.0.4] - 2026-07-15
### Fixed
- Prioritized the dashboard dependency signature before broad PHP-content checks so HPOS compatibility declarations do not misclassify dashboard plugins as WooCommerce extensions.

### Tests
- Added a regression check that detects the shipped HPOS-compatible dashboard starter as `dashboard-plugin`.

## [3.0.3] - 2026-07-15
### Fixed
- Removed scaffold identity leaks from Composer vendors, block namespaces, shortcode tags, dashboard globals, compiled bundles, and generated filenames.
- Renamed generated translation templates and WP-CLI include files alongside their rewritten references.
- Rebuilt npm assets after dependency installation when a starter declares a build script.
- Added WooCommerce, multisite, and WP-CLI project detection with a dependency-free grep fallback.

### Tests
- Scaffold all eight project types and scan every generated path and file for stale starter identities.
- Verify Composer identities, block source/build parity, dashboard bridge globals, POT filenames, WP-CLI paths, specialist routing, and operation without ripgrep.

## [3.0.2] - 2026-07-15
### Fixed
- Made the WordPress login E2E selector unambiguous for current Playwright strict-mode behavior.

## [3.0.1] - 2026-07-15
### Fixed
- Locked Composer dependencies for the PHP 8.2 CI baseline so plugin and dashboard starter tests install reproducibly.

## [3.0.0] - 2026-07-15
### Added
- Installable Codex plugin manifest and repository marketplace metadata.
- Compact native skill with natural-language mode routing and Codex UI starter prompts.
- Split references for plugins, themes, dashboards, blocks, REST, security/accessibility, WooCommerce, testing, and live-site safety.
- Interactive scaffold supporting eight WordPress project types without forced client branding.
- Project detection, evidence-based validation, deployable ZIP packaging, and forward tests for scaffolding safety.
- Reusable starter assets and GitHub Actions workflow under the skill package.
- Dedicated Custom GPT instructions and knowledge distribution.
- Discovery-ready GitHub presentation under the concise `wp-fullstack-dev` repository name.
- Low-maintenance community governance with structured issues, safe AI classification, PR labeling, stale cleanup, Dependabot, support boundaries, and coding-agent instructions.

### Changed
- Migrated all root examples into starter assets consumed by the scaffold.
- Updated CI to validate the native plugin, skill tooling, and migrated examples.
- Replaced unsupported command-frontmatter and deprecated slash-command assumptions with explicit `$wp-fullstack-dev` and natural-language workflows.
- Release packaging retains compiled production assets while excluding development-only files and dependencies.

## [2.1.0] - 2026-07-15
### Added
- Complete React dashboard plugin with authenticated REST settings and item CRUD endpoints.
- Jest, WP_Mock, Brain Monkey, PHPUnit, and Playwright examples.
- Dynamic Gutenberg block with committed production build assets.
- Block theme, WooCommerce HPOS extension, multisite lifecycle, and WP-CLI examples.
- Matrix-based GitHub Actions pipeline for PHP, JavaScript, and browser validation.
- Native Codex `wp-fullstack-dev/SKILL.md` with operating modes and evidence-based verification.

### Changed
- Basic plugin now exposes a shortcode and conditionally enqueues its stylesheet.
- Skill instructions now preserve existing work, separate operating modes, and require real test evidence.
- Sonny x Inkfire branding remains in repository examples but is no longer forced into client output.

## [2.0.0] - 2026-07-14
### Added
- Full block development standards (block.json, dynamic blocks, @wordpress/scripts)
- Advanced REST API best practices (permissions, validation, versioning)
- Performance audit pass (transients, object caching, asset conditioning)
- CI/CD pipeline sample (GitHub Actions with PHPCS, Jest, PHPUnit, Playwright)
- Multisite compatibility guidelines (network activation, per‑site cleanup)
- Code documentation requirements (phpDoc, auto‑README)
- Design patterns for scalable plugins
- Expanded knowledge base with all new sections
- Branding as Sonny x Inkfire across all generated code and documentation
- New passes in the agentic loop: Performance, Documentation, Block & REST API audit

## [1.0.0] - 2026-07-14
### Added
- Initial release with agentic plugin development, child theme support, accessibility (WAVE) audit, visual passes.
