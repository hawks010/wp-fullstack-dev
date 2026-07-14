/**
 * Block metadata tests.
 *
 * @author Sonny x Inkfire
 */
import metadata from '../src/block.json';

describe( 'dynamic message block metadata', () => {
	it( 'declares a dynamic render file and safe HTML support', () => {
		expect( metadata.name ).toBe( 'sonny-x-inkfire/dynamic-message' );
		expect( metadata.render ).toBe( 'file:./render.php' );
		expect( metadata.supports.html ).toBe( false );
	} );
} );
