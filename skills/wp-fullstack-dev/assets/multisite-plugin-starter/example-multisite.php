<?php
/**
 * Plugin Name: Example Multisite Lifecycle
 * Description: Demonstrates network activation, per-site options, and network-safe cleanup.
 * Version:     2.1.0
 * Author:      Sonny x Inkfire
 * Text Domain: example-multisite
 * Network:     true
 * Requires PHP: 8.2
 *
 * @package ExampleMultisite
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace ExampleMultisite;

use WP_Site;

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const OPTION_NAME = 'example_multisite_settings';

register_activation_hook( __FILE__, __NAMESPACE__ . '\\activate' );
add_action( 'wp_initialize_site', __NAMESPACE__ . '\\initialize_new_site', 100, 1 );

/**
 * Add the plugin option to one site.
 *
 * @since 2.1.0
 * @return void
 */
function add_site_option(): void {
	add_option(
		OPTION_NAME,
		array(
			'enabled' => true,
			'version' => '2.1.0',
		)
	);
}

/**
 * Handle site or network activation.
 *
 * @since 2.1.0
 * @param bool $network_wide Whether activation is network-wide.
 * @return void
 */
function activate( bool $network_wide ): void {
	if ( ! is_multisite() || ! $network_wide ) {
		add_site_option();
		return;
	}

	$site_ids = get_sites( array( 'fields' => 'ids', 'number' => 0 ) );
	foreach ( $site_ids as $site_id ) {
		switch_to_blog( (int) $site_id );
		add_site_option();
		restore_current_blog();
	}
}

/**
 * Initialize options when a new network site is created.
 *
 * @since 2.1.0
 * @param WP_Site $site Newly initialized site.
 * @return void
 */
function initialize_new_site( WP_Site $site ): void {
	switch_to_blog( (int) $site->blog_id );
	add_site_option();
	restore_current_blog();
}
