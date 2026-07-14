<?php
/**
 * Plugin Name: Example Dynamic Block
 * Description: Demonstrates metadata-driven registration and secure server-side block rendering.
 * Version:     2.1.0
 * Author:      Sonny x Inkfire
 * Text Domain: example-dynamic-block
 * Requires PHP: 8.2
 *
 * @package ExampleDynamicBlock
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action(
	'init',
	static function (): void {
		register_block_type( __DIR__ . '/build' );
	}
);
