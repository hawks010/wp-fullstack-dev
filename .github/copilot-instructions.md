# Repository instructions for coding agents

This repository distributes the `wp-fullstack-dev` Codex plugin and Custom GPT package. Preserve the native plugin layout: `.codex-plugin/plugin.json` points to `skills/`, and the primary skill is `skills/wp-fullstack-dev/SKILL.md`.

- Read the relevant reference under `skills/wp-fullstack-dev/references/` before changing a starter.
- Treat starter files as repository examples authored by Sonny x Inkfire, but never force that authorship into scaffolded client output.
- Keep the scaffold non-destructive. It must refuse existing destinations and avoid copying `vendor` or `node_modules`.
- Keep workflow permissions minimal. Fork-triggered workflows must not receive secrets or write access.
- Never let issue, comment, or pull-request text become executable shell, code, file paths, labels, or model-authored repository content without a strict allowlist.
- Do not auto-approve or auto-merge contributor code.
- Run the plugin and skill validators, scaffold forward tests, PHP checks, JavaScript builds/tests, and Playwright discovery as relevant.
- Report skipped checks honestly.
