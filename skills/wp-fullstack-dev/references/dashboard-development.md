# Dashboard development

Build WordPress-native admin applications: PHP owns menu registration, permissions, configuration, and asset loading; React owns interaction; REST owns data boundaries.

- Register the menu with the least privileged capability that matches the action.
- When attaching beneath a third-party parent menu, register after that parent (use a later `admin_menu` priority when necessary), use its real parent slug, and verify the submenu is visible in navigation. A direct `admin.php?page=...` URL loading successfully does not prove discoverability.
- Enqueue only on the page's exact `$hook_suffix`. Use the generated `*.asset.php` dependency/version metadata.
- Pass only bootstrap data that cannot be fetched safely; use `wp_add_inline_script()` or a namespaced object and escape JSON correctly.
- Use `@wordpress/components`, `@wordpress/element`, `@wordpress/api-fetch`, and `@wordpress/i18n`.
- Install nonce middleware once. REST capability checks remain mandatory; a nonce is not authorization.
- Model loading, empty, success, validation, error, and retry states. Keep notices announced and focus predictable after modals close.
- Split components by responsibility and test behavior rather than implementation details.

See `rest-api.md` for controller design and `security.md` for capability, nonce, output, and accessibility rules.
