# WordPress Full-Stack Dev v3 — by Sonny x Inkfire

[![CI](https://github.com/hawks010/wp-fullstack-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/hawks010/wp-fullstack-dev/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/hawks010/wp-fullstack-dev)](https://github.com/hawks010/wp-fullstack-dev/releases)
[![MIT license](https://img.shields.io/github/license/hawks010/wp-fullstack-dev)](LICENSE)
[![WordPress](https://img.shields.io/badge/WordPress-full--stack-3858E9?logo=wordpress)](https://wordpress.org/)

An installable skill for Claude Code, Codex, and Custom GPTs that builds, modifies, debugs, audits, tests, and packages WordPress plugins, themes, blocks, React dashboards, REST APIs, WooCommerce extensions, multisite features, and WP-CLI commands — and catches the mistakes that turn a codebase into patch-on-patch decay before they ship.

v3 is a WordPress engineering Swiss Army knife: one skill invocation, automatic mode routing, focused specialist references, production-aware safety rules, reusable starters, and evidence-based validation. v3.6–3.9 add a static project mapper that goes beyond a single file tree: it audits an entire multi-component site (theme + plugin + plugin) for the failure modes that actually wreck WordPress builds — duplicate hook registrations, byte-identical files shipped by two components, functions or constants defined in more than one place (fatal redeclaration risk), contested option ownership, missing uninstall contracts, orphaned cron schedules, and parallel "-new"/"-old"/"-v2" implementations left to rot side by side. Paired with a root-cause-first debugging methodology and a headless browser audit for JS/React/CSS runtime errors, it is built to stop circular, guess-and-check fixing and give an agent (or a human) a real definition of "done."

## Install in Codex

Use Codex's plugin marketplace flow with this repository:

```text
codex plugin marketplace add hawks010/wp-fullstack-dev
```

Then install **WordPress Full-Stack Dev** from the plugin marketplace in Codex. If your Codex environment supports repository skill installation instead, point it at this repository and select `skills/wp-fullstack-dev`.

Invoke it explicitly with `$wp-fullstack-dev`, or describe a matching WordPress task and allow implicit routing:

```text
$wp-fullstack-dev scaffold a plugin named inventory-sync
$wp-fullstack-dev build a React stock dashboard with authenticated REST endpoints
$wp-fullstack-dev validate and package this plugin
$wp-fullstack-dev audit this WooCommerce extension without changing files
```

Codex can run the bundled scaffold, mapper, validator, detector, browser audit, and packager in its workspace. The basic workflow does not require the user to type terminal commands. Skills use natural-language prompts; this package does not depend on deprecated custom slash commands.

```text
$wp-fullstack-dev map this site's components and find layering conflicts
$wp-fullstack-dev debug this WordPress issue: find the root cause before fixing
```

## What ships

- Native plugin manifest: `.codex-plugin/plugin.json`
- Skill: `skills/wp-fullstack-dev/SKILL.md`
- Eleven focused engineering references, including systematic debugging and multi-component site architecture
- Interactive and argument-driven scaffold tool
- A static project mapper that indexes hooks, REST routes, blocks, database touchpoints, and JavaScript entry points for a single project, **plus a site-audit mode** that scans a directory of components and reports cross-component conflicts (duplicate hooks, identical files, duplicated functions/constants, contested option writes), lifecycle risks (missing uninstall contracts, orphaned cron schedules), and parallel/stale implementation trees
- A headless browser runtime audit (`scripts/browser-audit.mjs`) that surfaces console errors, uncaught exceptions, failed requests, and HTTP errors on live pages — real evidence for JS/React/CSS bugs
- Structural project detection (real API usage and hook registrations, not keyword mentions) so specialist routing stays correct even on codebases that scan for or discuss WordPress patterns
- Evidence-based validation covering PHP syntax, Composer, PHPCS, PHPStan, PHPUnit, npm build/lint/test, Playwright (opt-in), and shipping hygiene (rejects `.bak`, `error_log`, and other debug artifacts before packaging)
- Deployable ZIP packaging that excludes dev tooling and hygiene violations
- Plugin, dashboard, dynamic block, classic theme, block theme, WooCommerce, multisite, and WP-CLI starters
- Reusable GitHub Actions workflow and this repository's full matrix CI (41 automated tests across the mapper, scaffold, and validator)
- Separate Custom GPT instructions and knowledge package, kept in sync with the debugging and layering discipline above

## Why this repository exists

Most AI coding resources cover one narrow WordPress task, and most AI-built WordPress stacks eventually decay into patch-on-patch: the same behavior duplicated across a theme and a plugin, hardcoded "temporary" handshakes that never get revisited, debug artifacts shipped to production, and a fourth speculative fix stacked on three failed ones. This project combines architecture, secure implementation, React administration, Gutenberg, WooCommerce, multisite, WP-CLI, testing, packaging, and production-safe editing in one installable toolkit — and adds the structural checks and debugging discipline that catch that decay before it ships, not after a client calls about a broken checkout.

Every detection rule in this skill was earned against real multi-component WordPress builds, not written speculatively: the cross-component conflict audit, lifecycle-risk checks, and parallel-implementation detector were each added after finding the exact failure they now catch in a real theme/plugin stack, then verified against it before merging.

It is also a working demonstration of modern WordPress and AI-assisted engineering by [Sonny x Inkfire](https://github.com/hawks010): complete examples, executable tests, transparent safety rules, and reproducible release tooling rather than prompt-only claims.

## Scaffold behavior

Supported types: `plugin`, `dashboard`, `block`, `classic-theme`, `block-theme`, `woocommerce`, `multisite`, and `wpcli`.

Generated projects use the requested name, slug, text domain, namespace, and prefix. Author metadata is optional. **Sonny x Inkfire is never injected into generated client work unless requested.** Existing destinations are never overwritten.

## Custom GPT distribution

1. Copy `skills/wp-fullstack-dev/chatgpt/instructions.md` into the GPT Instructions field.
2. Upload `skills/wp-fullstack-dev/chatgpt/knowledge.md` as Knowledge.
3. Tell the GPT the WordPress outcome; it will select the smallest operating mode.

The Custom GPT package contains the same safety and standards guidance but cannot assume access to the Codex scripts.

## Validation truthfulness

The toolkit reports checks as passed, failed, or skipped with a reason. It does not present static review as a browser test, automated accessibility output as conformance, or unrun commands as successful.

## Community automation

Issues and pull requests are automation-first: structured forms, allowlisted AI classification, path labels, first-contributor guidance, dependency updates, CI, and inactivity cleanup reduce routine maintenance. AI never approves or merges contributor code. Public forks are independent and carry no support or endorsement commitment from this project.

## Repository map

```text
.codex-plugin/plugin.json
.agents/plugins/marketplace.json
skills/wp-fullstack-dev/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
├── assets/
└── chatgpt/
```

## Author and license

Created and maintained by [**Sonny x Inkfire**](https://github.com/hawks010). MIT licensed for commercial and personal use.
