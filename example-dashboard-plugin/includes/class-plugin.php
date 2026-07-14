<?php
/**
 * Dashboard plugin coordinator.
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAppDashboard;

/**
 * Registers the admin screen, assets, and REST API.
 */
final class Plugin {
	/**
	 * Admin page hook suffix.
	 *
	 * @var string
	 */
	private string $page_hook = '';

	/**
	 * Register WordPress hooks.
	 *
	 * @since 2.1.0
	 * @return void
	 */
	public function register(): void {
		add_action( 'admin_menu', array( $this, 'register_admin_page' ) );
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_admin_assets' ) );
		add_action( 'rest_api_init', array( new REST_Controller(), 'register_routes' ) );
	}

	/**
	 * Seed plugin options without overwriting existing data.
	 *
	 * @since 2.1.0
	 * @return void
	 */
	public static function activate(): void {
		add_option(
			'myapp_settings',
			array(
				'title' => __( 'My App Dashboard', 'myapp-dashboard' ),
			)
		);
		add_option( 'myapp_items', array() );
	}

	/**
	 * Add the top-level dashboard page.
	 *
	 * @since 2.1.0
	 * @return void
	 */
	public function register_admin_page(): void {
		$this->page_hook = add_menu_page(
			__( 'My App Dashboard', 'myapp-dashboard' ),
			__( 'My App', 'myapp-dashboard' ),
			'manage_options',
			'myapp-dashboard',
			array( $this, 'render_admin_page' ),
			'dashicons-screenoptions',
			58
		);
	}

	/**
	 * Render the React mount point.
	 *
	 * @since 2.1.0
	 * @return void
	 */
	public function render_admin_page(): void {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( esc_html__( 'You are not allowed to access this page.', 'myapp-dashboard' ) );
		}
		?>
		<div class="wrap">
			<div id="myapp-dashboard-root"></div>
		</div>
		<?php
	}

	/**
	 * Enqueue compiled assets only on the plugin screen.
	 *
	 * @since 2.1.0
	 * @param string $hook_suffix Current admin page hook.
	 * @return void
	 */
	public function enqueue_admin_assets( string $hook_suffix ): void {
		if ( $hook_suffix !== $this->page_hook ) {
			return;
		}

		$asset_file = MYAPP_DASHBOARD_DIR . 'build/index.asset.php';
		$asset      = file_exists( $asset_file )
			? require $asset_file
			: array(
				'dependencies' => array( 'wp-api-fetch', 'wp-components', 'wp-element', 'wp-i18n' ),
				'version'      => MYAPP_DASHBOARD_VERSION,
			);

		wp_enqueue_script(
			'myapp-dashboard',
			MYAPP_DASHBOARD_URL . 'build/index.js',
			$asset['dependencies'],
			$asset['version'],
			true
		);
		wp_set_script_translations( 'myapp-dashboard', 'myapp-dashboard' );
		wp_enqueue_style( 'wp-components' );

		if ( file_exists( MYAPP_DASHBOARD_DIR . 'build/style-index.css' ) ) {
			wp_enqueue_style(
				'myapp-dashboard',
				MYAPP_DASHBOARD_URL . 'build/style-index.css',
				array( 'wp-components' ),
				$asset['version']
			);
		}

		wp_add_inline_script(
			'myapp-dashboard',
			'window.myAppDashboard = ' . wp_json_encode(
				array(
					'nonce' => wp_create_nonce( 'wp_rest' ),
				)
			) . ';',
			'before'
		);
	}
}
