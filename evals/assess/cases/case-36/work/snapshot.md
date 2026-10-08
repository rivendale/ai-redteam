# ci-minutes-report

A GitHub Action that reads the timing of the workflow's last 20 completed runs from the GitHub Actions API, with the workflow's own token
(`actions: read`), and writes a table of billable minutes per job to the job summary, so you can see which jobs to cut. No external services,
no telemetry. License: MIT. Pin it by commit: `uses: example-org/ci-minutes-report@5b1c9e0d4a7f2c38e6a1b0d9f4c2e7a35d8b6f01  # v1.2.0`.
Last release 2026-09-29.
