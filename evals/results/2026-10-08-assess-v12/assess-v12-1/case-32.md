VERDICT: try. It fits goal 4 and passes the license, cost and data constraints, but every claim about it comes from its own README. Run a one-week trial on real changelog.py output before adopting it.

WHAT IT IS: example-org/mdx-changelog. Read from a saved snapshot captured 2026-10-08, not live; no commit sha was recorded. License Apache-2.0, 540 stars, last push 2026-09-21, not archived, default branch `main`. Latest release is 0.9.3 (2026-09-21), installed with `pip install mdx-changelog==0.9.3`. It is a single-file Python tool.

CLAIMS CHECKED:
- **"Formats the changelog.py output nicely"** (the sender's claim). Partly holds.
  - The item takes "one entry per line, like the output of a commit-message script". That matches what changelog.py produces in kind. PROBABLE, load-bearing.
  - Whether changelog.py's actual line format parses cleanly, and whether the result counts as "nice", is not shown anywhere. UNVERIFIED, load-bearing. The trial settles this.
- **Writes a grouped markdown page with a date header.** Evidence is the README only, with no example output. PROBABLE, load-bearing.
- **Standard library only, no network access, no telemetry.** Evidence is the README only; the source is not in the snapshot. PROBABLE, load-bearing. If true, nothing leaves the machine.
- **540 stars, so it is well-used.** Popularity is not evidence of quality. Not used in the verdict.

FIT:
- **Goal:** goal 4, a weekly changelog without manual work. It formats the draft that changelog.py already builds.
- **Overlap:** changelog.py builds the draft but, per the context file, does not render a grouped page. This adds a formatting step. It does not duplicate anything in use.
- **Burden:** one pinned pip dependency and one extra command in the nightly cron. No account and no new service.
- **Cost:** free and open source, Apache-2.0, checked 2026-10-08 from the snapshot.
- **Risks:**
  - The license is Apache-2.0, which is allowed even if we vendor it in.
  - It is pre-1.0 (0.9.3), so keep the version pinned.
  - It is a small project, so health could change.
  - The no-network and no-telemetry claims have not been checked against the source.

NEXT ACTION:
- **Action:** pin `mdx-changelog==0.9.3`, run it on the last week's changelog.py output, and read its source file for any network or telemetry calls.
- **Owner:** operator.
- **Done when:** the generated page is compared with the current draft and the single source file has been read.
- **Stop condition:** stop if changelog.py's output needs reformatting by hand to parse, or if the source makes any network call.
- **Hand-off:** none.

CONFIDENCE: medium. The context file is present and the item is resolved from a snapshot. It is not high because one load-bearing claim (it parses changelog.py's actual output) is UNVERIFIED, and the other load-bearing claims rest only on the item's own README.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/mdx-changelog@main (no sha in snapshot; Apache-2.0, 540 stars, last push 2026-09-21, not archived, release 0.9.3; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "takes changelog.py-style output (one entry per line)", "evidence": "README: 'one entry per line, like the output of a commit-message script'", "status": "PROBABLE"},
    {"claim": "formats our actual changelog.py output nicely (sender)", "evidence": "no example output or format spec in the snapshot; not tested on our output", "status": "UNVERIFIED"},
    {"claim": "writes a grouped markdown page with a date header", "evidence": "README description only", "status": "PROBABLE"},
    {"claim": "standard library only, no network access, no telemetry", "evidence": "README statement; source not in snapshot", "status": "PROBABLE"},
    {"claim": "540 stars, so it is well-used", "evidence": "meta.json star count; popularity is not quality evidence", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "ship a weekly changelog without manual work (goal 4)",
          "overlap": "changelog.py builds the draft; this adds formatting and does not duplicate it",
          "burden": "one pinned pip dependency and one extra step in the nightly cron",
          "risks": ["Apache-2.0 is allowed even if vendored", "pre-1.0 (0.9.3): pin the version", "no-network and no-telemetry claims not yet checked in source", "small project, so health could change"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Pin mdx-changelog==0.9.3, run it on last week's changelog.py output, and read its single source file for network or telemetry calls",
                  "owner": "operator",
                  "done_when": "the generated page is compared with the current draft and the source file has been read",
                  "stop_condition": "stop if changelog.py output needs manual reformatting to parse, or if the source makes any network call",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```