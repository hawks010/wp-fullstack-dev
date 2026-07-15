# Changelog

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
