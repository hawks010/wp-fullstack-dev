<?php
/**
 * Network-safe uninstall routine.
 *
 * @package ExampleMultisite
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit;
}

$delete_site_data = static function (): void {
	delete_option( 'example_multisite_settings' );
};

if ( is_multisite() ) {
	$site_ids = get_sites( array( 'fields' => 'ids', 'number' => 0 ) );
	foreach ( $site_ids as $site_id ) {
		switch_to_blog( (int) $site_id );
		$delete_site_data();
		restore_current_blog();
	}
} else {
	$delete_site_data();
}
