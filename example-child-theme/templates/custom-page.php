<?php
/**
 * Custom page template.
 *
 * @package MyAgenticChildTheme
 * @author  Sonny x Inkfire
 */

get_header();
?>
<div class="childtheme-page-wrapper">
    <h1><?php the_title(); ?></h1>
    <?php
    while ( have_posts() ) {
        the_post();
        the_content();
    }
    ?>
</div>
<?php
get_footer();
