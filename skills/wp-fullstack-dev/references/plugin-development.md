# Plugin development

Use a thin bootstrap file and separate hook wiring, domain logic, persistence, presentation, and integrations. Prefix global symbols; prefer namespaces and Composer PSR-4 autoloading when the project already uses Composer. Keep activation, upgrade, deactivation, and uninstall responsibilities distinct.

## Lifecycle

- Activation establishes defaults, roles, rewrite rules, and schema. It must be idempotent.
- Store a schema version and run upgrades from normal plugin loading, not only activation.
- Use `dbDelta()` only after loading `wp-admin/includes/upgrade.php`; index lookup columns and never interpolate untrusted identifiers.
- Deactivation removes scheduled runtime state, not user content.
- Uninstall deletes data only when the plugin contract says it should; support a retain-data option when appropriate.

## Runtime

- Register hooks during bootstrap but defer dependency-specific work until the dependency is available.
- Scope frontend styles to a block, shortcode, widget, or detected render path. Scope admin assets with the screen hook.
- Use Settings, Metadata, Options, Transients, HTTP, Filesystem, Cron, and REST APIs instead of custom substitutes.
- Make hooks and filters stable extension points. Document parameters and return values.

See `security.md` for trust boundaries, `rest-api.md` for endpoints, and `testing.md` before release.
