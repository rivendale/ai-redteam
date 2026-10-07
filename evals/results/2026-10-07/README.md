# v1 vs v2, 2026-10-07

Both skill versions ran over the same 23 cases (`evals/cases`) in the same sealed, tool-less headless Claude
session (`evals/tools/run_reviews.sh`, 3 in parallel): no tools, no MCP servers, no settings files, an identical
output note asking only for a JSON block with verdict and findings. Reviewers never saw `expected.json`. The sealed
lane was canary-tested first: asked to read a planted file and print an environment variable, it printed neither;
a control prompt answered. Scored with `evals/score.py`. v1's exact text is kept here as `SKILL-v1.md`.

| measure | v1 | v2 |
|---|---|---|
| recall (planted defects at minimum severity) | 17/23 = 0.74 | 20/23 = 0.87 |
| found at any severity | 20/23 | 23/23 |
| false alarms on 6 clean controls | 1 | 0 |
| failure-list violations | 9 in 8 cases | 0 |
| extra Critical/High on defect cases (not scored) | 44 | 25 |

v2 meets the spec's bar: better recall with no more false alarms.

Run record: model `claude-opus-5-5` for every review (read from `--output-format json` modelUsage), Claude Code
2.1.292, both versions run concurrently on 2026-10-07 from the repository directory. An instruction-file check in the
same sealed lane, from an empty directory, reported only the built-in system prompt and an empty memory scaffold: no
project or user instruction files. Every report and the exact prompt that produced it are in `reports-v1/` and
`reports-v2/`, with `SHA256SUMS`.

Limits, stated plainly:
- One run per version; model output varies run to run. n = 23.
- The spec and v2 were written by the same agent (the eval cases were not: a second agent wrote them from the spec
  alone, without seeing either skill text). The reviewer model is from the same vendor as that author.
- The scorer matches findings by location and wording; read the per-case "missed" lists before concluding a defect
  was not found.
- v1 has no inputs ledger or sensitivity gate by design, so it cannot pass the cases that test them; that is the
  feature difference being measured.
- Violations 9 vs 0 are not fully like-for-like: v1 has no ledger or seat concept, so some of its violations are
  rules it was never written to follow.
- The extra Critical/High findings (44 vs 25) are not adjudicated; "0 false alarms" covers the 6 clean controls only.
- v2's three misses are severity calibration on claims (found, rated below the key): A01 P1, C03 P1, C04 P1.
