<?php
defined('ABSPATH') || exit;
// Daily purge of the sitemap cache (documented in docs/CACHE.md).
add_action('acme_purge_cache', function () {
    foreach (glob(WP_CONTENT_DIR . '/cache/acme/*.xml') as $f) { unlink($f); }
});
if (!wp_next_scheduled('acme_purge_cache')) {
    wp_schedule_event(time(), 'daily', 'acme_purge_cache');
}
