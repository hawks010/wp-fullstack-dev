<?php
/**
 * REST controller unit tests powered by WP_Mock.
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAppDashboard\Tests;

use MyAppDashboard\REST_Controller;
use WP_Error;
use WP_Mock;
use WP_Mock\Tools\TestCase;
use WP_REST_Request;

/**
 * Verify authorization and CRUD behavior.
 */
final class RestControllerTest extends TestCase {
	/**
	 * Verify that a valid nonce and capability are required.
	 *
	 * @return void
	 */
	public function test_permissions_check_accepts_authorized_request(): void {
		WP_Mock::userFunction( 'current_user_can' )->once()->with( 'manage_options' )->andReturn( true );
		WP_Mock::userFunction( 'wp_verify_nonce' )->once()->with( 'valid', 'wp_rest' )->andReturn( 1 );

		$request = new WP_REST_Request( array(), array( 'X-WP-Nonce' => 'valid' ) );
		$this->assertTrue( ( new REST_Controller() )->permissions_check( $request ) );
	}

	/**
	 * Verify that missing capabilities are rejected before nonce validation.
	 *
	 * @return void
	 */
	public function test_permissions_check_rejects_unauthorized_request(): void {
		WP_Mock::userFunction( 'current_user_can' )->once()->with( 'manage_options' )->andReturn( false );
		WP_Mock::userFunction( '__' )->andReturnUsing( static fn( string $text ): string => $text );

		$result = ( new REST_Controller() )->permissions_check( new WP_REST_Request() );
		$this->assertInstanceOf( WP_Error::class, $result );
		$this->assertSame( 'myapp_forbidden', $result->get_error_code() );
	}

	/**
	 * Verify settings are sanitized before persistence.
	 *
	 * @return void
	 */
	public function test_update_settings_sanitizes_and_persists_title(): void {
		WP_Mock::userFunction( 'sanitize_text_field' )->once()->with( '<b>Dashboard</b>' )->andReturn( 'Dashboard' );
		WP_Mock::userFunction( 'update_option' )->once()->with( 'myapp_settings', array( 'title' => 'Dashboard' ) )->andReturn( true );

		$response = ( new REST_Controller() )->update_settings( new WP_REST_Request( array( 'title' => '<b>Dashboard</b>' ) ) );
		$this->assertSame( array( 'title' => 'Dashboard' ), $response->get_data() );
		$this->assertSame( 200, $response->get_status() );
	}

	/**
	 * Verify validation helpers reject invalid values.
	 *
	 * @return void
	 */
	public function test_validation_helpers(): void {
		$controller = new REST_Controller();
		$this->assertTrue( $controller->validate_non_empty_string( 'Item' ) );
		$this->assertFalse( $controller->validate_non_empty_string( '   ' ) );
		$this->assertTrue( $controller->validate_positive_integer( '4' ) );
		$this->assertFalse( $controller->validate_positive_integer( 0 ) );
	}
}
