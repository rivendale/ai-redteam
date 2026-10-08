# crashrank

A command-line tool that reads a Crashlytics crash export (JSON), merges crash groups whose stacks differ only in line numbers or build IDs, and prints the five crash groups
that affect the most players, with the first version each appeared in and the share of players hit, as a markdown table for the weekly triage. It reads a file you give it
and writes to stdout: no network requests.
Single static binary, no telemetry. Install: download the release binary and check its published SHA-256.
License: Apache-2.0. Last release 2026-09-19.
