<?php
/**
 * REST route registration tests powered by Brain Monkey.
 *
 * @package MyAppDashboard
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

namespace MyAppDashboard\Tests;

use Brain\Monkey;
use Brain\Monkey\Functions;
use MyAppDashboard\REST_Controller;
use PHPUnit\Framework\TestCase;

/**
 * Verify all route groups are registered.
 */
final class RouteRegistrationTest extends TestCase {
	/**
	 * Set up Brain Monkey.
	 *
	 * @return void
	 */
	protected function setUp(): void {
		parent::setUp();
		Monkey\setUp();
	}

	/**
	 * Tear down Brain Monkey.
	 *
	 * @return void
	 */
	protected function tearDown(): void {
		Monkey\tearDown();
		parent::tearDown();
	}

	/**
	 * Verify settings, item collection, and item deletion routes.
	 *
	 * @return void
	 */
	public function test_registers_three_route_groups(): void {
		Functions\expect( 'register_rest_route' )->times( 3 )->andReturn( true );
		( new REST_Controller() )->register_routes();
		$this->addToAssertionCount( 1 );
	}
}
