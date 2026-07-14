<?php
/**
 * REST API controller for the dashboard example.
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAppDashboard;

use WP_Error;
use WP_REST_Request;
use WP_REST_Response;
use WP_REST_Server;

/**
 * Provides settings and item CRUD endpoints.
 */
final class REST_Controller {
	private const NAMESPACE = 'myapp/v1';

	/**
	 * Register REST routes.
	 *
	 * @since 2.1.0
	 * @return void
	 */
	public function register_routes(): void {
		register_rest_route(
			self::NAMESPACE,
			'/settings',
			array(
				array(
					'methods'             => WP_REST_Server::READABLE,
					'callback'            => array( $this, 'get_settings' ),
					'permission_callback' => array( $this, 'permissions_check' ),
				),
				array(
					'methods'             => WP_REST_Server::CREATABLE,
					'callback'            => array( $this, 'update_settings' ),
					'permission_callback' => array( $this, 'permissions_check' ),
					'args'                => array(
						'title' => array(
							'required'          => true,
							'type'              => 'string',
							'sanitize_callback' => 'sanitize_text_field',
							'validate_callback' => array( $this, 'validate_non_empty_string' ),
						),
					),
				),
			)
		);

		register_rest_route(
			self::NAMESPACE,
			'/items',
			array(
				array(
					'methods'             => WP_REST_Server::READABLE,
					'callback'            => array( $this, 'get_items' ),
					'permission_callback' => array( $this, 'permissions_check' ),
				),
				array(
					'methods'             => WP_REST_Server::CREATABLE,
					'callback'            => array( $this, 'create_item' ),
					'permission_callback' => array( $this, 'permissions_check' ),
					'args'                => array(
						'name' => array(
							'required'          => true,
							'type'              => 'string',
							'sanitize_callback' => 'sanitize_text_field',
							'validate_callback' => array( $this, 'validate_non_empty_string' ),
						),
					),
				),
			)
		);

		register_rest_route(
			self::NAMESPACE,
			'/items/(?P<id>\d+)',
			array(
				'methods'             => WP_REST_Server::DELETABLE,
				'callback'            => array( $this, 'delete_item' ),
				'permission_callback' => array( $this, 'permissions_check' ),
				'args'                => array(
					'id' => array(
						'required'          => true,
						'type'              => 'integer',
						'sanitize_callback' => 'absint',
						'validate_callback' => array( $this, 'validate_positive_integer' ),
					),
				),
			)
		);
	}

	/**
	 * Require both administrator capability and a valid REST nonce.
	 *
	 * @since 2.1.0
	 * @param WP_REST_Request $request Current request.
	 * @return true|WP_Error
	 */
	public function permissions_check( WP_REST_Request $request ) {
		if ( ! current_user_can( 'manage_options' ) ) {
			return new WP_Error( 'myapp_forbidden', __( 'You are not allowed to manage this data.', 'myapp-dashboard' ), array( 'status' => 403 ) );
		}

		$nonce = $request->get_header( 'X-WP-Nonce' );
		if ( ! is_string( $nonce ) || ! wp_verify_nonce( $nonce, 'wp_rest' ) ) {
			return new WP_Error( 'myapp_invalid_nonce', __( 'The REST nonce is invalid or expired.', 'myapp-dashboard' ), array( 'status' => 403 ) );
		}

		return true;
	}

	/**
	 * Validate a non-empty string parameter.
	 *
	 * @since 2.1.0
	 * @param mixed $value Parameter value.
	 * @return bool
	 */
	public function validate_non_empty_string( $value ): bool {
		return is_string( $value ) && '' !== trim( $value ) && 200 >= strlen( $value );
	}

	/**
	 * Validate a positive integer parameter.
	 *
	 * @since 2.1.0
	 * @param mixed $value Parameter value.
	 * @return bool
	 */
	public function validate_positive_integer( $value ): bool {
		return is_numeric( $value ) && 0 < (int) $value;
	}

	/**
	 * Return dashboard settings.
	 *
	 * @since 2.1.0
	 * @return WP_REST_Response
	 */
	public function get_settings(): WP_REST_Response {
		$settings = get_option( 'myapp_settings', array( 'title' => __( 'My App Dashboard', 'myapp-dashboard' ) ) );
		return new WP_REST_Response( $settings, 200 );
	}

	/**
	 * Persist dashboard settings.
	 *
	 * @since 2.1.0
	 * @param WP_REST_Request $request Current request.
	 * @return WP_REST_Response
	 */
	public function update_settings( WP_REST_Request $request ): WP_REST_Response {
		$settings = array( 'title' => sanitize_text_field( (string) $request->get_param( 'title' ) ) );
		update_option( 'myapp_settings', $settings );
		return new WP_REST_Response( $settings, 200 );
	}

	/**
	 * Return all items.
	 *
	 * @since 2.1.0
	 * @return WP_REST_Response
	 */
	public function get_items(): WP_REST_Response {
		$items = get_option( 'myapp_items', array() );
		return new WP_REST_Response( is_array( $items ) ? array_values( $items ) : array(), 200 );
	}

	/**
	 * Create an item.
	 *
	 * @since 2.1.0
	 * @param WP_REST_Request $request Current request.
	 * @return WP_REST_Response
	 */
	public function create_item( WP_REST_Request $request ): WP_REST_Response {
		$items    = get_option( 'myapp_items', array() );
		$items    = is_array( $items ) ? array_values( $items ) : array();
		$ids      = array_map( static fn( array $item ): int => absint( $item['id'] ?? 0 ), $items );
		$next_id  = empty( $ids ) ? 1 : max( $ids ) + 1;
		$new_item = array(
			'id'   => $next_id,
			'name' => sanitize_text_field( (string) $request->get_param( 'name' ) ),
		);

		$items[] = $new_item;
		update_option( 'myapp_items', $items );
		return new WP_REST_Response( $new_item, 201 );
	}

	/**
	 * Delete an item by ID.
	 *
	 * @since 2.1.0
	 * @param WP_REST_Request $request Current request.
	 * @return WP_REST_Response|WP_Error
	 */
	public function delete_item( WP_REST_Request $request ) {
		$id             = absint( $request->get_param( 'id' ) );
		$items          = get_option( 'myapp_items', array() );
		$items          = is_array( $items ) ? array_values( $items ) : array();
		$original_count = count( $items );
		$filtered       = array_values(
			array_filter(
				$items,
				static fn( array $item ): bool => absint( $item['id'] ?? 0 ) !== $id
			)
		);

		if ( count( $filtered ) === $original_count ) {
			return new WP_Error( 'myapp_item_not_found', __( 'Item not found.', 'myapp-dashboard' ), array( 'status' => 404 ) );
		}

		update_option( 'myapp_items', $filtered );
		return new WP_REST_Response( array( 'deleted' => true ), 200 );
	}
}
