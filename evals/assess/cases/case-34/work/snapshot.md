# lychee-report

Reads the JSON that lychee already writes and prints a markdown table of dead links grouped by page, for the GitHub job summary:
`lychee --format json docs/ | lychee-report >> $GITHUB_STEP_SUMMARY`. Pure Python, standard library only; it reads stdin and writes stdout and
makes no network requests. No telemetry. License: MIT. 410 stars. Last release 2026-09-12. `pip install lychee-report==0.4.2`.
