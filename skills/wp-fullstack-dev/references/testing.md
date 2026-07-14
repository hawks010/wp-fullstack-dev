# Testing, validation, and release engineering

Choose the smallest test pyramid that proves the changed behavior.

- PHP: `php -l`, PHPCS with WordPress Coding Standards, PHPUnit, integration tests where WordPress behavior matters, and Plugin Check for distributable plugins.
- JavaScript: lint, production build, Jest/component tests, and dependency audit interpreted by runtime exposure.
- Blocks/themes: validate `block.json` and `theme.json`; test editor/save/reload/frontend behavior.
- Browser: Playwright for critical admin and frontend journeys at representative viewports. Run against a disposable WordPress environment.
- Accessibility: automated scanning plus manual keyboard, focus, zoom/reflow, and assistive-technology checks.

CI should pin supported PHP/Node versions, use lockfiles, cache safely, grant minimal permissions, and stop disposable environments in `always()` cleanup. Release ZIPs include runtime PHP, translations, readmes, and compiled production assets; exclude VCS data, tests, source maps unless needed, node_modules, vendor when not runtime-required, local config, and secrets.

Use `scripts/validate.sh` and state every skipped check with its reason. Use `scripts/package-plugin.sh` only after validation. Publishing, tagging, pushing, and deploying require explicit authorization.
