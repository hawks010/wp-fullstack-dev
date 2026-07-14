<?php
/**
 * Core plugin tests.
 *
 * @package MyAgenticPlugin
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAgenticPlugin\Tests;

use MyAgenticPlugin\Core;
use WP_Mock;
use WP_Mock\Tools\TestCase;

/**
 * Verify shortcode registration and rendering.
 */
final class CoreTest extends TestCase {
    /**
     * Verify hooks are registered during construction.
     *
     * @return void
     */
    public function test_registers_shortcode_and_enqueue_hook(): void {
        WP_Mock::userFunction( 'add_shortcode' )->once()->with( 'my_agentic_message', \Mockery::type( 'array' ) )->andReturn( true );
        WP_Mock::userFunction( 'add_action' )->andReturn( true );

        new Core();
        $this->addToAssertionCount( 1 );
    }

    /**
     * Verify rendering escapes text and enqueues the scoped stylesheet.
     *
     * @return void
     */
    public function test_renders_message_and_enqueues_stylesheet(): void {
        WP_Mock::userFunction( 'add_shortcode' )->andReturn( true );
        WP_Mock::userFunction( 'add_action' )->andReturn( true );
        WP_Mock::userFunction( 'esc_html__' )->once()->andReturn( 'Powered by My Agentic Plugin' );
        WP_Mock::userFunction( 'wp_enqueue_style' )->once()->andReturn( true );

        $markup = ( new Core() )->render_message();

        $this->assertSame( '<div class="myap-footer-message">Powered by My Agentic Plugin</div>', $markup );
    }
}
