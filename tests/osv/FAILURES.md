# Known-bad dependency lookup: failures before implementation

- Added/bumped resolved versions in npm, PyPI, Go, crates or Actions escape lookup.
- An unchanged or removed version becomes a new finding.
- Manifest ranges, unsupported locks, aliases, local/git sources or malformed input silently become clean.
- A renamed file loses comparison coverage; API pagination or file limits omit a dependency file.
- OSV querybatch results are misaligned, missing, malformed, truncated or paginated but treated as clean.
- A MAL record or ordinary advisory match can be erased or contradicted by model prose.
- An unavailable advisory detail erases the known matching ID.
- Missing severity is invented; a database match is overstated as proof of runtime exploitability.
- Network failure, timeout, request/query/body limits or unsupported input are reported as no matches.
- Credentials or PR text reach OSV; untrusted paths, package URLs or advisory links become request destinations.
- The tool executes a manifest/installer or checks out the PR head in a secret-bearing job.
- A model failure prevents already collected known-bad findings from being published first.
- A clean recorded bump creates a finding, or a zero result claims general safety.

Tests use recorded public OSV responses and synthetic repository files. No live CI requests or model eval cases.
