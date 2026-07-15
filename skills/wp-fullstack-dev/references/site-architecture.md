# Site architecture and component layering

One component owns each behavior. Duplication across a theme and a plugin is the primary source of patch-on-patch decay: copies diverge silently, hooks fire twice, and duplicated function definitions become fatal redeclarations the moment load conditions change.

## Ownership rules

- Behavior — bookings, payments, emails, REST, cron, validation — lives in a plugin. Themes own presentation only; switching themes must never change business behavior.
- Move code between components; never copy it. Delete the source in the same change that lands the destination.
- Exactly one component registers a given hook callback, defines a given function or constant, and writes a given option. Share values across components through filters or getter functions, not duplicate `define()`s.
- Coordinate components with checks that reflect real state (`function_exists`, `did_action`, versioned constants). Never ship a hardcoded stub (`return true;`) as an ownership handshake — the first person to make it conditional arms every duplicate downstream.
- Prefer named functions over closures for hooks that another component may need to `remove_filter`.

## Migration discipline

- A compatibility shim ("skip our copy if the other component is active") is a migration step, not an architecture. Give it a stated removal condition and delete it in the release that completes the migration.
- Never ship backup files, `error_log` dumps, or modules commented out in loaders. Delete dead code; version control remembers it.

## Verify

Run `python3 scripts/map-project.py` against a directory containing all of a site's custom components. The map emits a `Cross-component conflicts` section listing duplicate hook registrations, identical files, duplicated functions and constants, and contested option writes. Resolve every entry before release. `scripts/validate.sh` fails on shipped backup and debug artifacts.
