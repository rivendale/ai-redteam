VERDICT: try. It targets goal 2 (cut CI minutes by a third), is MIT, free, and adds no account. But the snapshot does not show how it decides which tests a diff affects or how much time it saves, so it should earn its place in a bounded shadow trial against the full suite.

WHAT IT IS: repo example-org/ci-select, default branch main, commit sha not captured. MIT license, 2,100 stars, last push 2026-10-01, not archived. Read from a saved snapshot captured 2026-10-08 (work/meta.json, work/snapshot.md), not live. The snapshot is the README text only; no source code was captured.

CLAIMS CHECKED:
- **"Picks only the tests a diff affects"** (README, and the sender's words): UNVERIFIED, load-bearing.
  - The README shows usage (`pytest $(ci-select --diff origin/main)`) but not the method. Nothing says how it traces dependencies, such as import graphs, coverage maps, conftest/fixture changes, data files or dynamic imports.
  - Nothing reports a missed-test rate. A selector that misses affected tests is the main risk here.
- **"It serves goal 2"** (the sender's question, i.e. cutting CI minutes by a third): UNVERIFIED, load-bearing.
  - The item gives no benchmark or savings figure. The fact part is that it reduces the tests run per diff (as described). The inference that this yields a one-third cut is unsupported.
  - The savings depend on our suite's shape: how much of our CI time pytest takes, and how localized our diffs are.
- **"No network access. No telemetry."** (README): PROBABLE, load-bearing for the data constraint.
  - This is a plain statement from the README. It is plausible for a pure-Python selector, but the source was not in the snapshot to check.
- **"Pure Python, one dependency (the standard library only)"** (README): PROBABLE, not load-bearing.
  - The wording contradicts itself: the standard library is not a dependency. The likely reading is "no third-party dependencies."
- **"License: MIT"**: CONFIRMED by meta.json. Not load-bearing beyond meeting our license rule.
- **"Last release 2026-10-01", "2,100 stars"**: CONFIRMED by meta.json (last push 2026-10-01, 2,100 stars). Not load-bearing; popularity is not evidence that it works.
- **"Issues answered within days"**: UNVERIFIED, not load-bearing. No issue data was captured.

FIT:
- **Goal:** goal 2, cut CI minutes by a third.
- **Overlap:** none found. We run pytest in GitHub Actions and have no test-selection tool. It complements pytest rather than replacing anything.
- **Burden:** one pinned pip install in CI (`ci-select==2.1.0`) and a changed pytest invocation. We would also need a safety net, such as a periodic or merge-time full run, which adds some workflow logic.
- **Cost:** free and open source (MIT), as read 2026-10-08. No tiers and no account.
- **Risks:**
  - Silently skipped affected tests could let regressions through.
  - It only works with pytest, which matches our stack.
  - MIT is fine even for vendoring.
  - It installs from PyPI at a pinned version, not a moving branch.
  - It claims no telemetry and no network access; this is unverified in source.
  - Project health looks active (push 7 days before capture).

NEXT ACTION:
- **Action:** Run it in shadow mode in the GitHub Actions workflow for 2 weeks. On each PR, record which tests ci-select selects, while still running the full pytest suite. Compare the selected set's runtime with the full run, and check whether any test that failed in the full run was left unselected.
- **Owner:** operator (or whoever owns the CI workflow).
- **Done when:** 2 weeks of PRs are logged with the estimated minutes saved and the count of missed failing tests.
- **Stop condition:** stop if it ever leaves out a test that failed in the full run, or if the estimated saving is under one third of the pytest CI minutes.
- **Hand-off:** none.

CONFIDENCE: medium. The item is resolved and the context file is present. Confidence is limited because the load-bearing claims (accurate selection and the size of the savings) are UNVERIFIED, the snapshot holds only README text with no source, and no commit sha was captured.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/ci-select@main (sha not captured; MIT, 2,100 stars, last push 2026-10-01, not archived; saved snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "picks only the tests a diff affects", "evidence": "README usage line only; no selection method or missed-test rate given", "status": "UNVERIFIED"},
    {"claim": "using it would serve goal 2 (cut CI minutes by a third)", "evidence": "sender's inference; item gives no benchmark or savings figure", "status": "UNVERIFIED"},
    {"claim": "no network access and no telemetry", "evidence": "README statement; source not in snapshot", "status": "PROBABLE"},
    {"claim": "pure Python with no third-party dependencies", "evidence": "README says 'one dependency (the standard library only)', self-contradictory wording", "status": "PROBABLE", "load_bearing": false},
    {"claim": "MIT license", "evidence": "meta.json license: MIT", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "last release 2026-10-01 with 2,100 stars", "evidence": "meta.json last_push 2026-10-01, stars 2100", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues answered within days", "evidence": "README statement; no issue data captured", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third (goal 2)",
          "overlap": "none found; complements pytest in GitHub Actions",
          "burden": "one pinned pip install in CI, changed pytest invocation, plus a periodic full-suite safety run",
          "risks": ["silently skipped affected tests could let regressions through",
                    "no-network/no-telemetry claim not verified in source",
                    "MIT, pinned PyPI install, active project"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated; pytest only", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Run ci-select in shadow mode in GitHub Actions for 2 weeks alongside the full pytest suite, logging selected-set runtime vs full runtime and any failing tests it did not select",
                  "owner": "operator",
                  "done_when": "2 weeks of PRs logged with estimated minutes saved and count of missed failing tests",
                  "stop_condition": "stop if it ever omits a test that failed in the full run, or if estimated savings are under one third of pytest CI minutes",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```