# placeholder-check

A small command-line tool that reads a Crowdin CSV export and reports strings whose placeholders are missing, extra or reordered compared with the
source string. Understands {0}, {name}, %s, %d and %1$s. Crowdin's own check flags only a missing placeholder in the editor; this tool also checks extra and reordered ones across a whole export.
Reads a file you give it; makes no network requests; no telemetry. Release binaries for macOS and Windows with published SHA-256 sums; no toolchain needed.
License: zlib. Last release v0.8.2 (2026-09-17).
