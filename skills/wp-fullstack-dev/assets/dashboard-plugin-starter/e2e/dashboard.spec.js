/**
 * Dashboard browser test.
 *
 * @author Sonny x Inkfire
 */
const { test, expect } = require( '@playwright/test' );

test( 'administrator can load the dashboard title', async ( { page } ) => {
	await page.goto( '/wp-login.php' );
	await page.getByLabel( 'Username or Email Address' ).fill( 'admin' );
	await page.locator( '#user_pass' ).fill( 'password' );
	await page.getByRole( 'button', { name: 'Log In' } ).click();
	await page.goto( '/wp-admin/admin.php?page=myapp-dashboard' );

	await expect( page.getByRole( 'heading', { name: 'My App Dashboard' } ) ).toBeVisible();
} );
