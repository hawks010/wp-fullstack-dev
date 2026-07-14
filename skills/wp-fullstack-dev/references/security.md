# Security, internationalization, and accessibility

Apply controls at each trust boundary.

## Security

- Sanitize according to type: text, key, email, URL, integer, enum, HTML allowlist, or structured schema.
- Validate domain rules separately from sanitization. Reject invalid values instead of silently transforming security-sensitive inputs.
- Check capabilities before reading or mutating protected resources. Use nonces for state-changing admin, AJAX, and cookie-authenticated REST requests.
- Escape late with `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`, or the correct context. Use prepared SQL and allowlists for identifiers/order clauses.
- Protect uploads by MIME/type, size, permissions, storage path, and download authorization.
- Do not log credentials, nonces, personal data, or full payment payloads. Never commit secrets.

## Internationalization

Use one project text domain, translator comments for placeholders, numbered placeholders where word order can change, and plural APIs for counts. Do not concatenate translatable sentence fragments.

## Accessibility

Target WCAG 2.2 AA: semantic landmarks, one logical heading hierarchy, programmatic labels and instructions, keyboard-complete controls, visible focus, useful error identification, and contrast of at least 4.5:1 for normal text and 3:1 for large text and UI graphics where applicable.

Automated tools can identify likely issues; they cannot prove conformance. Verify keyboard journeys, focus order, 200% zoom/reflow, reduced motion, accessible names, status announcements, and representative screen-reader output. Report automated and manual evidence separately.
