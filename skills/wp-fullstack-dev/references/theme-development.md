# Theme development

Identify classic, child, hybrid, or block theme before editing. Do not put portable business logic in a theme.

## Classic and child themes

- Include a valid `style.css` header. A child theme's `Template` must exactly match the parent directory.
- Enqueue parent and child styles with explicit dependencies and file-based versions where useful; never use raw `<link>` tags in templates.
- Escape template output and use template parts rather than duplicating markup.
- Register menus, image sizes, editor styles, and theme supports from `after_setup_theme`.

## Block themes

- Treat `theme.json` as the design-system source for settings, styles, palettes, typography, spacing, and layout.
- Keep templates in `templates/`, parts in `parts/`, and patterns in `patterns/`.
- Validate JSON and confirm templates in both Site Editor and frontend.
- Avoid CSS that fights generated block styles; prefer presets and block-level rules.

Verify keyboard order, landmarks, heading hierarchy, zoom/reflow, contrast, and responsive behavior. See `security.md` and `testing.md`.
