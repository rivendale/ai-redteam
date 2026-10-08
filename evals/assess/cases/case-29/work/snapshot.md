# ci-select

Choose the tests a change affects. `ci-select --diff origin/main` prints the test files to run; use it as `pytest $(ci-select --diff origin/main)`.
Works with pytest. Pure Python, one dependency (the standard library only). No network access. No telemetry. License: MIT. Last release 2026-10-01.
Install: `pip install ci-select==2.1.0`. 2,100 stars; issues answered within days.
