<?php
/**
 * Uninstall routine – cleans up all plugin data.
 *
 * @package MyAgenticPlugin
 * @author  Sonny x Inkfire
 */

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}

global $wpdb;

// Remove custom table
$table_name = $wpdb->prefix . 'myap_data';
$wpdb->query( "DROP TABLE IF EXISTS {$table_name}" );

// Delete options
delete_option( 'myap_version' );
// Delete any other options or transients
