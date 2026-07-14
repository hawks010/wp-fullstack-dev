# Block development

Register blocks from `block.json`; use the current metadata schema and `apiVersion`. Keep editor and frontend behavior consistent.

- Define attributes, supports, scripts, styles, and render behavior in metadata.
- Use a static `save` implementation only when markup can safely remain in post content. Use `render.php` for dynamic output.
- Escape every dynamic value in PHP. Use `get_block_wrapper_attributes()` for wrapper classes and style supports.
- Build with `@wordpress/scripts` and commit production assets when the distributed plugin must work without Node.
- Use Inspector Controls for secondary settings and block controls for frequent contextual actions.
- Provide labels, keyboard access, useful placeholders, and editor error states.
- Deprecate old saved markup deliberately to prevent invalid-block errors.

Validate metadata, run the production build, insert/edit/save/reload the block, and verify frontend rendering. See `testing.md`.
