VERDICT: try — it targets goal 2 (cut CI minutes by a third), is MIT, free, needs no account and nothing in use overlaps it, but nothing in the item shows that it selects tests correctly or how many minutes it saves, so a bounded comparison against the full suite has to come first.

WHAT IT IS: example-org/ci-select, read from a saved snapshot captured 2026-10-08 (no commit sha recorded). It is MIT, has 2,100 stars, was last pushed 2026-10-01, is not archived, and its default branch is `main`. The README says the latest release is 2.1.0, from 2026-10-01. It is a pytest test-selection CLI: `pytest $(ci-select --diff origin/main)`.

CLAIMS CHECKED:
- **"Picks only the tests a diff affects"** (the sender's words and the README). This joins a fact to an inference, so I split it.
  - **Fact:** given a diff, it prints a list of test files. The documented usage shows this. PROBABLE.
  - **Inference:** that list holds every affected test and only those. The README never says how it maps changed code to tests (import graph, coverage data, file names). It gives no accuracy figures and no word on what it does with conftest, fixture, config or data-file changes. UNVERIFIED. The verdict rests on this claim.
- **Works with pytest.** README only. PROBABLE. The verdict rests on this.
- **License: MIT.** The README and meta.json agree. CONFIRMED. The verdict rests on this, because it passes our license rule even if we vendor it in.
- **No network access, no telemetry.** The README says so, but I did not read the source. PROBABLE. The verdict rests on this, because it would run over our code in CI.
- **"One dependency (the standard library only)".** This contradicts itself: the standard library is not a dependency. The snapshot has no pyproject or requirements file to settle it. UNVERIFIED. The verdict does not rest on this.
- **Actively maintained.** The last push and release are both from 2026-10-01, and the repo is not archived. CONFIRMED. The claim "issues answered within days" is UNVERIFIED. The 2,100 stars are a fact but are not evidence that it works. The verdict does not rest on these.
- **That it gets us to a one-third cut in CI minutes** (implied by "goal 2?"). The item offers no savings numbers. It can only cut the test step, so the saving depends on how much of our CI time pytest takes. UNVERIFIED. The trial measures this, so the verdict does not rest on it.

FIT:
- **Goal:** goal 2, cut CI minutes by a third this quarter.
- **Overlap:** none found. We run pytest on GitHub Actions with no test selection, and lychee, ruff and the rest do other jobs.
- **Burden:** one pinned pip dependency, and one change to the CI test step. The ongoing cost is trusting its selection: a missed test is a silent gap in CI. One safety net is a periodic or pre-merge full run. Note that if it prints nothing, `pytest` with no arguments runs the whole suite, which is safe but saves nothing.
- **Cost:** free and open source (MIT), with no tiers or limits, checked 2026-10-08.
- **Risks:**
  - The main risk is that a wrong selection lets regressions through.
  - The license passes our rules.
  - The install path is a version-pinned PyPI package, which is fine.
  - No telemetry or network use is claimed, but that is not verified from source.
  - Lock-in is low: removing it means one line back.

NEXT ACTION: the operator, or whoever owns CI, replays ci-select over the last 20 merged PRs. This can run locally or in one throwaway job, so it does not add CI minutes.
- **Comparison:** for each PR, compare the tests ci-select selects with the tests that actually failed or changed on the full run, and record how much test-step time the selected run takes against the full run.
- **Done when:** all 20 PRs are compared, and every miss and the median time saved are written down.
- **Stop condition:** stop and skip it if ci-select ever leaves out a test that failed on the full run, or if the projected test-step saving cannot reach about a third of total CI minutes.
- **Hand-off:** none.

CONFIDENCE: medium. The item is resolved from a snapshot and our context file is present. However, the claim the verdict depends on most, that it selects the right tests, is UNVERIFIED. The source was not read, so "no network or telemetry" is only PROBABLE.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/ci-select@main (no sha in snapshot; MIT, last push 2026-10-01, not archived, 2,100 stars, release 2.1.0)",
           "resolved": true},
  "claims": [
    {"claim": "given a diff, it prints a list of test files to run", "evidence": "README usage: pytest $(ci-select --diff origin/main)", "status": "PROBABLE"},
    {"claim": "the list is exactly the tests the diff affects (none missed)", "evidence": "README asserts it; no selection method, accuracy data, or handling of conftest/config/data changes given", "status": "UNVERIFIED"},
    {"claim": "works with pytest", "evidence": "README statement only", "status": "PROBABLE"},
    {"claim": "license is MIT", "evidence": "README and meta.json (read live at capture) agree", "status": "CONFIRMED"},
    {"claim": "no network access and no telemetry", "evidence": "README statement; source not read", "status": "PROBABLE"},
    {"claim": "one dependency (the standard library only)", "evidence": "README wording contradicts itself; no pyproject or requirements in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "actively maintained", "evidence": "meta.json: last push 2026-10-01, not archived; README: release 2026-10-01", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues answered within days", "evidence": "README statement only; issue tracker not in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "using it cuts our CI minutes by a third (sender's goal 2 question)", "evidence": "no savings figures in the item; it only shortens the test step", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none found; pytest on GitHub Actions runs the full suite today",
          "burden": "one pinned pip dependency and a change to the CI test step; a periodic full run is advisable as a safety net",
          "risks": ["a wrong selection lets regressions pass CI", "no network/telemetry claim not verified from source", "MIT passes our license rules", "pinned PyPI install, low lock-in"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Replay ci-select over the last 20 merged PRs (locally or one throwaway job) and compare its selection and test time with the full pytest run",
                  "owner": "operator",
                  "done_when": "all 20 PRs compared, with every missed test and the median test-time saving recorded",
                  "stop_condition": "stop if it ever omits a test that failed on the full run, or if the projected saving cannot reach about a third of CI minutes",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```