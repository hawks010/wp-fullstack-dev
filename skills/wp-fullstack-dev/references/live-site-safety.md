# Live-site safety

Treat every remote site as production unless the user identifies a disposable environment.

1. Confirm the exact site, environment, WordPress root, active theme/plugin, and requested scope.
2. Reproduce read-only first. Capture relevant versions, logs, browser evidence, timezone, caches, and stored data.
3. Prefer staging. Before a live mutation, back up the exact database rows, options, post meta, files, or configuration being touched. Prove the backup with successful exit codes, non-empty expected files, an external checksum manifest and checksum verification, plus an archive listing or restore spot-check. A filename alone is not evidence.
4. Use a minimal reversible patch. Avoid bulk replacement, destructive SQL, plugin/theme auto-updates, real payment activity, and cache purges outside scope.
5. Verify both stored state and rendered behavior. Builder previews and database values alone are insufficient for public UI issues.
6. Record commands, changed files/data, rollback path, cache actions, and verification evidence without exposing credentials. Never place secrets in URLs or logged command arguments; prefer protected credential files, environment injection, or standard input, redact output, and rotate anything exposed.
7. Track every temporary user, fixture, token, application password, file, and debug switch. Remove it after verification and confirm removal rather than assuming cleanup ran.

For Elementor or similar builder data, preserve valid JSON and back up metadata first. For WooCommerce, account for site timezone, order status, refunds, HPOS, and asynchronous jobs. Stop and request authority before any materially broader or irreversible action.
