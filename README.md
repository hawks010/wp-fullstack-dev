# WordPress Full-Stack Dev v3 — by Sonny x Inkfire

[![CI](https://github.com/hawks010/wp-fullstack-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/hawks010/wp-fullstack-dev/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/hawks010/wp-fullstack-dev)](https://github.com/hawks010/wp-fullstack-dev/releases)
[![MIT license](https://img.shields.io/github/license/hawks010/wp-fullstack-dev)](LICENSE)
[![WordPress](https://img.shields.io/badge/WordPress-full--stack-3858E9?logo=wordpress)](https://wordpress.org/)

An installable Codex plugin and Custom GPT package for building, modifying, debugging, auditing, testing, and packaging WordPress plugins, themes, blocks, React dashboards, REST APIs, WooCommerce extensions, multisite features, and WP-CLI commands.

v3 is designed as a WordPress engineering Swiss Army knife: one skill invocation, automatic mode routing, focused specialist references, production-aware safety rules, reusable starters, and evidence-based validation.

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

Codex can run the bundled scaffold, validator, detector, and packager in its workspace. The basic workflow does not require the user to type terminal commands. Skills use natural-language prompts; this package does not depend on deprecated custom slash commands.

## What ships

- Native plugin manifest: `.codex-plugin/plugin.json`
- Skill: `skills/wp-fullstack-dev/SKILL.md`
- Nine focused engineering references
- Interactive and argument-driven scaffold tool
- Project detection, evidence-based validation, and deployable ZIP packaging
- Plugin, dashboard, dynamic block, classic theme, block theme, WooCommerce, multisite, and WP-CLI starters
- Reusable GitHub Actions workflow and this repository's full matrix CI
- Separate Custom GPT instructions and knowledge package

## Why this repository exists

Most AI coding resources cover one narrow WordPress task. This project combines architecture, secure implementation, React administration, Gutenberg, WooCommerce, multisite, WP-CLI, testing, packaging, and production-safe editing in one installable toolkit.

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
