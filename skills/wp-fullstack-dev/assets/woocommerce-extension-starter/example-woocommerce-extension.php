<?php
/**
 * Plugin Name: Example WooCommerce Extension
 * Description: Adds an accessible product tab and declares HPOS compatibility.
 * Version:     2.1.0
 * Author:      Sonny x Inkfire
 * Text Domain: example-woocommerce-extension
 * Requires PHP: 8.2
 * Requires Plugins: woocommerce
 *
 * @package ExampleWooCommerceExtension
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace ExampleWooCommerceExtension;

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action(
	'before_woocommerce_init',
	static function (): void {
		if ( class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
			\Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'custom_order_tables', __FILE__, true );
		}
	}
);

add_filter(
	'woocommerce_product_tabs',
	static function ( array $tabs ): array {
		$tabs['sonny_x_inkfire_details'] = array(
			'title'    => __( 'Additional details', 'example-woocommerce-extension' ),
			'priority' => 25,
			'callback' => __NAMESPACE__ . '\\render_product_tab',
		);

		return $tabs;
	}
);

/**
 * Render custom product-tab content.
 *
 * @since 2.1.0
 * @return void
 */
function render_product_tab(): void {
	?>
	<h2><?php esc_html_e( 'Additional product details', 'example-woocommerce-extension' ); ?></h2>
	<p><?php esc_html_e( 'This content is added with supported WooCommerce product-tab hooks.', 'example-woocommerce-extension' ); ?></p>
	<?php
}
