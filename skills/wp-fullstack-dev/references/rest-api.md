# REST API development

Use a versioned namespace such as `vendor/v1` and a controller class for non-trivial APIs. Register routes on `rest_api_init`.

- Every route needs an explicit `permission_callback`. Use capabilities or resource ownership; never rely on authentication alone.
- Describe arguments in the route schema. Use `sanitize_callback` for normalization and `validate_callback` for admissibility.
- Treat nonce validation as CSRF protection for cookie-authenticated requests, not as authorization.
- Return `WP_REST_Response`, `WP_Error`, or `rest_ensure_response()`. Use meaningful HTTP statuses and stable error codes.
- Enforce pagination and bounded limits on collections. Avoid returning secrets, internal paths, or unnecessary user data.
- For writes, validate the complete business operation before mutation and make retries safe where feasible.
- Add schema and permission tests for anonymous, unauthorized, malformed, valid, and missing-resource cases.

## Deliberately public endpoints

Some flows are legitimately anonymous (intake forms, unsubscribe links, webhooks). `permission_callback => '__return_true'` is acceptable only when the handler itself enforces a real gate: a hashed bearer token verified with `wp_check_password()`/`hash_equals()`, a signed expiring URL, or a provider signature. Upload endpoints additionally need server-side type/size allowlists and isolated storage. In a project map, every `permission_callback: __return_true` row is a review obligation — confirm the in-handler gate exists and name it in the audit report; never wave one through because "the form is public."

Sanitize on input, authorize before use, and escape in the eventual rendering context. See `security.md`.
