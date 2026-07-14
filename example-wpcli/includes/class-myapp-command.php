<?php
/**
 * Custom WP-CLI command.
 *
 * @package ExampleWPCLI
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

use function WP_CLI\Utils\format_items;

/**
 * Manage My App demonstration data.
 */
final class MyApp_Command {
	/**
	 * List dashboard items.
	 *
	 * ## OPTIONS
	 *
	 * [--format=<format>]
	 * : Output format. Accepts table, json, csv, yaml, or count.
	 * ---
	 * default: table
	 * ---
	 *
	 * ## EXAMPLES
	 *
	 *     wp myapp items --format=json
	 *
	 * @since 2.1.0
	 * @param array<int, string>    $args Positional arguments.
	 * @param array<string, string> $assoc_args Associative arguments.
	 * @return void
	 */
	public function items( array $args, array $assoc_args ): void { // phpcs:ignore Generic.CodeAnalysis.UnusedFunctionParameter.FoundBeforeLastUsed
		$items  = get_option( 'myapp_items', array() );
		$items  = is_array( $items ) ? array_values( $items ) : array();
		$format = $assoc_args['format'] ?? 'table';

		if ( empty( $items ) ) {
			WP_CLI::warning( 'No dashboard items were found.' );
			return;
		}

		format_items( $format, $items, array( 'id', 'name' ) );
	}
}
