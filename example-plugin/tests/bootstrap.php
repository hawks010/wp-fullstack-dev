<?php
/**
 * PHPUnit bootstrap.
 *
 * @package MyAgenticPlugin
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

require_once dirname( __DIR__ ) . '/vendor/autoload.php';

define( 'MYAP_VERSION', '1.0.0' );
define( 'MYAP_PLUGIN_URL', 'https://example.test/wp-content/plugins/my-agentic-plugin/' );

WP_Mock::bootstrap();

require_once dirname( __DIR__ ) . '/includes/class-core.php';
