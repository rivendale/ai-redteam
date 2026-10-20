<?php
defined('ABSPATH') || exit;
function acme_get_title_format() {
    return get_option('acme_title_format', '%title% | %sitename%');
}
function acme_render_title() {
    echo '<title>' . $GLOBALS['acme_title'] . '</title>';
}
