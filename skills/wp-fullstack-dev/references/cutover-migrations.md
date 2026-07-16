# Staged cutovers and migrations

Use this mode when replacing, consolidating, or retiring WordPress behavior across themes, plugins, cron jobs, Action Scheduler jobs, data stores, or external integrations.

1. Map every component before editing. Inventory active and inactive plugins/themes, must-use plugins, drop-ins, scheduled hooks, Action Scheduler groups/actions, REST/AJAX entry points, shortcodes, blocks, options, custom tables, post types, webhooks, and external workers.
2. Assign one owner to each behavior and dataset. Record the old owner, new owner, migration path, compatibility window, rollback trigger, and removal condition.
3. Prove the backup. Require successful export/archive exit codes, non-empty expected files, an external checksum manifest, `sha256sum -c` (or platform equivalent), and an archive listing or restore spot-check. A command that merely printed a filename is not backup evidence.
4. Prefer shadow or read-only comparison before authority transfer. For orders, bookings, payments, inventory, or other financial truth, fail closed: never let two components write the same truth or silently fall back to an unverified implementation.
5. Cut over in stages: stop new writes at the old owner, migrate and reconcile data, enable the new owner, verify user journeys and background work, then remove old registrations and code. Preserve historical data unless deletion is explicitly authorized.
6. Verify after cutover: hooks, routes, shortcodes, blocks, admin navigation, capabilities, settings, schedules, queues, logs, public output, and rollback readiness. Re-run the project/site map and conflict audit.
7. Keep a temporary-artifact ledger. Remove test users, fixtures, API tokens, application passwords, temporary files, and debug switches; verify their absence and rotate credentials that may have been exposed.

Do not declare completion while old and new implementations remain active, scheduled work is orphaned, reconciliation differs, backup proof is missing, or rollback has not been defined.
