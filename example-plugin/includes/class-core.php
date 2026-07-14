<?php
/**
 * Core plugin class.
 *
 * @package MyAgenticPlugin
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAgenticPlugin;

class Core {
    public function __construct() {
        add_action( 'wp_footer', [ $this, 'display_footer_message' ] );
    }

    /**
     * Display a footer message.
     *
     * @since  1.0.0
     * @return void
     */
    public function display_footer_message(): void {
        ?>
        <div class="myap-footer-message">
            <?php esc_html_e( 'Powered by My Agentic Plugin', 'my-agentic-plugin' ); ?>
        </div>
        <?php
    }
}
