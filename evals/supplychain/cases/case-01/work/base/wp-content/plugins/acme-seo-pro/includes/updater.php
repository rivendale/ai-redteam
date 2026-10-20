<?php
defined('ABSPATH') || exit;
// Update check against the vendor's published endpoint (unchanged since 2.0).
function acme_check_update() {
    return wp_remote_get('https://updates.acme.example/check?plugin=acme-seo-pro&v=2.4.1');
}
