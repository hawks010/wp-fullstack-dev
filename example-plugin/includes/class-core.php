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
	/**
	 * Register shortcode and conditional asset hooks.
	 *
	 * @since  1.0.0
	 * @return void
	 */
	public function __construct() {
		add_shortcode( 'my_agentic_message', array( $this, 'render_message' ) );
		add_action( 'wp_enqueue_scripts', array( $this, 'maybe_enqueue_assets' ) );
	}

	/**
	 * Enqueue styles when the current singular post contains the shortcode.
	 *
	 * @since  1.0.0
	 * @return void
	 */
	public function maybe_enqueue_assets(): void {
		global $post;

		if ( is_singular() && $post instanceof \WP_Post && has_shortcode( $post->post_content, 'my_agentic_message' ) ) {
			$this->enqueue_assets();
		}
	}

	/**
	 * Render the plugin message shortcode.
	 *
	 * Enqueuing here is a fallback for shortcode content rendered outside the
	 * main singular post content.
	 *
	 * @since  1.0.0
	 * @return string
	 */
	public function render_message(): string {
		$this->enqueue_assets();

		return sprintf(
			'<div class="myap-footer-message">%s</div>',
			esc_html__( 'Powered by My Agentic Plugin', 'my-agentic-plugin' )
		);
	}

	/**
	 * Enqueue the shortcode stylesheet once.
	 *
	 * @since  1.0.0
	 * @return void
	 */
	private function enqueue_assets(): void {
		wp_enqueue_style(
			'my-agentic-plugin-style',
			MYAP_PLUGIN_URL . 'assets/css/style.css',
			array(),
			MYAP_VERSION
		);
	}
}
