<?php
/**
 * Plugin Name: My App Dashboard
 * Description: Demonstrates a React-powered WordPress dashboard backed by secure REST endpoints.
 * Version:     2.1.0
 * Author:      Sonny x Inkfire
 * Text Domain: myapp-dashboard
 * Domain Path: /languages
 * Requires PHP: 8.2
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MYAPP_DASHBOARD_VERSION', '2.1.0' );
define( 'MYAPP_DASHBOARD_FILE', __FILE__ );
define( 'MYAPP_DASHBOARD_DIR', plugin_dir_path( __FILE__ ) );
define( 'MYAPP_DASHBOARD_URL', plugin_dir_url( __FILE__ ) );

require_once MYAPP_DASHBOARD_DIR . 'includes/class-rest-controller.php';
require_once MYAPP_DASHBOARD_DIR . 'includes/class-plugin.php';

register_activation_hook( __FILE__, array( MyAppDashboard\Plugin::class, 'activate' ) );

add_action(
	'before_woocommerce_init',
	static function (): void {
		if ( class_exists( Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
			Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility(
				'custom_order_tables',
				__FILE__,
				true
			);
		}
	}
);

add_action(
	'plugins_loaded',
	static function (): void {
		load_plugin_textdomain(
			'myapp-dashboard',
			false,
			dirname( plugin_basename( __FILE__ ) ) . '/languages'
		);

		( new MyAppDashboard\Plugin() )->register();
	}
);
