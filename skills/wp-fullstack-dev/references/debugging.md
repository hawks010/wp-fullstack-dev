# Systematic debugging

The iron law: **no fixes without root-cause investigation first.** Patch-on-patch decay starts the moment a symptom is treated before its cause is understood. Methodology adapted from obra/superpowers `systematic-debugging` and anthropics/skills `webapp-testing`.

## The four phases (in order, no skipping)

1. **Root cause.** Read the actual error message, stack trace, and line numbers. Reproduce the failure with documented steps before touching code. Check recent changes (`git log`, deployments). For multi-layer failures, instrument each boundary — PHP error log, REST response, browser console — to isolate which layer is lying.
2. **Pattern analysis.** Find working code in the same codebase that does the same job. Read it completely. List every difference between working and broken.
3. **Hypothesis.** Form one specific hypothesis and test it with the smallest possible change. If wrong, revert and form a new hypothesis — never stack a second speculative change on the first.
4. **Fix.** Write the failing test first, apply one targeted fix, verify the test passes and nothing else broke.

**Stop signs — halt immediately if you are:** proposing a fix before investigating; changing several things at once; saying "quick fix now, investigate later"; or on your **third failed fix attempt** — at three strikes the architecture is the suspect, not the line of code. Escalate to a design change instead of a fourth patch.

## Instrumentation per layer

- **PHP:** `WP_DEBUG` + `WP_DEBUG_LOG` on (staging), then read `wp-content/debug.log` — do not guess from a white screen. `wp plugin deactivate --all` then reactivate one at a time for conflict isolation (see `troubleshooting.md`). Query Monitor for hooks, queries, and capability checks. PHPStan (`vendor/bin/phpstan analyse`) catches type errors before runtime.
- **REST/AJAX:** curl the endpoint directly with and without auth; a browser-only diagnosis conflates frontend and backend failures.
- **JavaScript / React / CSS:** run `node scripts/browser-audit.mjs <url>` against the affected pages — it reports console errors and warnings, uncaught exceptions, failed requests, and HTTP 4xx/5xx responses. Reconnaissance before action: inspect the rendered DOM and captured logs first, then act on what is actually there, waiting for `networkidle` on dynamic pages. `SCRIPT_DEBUG` swaps minified WordPress bundles for readable ones.
- **Structure:** `map-project.py` before diving into files — most "mystery" behavior is a hook registered somewhere unexpected, and the map (or its `Cross-component conflicts` / `Lifecycle risks` sections) shows it.

## Evidence rules

- A bug is not fixed until the original reproduction passes and a regression test exists.
- Report what was observed, not what was intended: paste the failing output and the passing output.
- Absence of an error in one layer is not evidence of health — check the layer above and below.
