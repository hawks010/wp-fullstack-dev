# Troubleshooting conflicts, caching, and environment issues

Before assuming the bug is in the code just written, rule out these three categories. Most "nightmare" WordPress issues live here, not in application logic.

## Plugin/theme conflicts

- Isolate with the standard bisection protocol: switch to a default theme and deactivate all other plugins; if the issue disappears, reactivate one at a time (theme first, then plugins alphabetically) until it reappears.
- Symptom mapping: a blank white screen or 500 is almost always a PHP fatal (check the host's PHP error log, not just `WP_DEBUG` display, since many hosts suppress on-screen errors); a broken admin layout or JS console error usually means a duplicate script handle, a jQuery/React version mismatch, or two plugins enqueuing conflicting block editor assets.
- Prefix every global function, class, constant, and option/transient key. Unprefixed or generically named symbols (`init()`, `Settings`, `MYPLUGIN`) are the most common source of fatal redeclaration errors when two plugins share a host.
- Check for duplicate `register_block_type()`, `register_rest_route()`, or `add_shortcode()` calls with the same identifier across active plugins; the second registration silently loses or throws, depending on the API.

## Caching and stale state

- Before debugging "my change isn't showing," rule out layered caching in this order: browser cache, CDN/edge cache (Cloudflare, host-level), page cache (WP Rocket, W3 Total Cache, host-level full-page cache), object cache (Redis/Memcached), then transients and `wp_cache_*` calls in the code itself.
- Transients and object cache entries do not expire just because the underlying data changed; any code that writes data the user expects to see immediately must explicitly delete or update the matching cache key in the same request.
- REST/AJAX responses that appear cached are frequently a page-cache or CDN rule catching `GET` requests to `/wp-json/*`; verify with cache-busting headers or a direct cURL bypassing the CDN before assuming a code bug.
- When in doubt, reproduce with all caching plugins deactivated and object cache disabled before attributing behavior to application code.

## Hosting environment variance

- Never assume `exec()`, `shell_exec()`, `proc_open()`, direct file writes to the plugin/theme directory, or `wp-config.php` edits are available; many managed hosts disable or block these. Detect capability before relying on it and degrade gracefully.
- PHP version, memory limit, `max_execution_time`, and disabled-function lists vary by host and by environment (staging vs. production) even for the same site. Do not hardcode assumptions from local development (`wp-env`, Local, Docker) into production-facing code.
- Multisite subdirectory vs. subdomain installs, and reverse-proxy/CDN setups that rewrite `HTTPS` detection, commonly break URL generation and cookie-based auth in ways that only appear on the live host. Verify `home_url()`/`site_url()` output on the actual target environment, not just locally.
- If a fix can't be verified because the sandbox lacks a capability the live host has (or vice versa), say so explicitly rather than presenting untested behavior as verified.

## `dbDelta()` formatting gotchas

- `dbDelta()` parses the `CREATE TABLE` string with strict formatting rules: each field and key on its own line, two spaces between `PRIMARY KEY` and the parenthesized column list, and no trailing comments on definition lines. Deviating from this causes silent no-ops, not errors — the schema simply never updates.
- Always compare `get_option( '{prefix}_db_version' )` against the code's current version and re-run `dbDelta()` on every relevant load, not only on activation, so upgrades reach sites that update the plugin without deactivating it.

See `plugin-development.md` for lifecycle/versioning, `live-site-safety.md` for the broader production-safety protocol this feeds into, and `map-project.py` (`scripts/map-project.py`) to locate conflicting registrations quickly instead of grepping the whole tree.
