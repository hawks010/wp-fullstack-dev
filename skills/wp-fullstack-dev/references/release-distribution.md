# Release and distribution

Packaging (`scripts/package-plugin.sh`) produces the ZIP; this covers what happens after.

## WordPress.org SVN

- The `readme.txt` (not `README.md`) is the source of truth for the .org listing: `Stable tag`, `Requires at least`, `Tested up to`, `Requires PHP`, and a `== Changelog ==` section in WordPress.org's expected format. Keep it in sync with `CHANGELOG.md`; .org never reads the Markdown file.
- SVN layout: `trunk/` holds the current development code, `tags/x.y.z/` holds immutable released versions, `assets/` (banner, icon, screenshots) sits at the repository root and is never included in the shipped ZIP.
- Deploy flow: commit changes to `trunk/`, then `svn cp` trunk into a new `tags/x.y.z/` for the release. Never edit an existing tag after publishing it — cut a new version instead.
- `Stable tag` in `readme.txt` controls what users download; bumping trunk without bumping `Stable tag` (or vice versa) ships the wrong code to end users.

## Self-hosted and premium updates

- Plugins distributed outside WordPress.org need their own update channel: hook `pre_set_site_transient_update_plugins` to inject a remote version check, and `plugins_api` to supply changelog/details data for the update screen.
- License-gated updates (EDD, Freemius, or a custom licensing server) must validate the license key server-side before serving the update payload; client-side-only checks are not a security boundary.
- Version comparisons for the update check must use the same version constant the plugin bootstraps with (see `plugin-development.md` schema-version pattern) to avoid the update mechanism and the runtime disagreeing about the installed version.

## Versioning discipline

- Follow semantic versioning: patch for fixes, minor for backward-compatible features, major for breaking changes to hooks, filters, REST contracts, or stored data shape.
- Every schema or stored-option shape change ships with an upgrade routine keyed off the version constant, not just a changelog note — see `troubleshooting.md` for `dbDelta()` formatting gotchas that cause silent upgrade failures.
