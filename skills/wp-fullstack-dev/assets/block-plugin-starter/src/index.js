/**
 * Dynamic message block editor.
 *
 * @author Sonny x Inkfire
 */
import { registerBlockType } from '@wordpress/blocks';
import { InspectorControls, RichText, useBlockProps } from '@wordpress/block-editor';
import { PanelBody, TextControl } from '@wordpress/components';
import { __ } from '@wordpress/i18n';

import metadata from './block.json';
import './editor.scss';
import './style.scss';

/**
 * Edit the dynamic message block.
 *
 * @param {Object}   props               Block properties.
 * @param {Object}   props.attributes    Block attributes.
 * @param {Function} props.setAttributes Attribute update callback.
 * @return {JSX.Element} Editor interface.
 */
export function Edit( { attributes, setAttributes } ) {
	const blockProps = useBlockProps( { className: 'example-dynamic-message' } );

	return (
		<>
			<InspectorControls>
				<PanelBody title={ __( 'Message settings', 'example-dynamic-block' ) }>
					<TextControl
						label={ __( 'Accessible label', 'example-dynamic-block' ) }
						value={ attributes.label }
						onChange={ ( label ) => setAttributes( { label } ) }
					/>
				</PanelBody>
			</InspectorControls>
			<div { ...blockProps }>
				<RichText
					tagName="p"
					value={ attributes.content }
					onChange={ ( content ) => setAttributes( { content } ) }
					placeholder={ __( 'Write a message…', 'example-dynamic-block' ) }
				/>
			</div>
		</>
	);
}

registerBlockType( metadata.name, {
	edit: Edit,
	save: () => null,
} );
