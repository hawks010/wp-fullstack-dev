<?php
/**
 * Plugin Name: My Agentic Plugin
 * Plugin URI:  https://github.com/hawks010/wp-fullstack-dev-gpt-skill
 * Description: A minimal WordPress plugin demonstrating modern standards: PHP 8.2+, PSR‑4 autoloading, i18n, DB versioning, and clean uninstall.
 * Version:     1.0.0
 * Author:      Sonny x Inkfire
 * Text Domain: my-agentic-plugin
 * Domain Path: /languages
 */

declare(strict_types=1);

// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
    die;
}

define( 'MYAP_VERSION', '1.0.0' );
define( 'MYAP_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'MYAP_PLUGIN_URL', plugin_dir_url( __FILE__ ) );

// PSR-4 autoloader (custom, no Composer)
spl_autoload_register( function ( $class ) {
    $prefix   = 'MyAgenticPlugin\\';
    $base_dir = MYAP_PLUGIN_DIR . 'includes/';

    $len = strlen( $prefix );
    if ( strncmp( $prefix, $class, $len ) !== 0 ) {
        return;
    }

    $relative_class = substr( $class, $len );
    $file           = $base_dir . 'class-' . strtolower( str_replace( '\\', '-', $relative_class ) ) . '.php';

    if ( file_exists( $file ) ) {
        require $file;
    }
} );

// Initialize the plugin on `plugins_loaded`
add_action( 'plugins_loaded', function () {
    load_plugin_textdomain( 'my-agentic-plugin', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );

    // Version check & dbDelta upgrade
    $stored_version = get_option( 'myap_version', '0' );
    if ( version_compare( $stored_version, MYAP_VERSION, '<' ) ) {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        // Example custom table
        global $wpdb;
        $table_name      = $wpdb->prefix . 'myap_data';
        $charset_collate = $wpdb->get_charset_collate();
        $sql             = "CREATE TABLE $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            name varchar(100) NOT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY  (id)
        ) $charset_collate;";
        dbDelta( $sql );
        update_option( 'myap_version', MYAP_VERSION );
    }

    // Boot the core class
    if ( class_exists( 'MyAgenticPlugin\\Core' ) ) {
        new \MyAgenticPlugin\Core();
    }
} );

// Enqueue front‑end assets
add_action( 'wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'my-agentic-plugin-style',
        MYAP_PLUGIN_URL . 'assets/css/style.css',
        [],
        MYAP_VERSION
    );
} );
