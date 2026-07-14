/**
 * React dashboard application.
 *
 * @author Sonny x Inkfire
 */
import apiFetch from '@wordpress/api-fetch';
import {
	Button,
	Card,
	CardBody,
	Modal,
	Notice,
	Spinner,
	TextControl,
} from '@wordpress/components';
import { render, useEffect, useState } from '@wordpress/element';
import { __ } from '@wordpress/i18n';

import './style.scss';

const config = window.myAppDashboard || {};

if ( config.nonce ) {
	apiFetch.use( apiFetch.createNonceMiddleware( config.nonce ) );
}

/**
 * Render the settings and items experience.
 *
 * @return {JSX.Element} Dashboard application.
 */
export function DashboardApp() {
	const [ settings, setSettings ] = useState( { title: '' } );
	const [ items, setItems ] = useState( [] );
	const [ loading, setLoading ] = useState( true );
	const [ saving, setSaving ] = useState( false );
	const [ modalOpen, setModalOpen ] = useState( false );
	const [ itemName, setItemName ] = useState( '' );
	const [ notice, setNotice ] = useState( null );

	useEffect( () => {
		Promise.all( [
			apiFetch( { path: '/myapp/v1/settings' } ),
			apiFetch( { path: '/myapp/v1/items' } ),
		] )
			.then( ( [ settingsResponse, itemsResponse ] ) => {
				setSettings( settingsResponse );
				setItems( itemsResponse );
			} )
			.catch( ( error ) => {
				setNotice( {
					status: 'error',
					message: error.message || __( 'Unable to load dashboard data.', 'myapp-dashboard' ),
				} );
			} )
			.finally( () => setLoading( false ) );
	}, [] );

	const saveSettings = async ( event ) => {
		event.preventDefault();
		setSaving( true );
		try {
			const response = await apiFetch( {
				path: '/myapp/v1/settings',
				method: 'POST',
				data: settings,
			} );
			setSettings( response );
			setNotice( { status: 'success', message: __( 'Settings saved.', 'myapp-dashboard' ) } );
		} catch ( error ) {
			setNotice( { status: 'error', message: error.message || __( 'Settings could not be saved.', 'myapp-dashboard' ) } );
		} finally {
			setSaving( false );
		}
	};

	const createItem = async () => {
		if ( ! itemName.trim() ) {
			return;
		}
		setSaving( true );
		try {
			const item = await apiFetch( {
				path: '/myapp/v1/items',
				method: 'POST',
				data: { name: itemName },
			} );
			setItems( ( current ) => [ ...current, item ] );
			setItemName( '' );
			setModalOpen( false );
			setNotice( { status: 'success', message: __( 'Item added.', 'myapp-dashboard' ) } );
		} catch ( error ) {
			setNotice( { status: 'error', message: error.message || __( 'Item could not be added.', 'myapp-dashboard' ) } );
		} finally {
			setSaving( false );
		}
	};

	const deleteItem = async ( id ) => {
		try {
			await apiFetch( { path: `/myapp/v1/items/${ id }`, method: 'DELETE' } );
			setItems( ( current ) => current.filter( ( item ) => item.id !== id ) );
			setNotice( { status: 'success', message: __( 'Item deleted.', 'myapp-dashboard' ) } );
		} catch ( error ) {
			setNotice( { status: 'error', message: error.message || __( 'Item could not be deleted.', 'myapp-dashboard' ) } );
		}
	};

	if ( loading ) {
		return (
			<div className="myapp-dashboard__loading" aria-live="polite">
				<Spinner />
				<span>{ __( 'Loading dashboard…', 'myapp-dashboard' ) }</span>
			</div>
		);
	}

	return (
		<div className="myapp-dashboard">
			<h1>{ settings.title || __( 'My App Dashboard', 'myapp-dashboard' ) }</h1>

			{ notice && (
				<Notice status={ notice.status } onRemove={ () => setNotice( null ) }>
					{ notice.message }
				</Notice>
			) }

			<div className="myapp-dashboard__grid">
				<Card>
					<CardBody>
						<h2>{ __( 'Settings', 'myapp-dashboard' ) }</h2>
						<form onSubmit={ saveSettings }>
							<TextControl
								label={ __( 'Dashboard title', 'myapp-dashboard' ) }
								value={ settings.title }
								onChange={ ( title ) => setSettings( { ...settings, title } ) }
								required
							/>
							<Button variant="primary" type="submit" isBusy={ saving } disabled={ saving }>
								{ __( 'Save settings', 'myapp-dashboard' ) }
							</Button>
						</form>
					</CardBody>
				</Card>

				<Card>
					<CardBody>
						<div className="myapp-dashboard__section-heading">
							<h2>{ __( 'Items', 'myapp-dashboard' ) }</h2>
							<Button variant="secondary" onClick={ () => setModalOpen( true ) }>
								{ __( 'Add item', 'myapp-dashboard' ) }
							</Button>
						</div>
						{ items.length === 0 ? (
							<p>{ __( 'No items yet.', 'myapp-dashboard' ) }</p>
						) : (
							<ul className="myapp-dashboard__items">
								{ items.map( ( item ) => (
									<li key={ item.id }>
										<span>{ item.name }</span>
										<Button variant="link" isDestructive onClick={ () => deleteItem( item.id ) }>
											{ __( 'Delete', 'myapp-dashboard' ) }
										</Button>
									</li>
								) ) }
							</ul>
						) }
					</CardBody>
				</Card>
			</div>

			{ modalOpen && (
				<Modal title={ __( 'Add item', 'myapp-dashboard' ) } onRequestClose={ () => setModalOpen( false ) }>
					<TextControl
						label={ __( 'Item name', 'myapp-dashboard' ) }
						value={ itemName }
						onChange={ setItemName }
						autoFocus
					/>
					<div className="myapp-dashboard__modal-actions">
						<Button variant="tertiary" onClick={ () => setModalOpen( false ) }>
							{ __( 'Cancel', 'myapp-dashboard' ) }
						</Button>
						<Button variant="primary" onClick={ createItem } isBusy={ saving } disabled={ saving || ! itemName.trim() }>
							{ __( 'Add item', 'myapp-dashboard' ) }
						</Button>
					</div>
				</Modal>
			) }
		</div>
	);
}

const root = document.getElementById( 'myapp-dashboard-root' );
if ( root ) {
	render( <DashboardApp />, root );
}
