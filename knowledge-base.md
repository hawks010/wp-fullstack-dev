# WordPress Full‑Stack Development – Standards & Reference (2026 Edition)

## 1. PHP & Architecture
- PHP 8.2+ with `declare(strict_types=1);`.
- PSR‑4 autoloading (Composer or custom); no manual `require_once`.
- Plugin namespace root: `MyPlugin`.
- Child themes: `Template: parent-theme-folder` in `style.css`, enqueue parent and child styles.

## 2. Theme Development
- **Child Themes**:  
  ```php
  add_action( 'wp_enqueue_scripts', function () {
      wp_enqueue_style( 'parent-style', get_template_directory_uri() . '/style.css' );
      wp_enqueue_style( 'child-style', get_stylesheet_directory_uri() . '/style.css', [ 'parent-style' ] );
  } );
  ```
- **Block Themes**:  
  - Use `theme.json` for settings and styles.  
  - Templates are HTML files in `/templates` and `/parts`.  
  - Declare support: `add_theme_support( 'wp-block-styles' );`

## 3. React & Admin Interfaces
- Use `@wordpress/scripts` for build process: `wp-scripts start`, `wp-scripts build`.
- Admin pages:  
  ```php
  add_menu_page( __( 'My Page', 'textdomain' ), __( 'My Page', 'textdomain' ), 'manage_options', 'my-page', 'render_app', 'dashicons-admin-generic', 30 );
  function render_app() {
      echo '<div id="my-app"></div>';
      wp_enqueue_script( 'my-script', plugins_url( 'build/index.js', __FILE__ ), [ 'wp-element', 'wp-components', 'wp-api-fetch' ], '1.0.0', true );
  }
  ```
- Component structure: break into `App.js`, `components/Header.js`, `components/SettingsPanel.js` etc.
- Use `@wordpress/api-fetch` for REST API calls; set nonce:  
  ```js
  wp.apiFetch.use( wp.apiFetch.createNonceMiddleware( wpApiSettings.nonce ) );
  ```

## 4. Accessibility (WAVE Standards)
- **Color Contrast**: normal text ≥ 4.5:1, large text ≥ 3:1.
- **Semantic HTML**: use `<header>`, `<main>`, `<nav>`, `<footer>`, proper headings (h1–h6), `<label>` for inputs.
- **ARIA**: `aria-label` where visible text is absent, `role` attributes sparingly (use native HTML first).
- **Focus Management**: visible `:focus` styles, tabindex not used to override native order.
- **Alt Text**: all informative images must have `alt` attributes; decorative images can have `alt=""`.
- **Forms**: error messages linked to fields with `aria-describedby`.

## 5. WAVE Audit Procedure (Agent Simulation)
1. Scan for missing `alt`, empty links, form labels.
2. Check heading order: no skipped levels.
3. Verify color contrast with known safe combos (black/white, dark grey/white, etc.).
4. Test with a simulated screen reader: all interactive elements should have accessible names.

## 6. WooCommerce Compatibility
- Declare HPOS:  
  ```php
  add_action( 'before_woocommerce_init', function() {
      if ( class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
          \Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'custom_order_tables', __FILE__, true );
      }
  } );
  ```
- Use CRUD methods instead of post meta.

## 7. Database Versioning (`dbDelta`)
- Define `MYPLUGIN_VERSION` and compare with `get_option( 'myplugin_version' )`.
- In upgrade routine: `require_once ABSPATH . 'wp-admin/includes/upgrade.php';` then `dbDelta( $sql );`.
- `uninstall.php` removes custom tables and the version option.

## 8. Security & i18n Checklist
- Sanitization: `sanitize_text_field()`, `absint()`, `wc_clean()`, `rest_sanitize_*`.
- Escaping: `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses()`.
- Nonces: `wp_nonce_field()`, `check_admin_referer()`, `wp_verify_nonce()` for all forms/AJAX.
- Text domain for all strings; load plugin/theme textdomain early.

## 9. Block Development (Gutenberg)
- Use `block.json` for block registration (metadata, attributes, supports, editor/ style handles).
- Dynamic blocks: register with `register_block_type( __DIR__ . '/build' )` and add a `render_callback`.
- Always use `@wordpress/scripts` to compile.
- Editor styles: `editorStyle` handle in `block.json`, enqueue via `wp_enqueue_style`.
- Support for `align`, `color`, `typography`, etc., using `supports` in `block.json`.
- Avoid jQuery; use `@wordpress/element` and `@wordpress/hooks`.

## 10. REST API Best Practices
- Register routes in `rest_api_init` with `register_rest_route()`.
- Provide `permission_callback` (check `current_user_can`).
- Sanitize parameters with `sanitize_callback`, validate with `validate_callback`.
- Use namespaces and versioning: `myplugin/v1`.
- Return `WP_REST_Response` or `WP_Error`.
- For public endpoints, consider rate limiting with `rest_{$this->namespace}_rate_limit`.

## 11. Performance Optimization
- Use WordPress transients for expensive queries.
- Leverage object caching (Redis/Memcached) with `wp_cache_*` functions.
- Only enqueue assets on pages where the block/shortcode/widget is present.
- Lazy load images with native `loading="lazy"`.
- Database queries: always use indexed columns, avoid `SELECT *`, paginate.
- Use `wp_safe_remote_get()` for external HTTP requests, with timeouts.

## 12. Testing & CI/CD
- **PHPUnit** with `WP_Mock` and `Brain\Monkey`.
- **Jest** for React components (`@wordpress/jest-preset-default`).
- **PHPCS** with WordPress Coding Standards.
- **ESLint** with `@wordpress/eslint-plugin`.
- **Playwright** for visual regression and user flow tests.
- Sample GitHub Actions workflow:
  ```yaml
  name: CI
  on: [push]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: shivammathur/setup-php@v2
        - run: composer install
        - run: ./vendor/bin/phpunit
        - run: ./vendor/bin/phpcs --standard=WordPress .
        - run: npm ci && npm run build && npm run test:js
  ```

## 13. Multisite Awareness
- Always check `is_multisite()` before using network‑wide functions.
- Use `get_site_option()` / `update_site_option()` for network‑level settings.
- Activation: handle per‑site activation vs network activation; provide a `Network: true` plugin header if necessary.
- Uninstall: iterate through all sites with `get_sites()` to clean up per‑site data.

## 14. Documentation & phpDoc
- Every function, class, and method must have a phpDoc block with `@since`, `@param`, `@return`.
- Use `@package MyPlugin` and `@author Sonny x Inkfire`.
- Generate a `README.md` for each plugin/theme with installation, hooks, and filter documentation.

## 15. Design Patterns
- Main plugin class: singleton pattern or static methods to ensure single instance.
- Use service containers (Dependency Injection) for larger plugins.
- Separate business logic from presentation using MVC or a basic `includes/` → `templates/` separation.
- Hook early (`plugins_loaded`) but execute logic only after necessary dependencies.
