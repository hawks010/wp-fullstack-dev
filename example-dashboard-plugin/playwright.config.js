/**
 * Playwright configuration.
 *
 * @author Sonny x Inkfire
 */
const { defineConfig } = require( '@playwright/test' );

module.exports = defineConfig( {
	testDir: './e2e',
	use: {
		baseURL: process.env.WP_BASE_URL || 'http://localhost:8888',
		trace: 'retain-on-failure',
	},
	reporter: process.env.CI ? 'github' : 'list',
} );
