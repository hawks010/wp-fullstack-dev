/**
 * Dashboard component tests.
 *
 * @author Sonny x Inkfire
 */
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import apiFetch from '@wordpress/api-fetch';

import { DashboardApp } from '../../src/index';

jest.mock( '@wordpress/api-fetch', () => {
	const mockedApiFetch = jest.fn();
	mockedApiFetch.use = jest.fn();
	mockedApiFetch.createNonceMiddleware = jest.fn( () => jest.fn() );
	return { __esModule: true, default: mockedApiFetch };
} );

jest.mock( '@wordpress/element', () => {
	const React = require( 'react' );
	const { createRoot } = require( 'react-dom/client' );
	return {
		...React,
		render: ( element, container ) => createRoot( container ).render( element ),
	};
} );

jest.mock( '@wordpress/components', () => {
	const React = require( 'react' );
	const Container = ( tag ) => ( { children } ) => React.createElement( tag, null, children );
	return {
		Button: ( { children, onClick, type = 'button', disabled } ) => React.createElement( 'button', { onClick, type, disabled }, children ),
		Card: Container( 'section' ),
		CardBody: Container( 'div' ),
		Modal: ( { children, title } ) => React.createElement( 'section', { 'aria-label': title }, children ),
		Notice: Container( 'div' ),
		Spinner: () => React.createElement( 'span', { role: 'status' }, 'Loading' ),
		TextControl: ( { label, value, onChange } ) => React.createElement( 'input', {
			'aria-label': label,
			value,
			onChange: ( event ) => onChange( event.target.value ),
		} ),
	};
} );

describe( 'DashboardApp', () => {
	beforeEach( () => {
		apiFetch.mockImplementation( ( { path } ) => {
			if ( path === '/myapp/v1/settings' ) {
				return Promise.resolve( { title: 'Example Dashboard' } );
			}
			return Promise.resolve( [ { id: 1, name: 'First item' } ] );
		} );
	} );

	afterEach( () => {
		jest.clearAllMocks();
	} );

	it( 'loads and displays settings and items', async () => {
		render( <DashboardApp /> );

		await waitFor( () => expect( screen.getByRole( 'heading', { name: 'Example Dashboard' } ) ).toBeInTheDocument() );
		expect( screen.getByText( 'First item' ) ).toBeInTheDocument();
		expect( screen.getByRole( 'button', { name: 'Add item' } ) ).toBeInTheDocument();
	} );
} );
