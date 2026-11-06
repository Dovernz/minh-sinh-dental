<?php
/**
 * Template for displaying all pages
 */
get_header();
?>

<main class="container">
    <?php while (have_posts()) : the_post(); ?>
        <article class="article-container">
            <header class="article-header">
                <h1 class="article-title"><?php the_title(); ?></h1>
            </header>

            <div class="article-body">
                <?php the_content(); ?>
            </div>
        </article>
    <?php endwhile; ?>
</main>

<?php get_footer(); ?>
