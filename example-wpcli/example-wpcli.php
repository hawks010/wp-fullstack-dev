<?php
/**
 * Plugin Name: Example WP-CLI Command
 * Description: Registers a custom command for listing dashboard items.
 * Version:     2.1.0
 * Author:      Sonny x Inkfire
 * Text Domain: example-wpcli
 * Requires PHP: 8.2
 *
 * @package ExampleWPCLI
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( defined( 'WP_CLI' ) && WP_CLI ) {
	require_once __DIR__ . '/includes/class-myapp-command.php';
	WP_CLI::add_command( 'myapp', MyApp_Command::class );
}
