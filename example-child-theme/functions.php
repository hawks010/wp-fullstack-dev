<?php
/**
 * Child theme functions and definitions.
 *
 * @package MyAgenticChildTheme
 * @author  Sonny x Inkfire
 */

declare(strict_types=1);

// Enqueue parent and child styles
add_action( 'wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'parent-style',
        get_template_directory_uri() . '/style.css'
    );
    wp_enqueue_style(
        'child-style',
        get_stylesheet_directory_uri() . '/style.css',
        [ 'parent-style' ],
        wp_get_theme()->get( 'Version' )
    );
    wp_enqueue_style(
        'child-custom',
        get_stylesheet_directory_uri() . '/assets/css/child-theme.css',
        [ 'child-style' ],
        '1.0.0'
    );
} );

// Load text domain
add_action( 'after_setup_theme', function () {
    load_child_theme_textdomain( 'my-agentic-child-theme', get_stylesheet_directory() . '/languages' );
} );

// Example template override
add_filter( 'template_include', function ( $template ) {
    if ( is_page( 'custom' ) ) {
        return get_stylesheet_directory() . '/templates/custom-page.php';
    }
    return $template;
} );
