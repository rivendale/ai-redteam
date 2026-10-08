VERDICT: try. The method directly serves goal 2 and costs nothing to test, but the post's numbers (31 → 12 minutes, 1 miss in 20 PRs) are not in the captured snapshot and were measured on their repo, so we have to measure our own savings.

WHAT IT IS: Post "Selecting tests by diff, with numbers", https://posts.example.test/test-selection-by-diff, posted 2026-09-29. The author is not named in the snapshot or meta. Read from a saved copy (work/snapshot.md, captured 2026-10-08), not live. The snapshot says "The 40 lines of Python are included below, with the exact commands and our before and after timings for 20 consecutive PRs", but none of that is in the captured text. The snapshot holds only the summary paragraph. No text in it tries to direct the reader.

CLAIMS CHECKED:
- **Method: map each test file to the source files it imports, and on a PR run only tests whose imports intersect the diff.** CONFIRMED as a description of what they did. **Load-bearing.**
- **"Useful for goal 2" (sender).** PROBABLE. Running fewer tests per PR does cut CI minutes. Whether we reach a third depends on how much of our CI time is pytest, which is untested. **Load-bearing.**
- **CI dropped from 31 to 12 minutes on a 1,900-test repo.** UNVERIFIED.
  - Evidence offered: a before/after table for 20 consecutive PRs, which is missing from the snapshot.
  - Even with the table, this is a single-repo before/after with no control.
  - It would change if our tests import broadly, for example through a shared conftest or a utils module that most tests touch. Then most PRs would select most tests.
  - Not load-bearing; the trial measures it.
- **The post includes 40 lines of Python and exact commands.** UNVERIFIED. They are not present in the captured copy. Not load-bearing.
- **One stale-map failure in 20 PRs.** UNVERIFIED. This is self-reported, and the sample is small. Not load-bearing.
- **A nightly full run catches stale-map misses.** PROBABLE. A full run does execute every test, but a miss is only caught after merge, up to a day late. This is the safety net the trial depends on. **Load-bearing.**

FIT:
- **Goal:** goal 2, "Cut CI minutes by a third this quarter".
- **Overlap:** none found. We have pytest and GitHub Actions but no test selection.
- **Burden:**
  - A script to build and refresh the import map.
  - A change to the PR workflow.
  - A new nightly full-suite job. Its minutes count against the savings.
  - Someone has to fix the main branch when nightly catches a miss.
- **Cost:** free. It is a technique we would write ourselves; no account or subscription (read 2026-10-08).
- **Risks:**
  - Import-based mapping misses dependencies that are not imports: data files, config, fixtures in conftest.py, dynamic imports, subprocess calls.
  - Misses reach main and are caught after merge.
  - The post's code has no stated license, so write our own rather than vendoring it.
  - No data leaves the machine.

NEXT ACTION: Operator (or whoever owns the CI workflows) writes an import-map selector for our pytest suite and replays it offline against the last 20 merged PRs.
- **Done when:** for each PR, we have the selected test set, whether it would have caught every failure the full run caught, and the projected PR minutes saved net of one nightly full run.
- **Stop condition:** stop if it would have missed a failing test in more than 1 of the 20 PRs, or if the projected net saving is under a third of current CI minutes.
- **Hand-off:** `harvest`, to capture the post's commands and approach once the full page, including its code and timings table, can be read.

CONFIDENCE: medium. The context file is present and the method is clear. Limits:
- The snapshot is incomplete (the code and timing table are missing).
- The author is unknown.
- The savings figures are unverified and from a different repo.
- The sender's goal-2 claim is only PROBABLE until we measure.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Selecting tests by diff, with numbers\", https://posts.example.test/test-selection-by-diff, posted 2026-09-29, author not named; saved snapshot captured 2026-10-08, code and timing table referenced but missing from the snapshot",
           "resolved": true},
  "claims": [
    {"claim": "map each test file to the source files it imports and run only tests whose imports intersect the PR diff",
     "evidence": "the post's own description of its method",
     "status": "CONFIRMED"},
    {"claim": "this is useful for goal 2 (cut CI minutes by a third)",
     "evidence": "running fewer tests per PR cuts minutes; share of our CI time spent in pytest is unmeasured",
     "status": "PROBABLE"},
    {"claim": "CI dropped from 31 to 12 minutes on a 1,900-test repo",
     "evidence": "before/after timings for 20 PRs are said to be included but are absent from the snapshot; single-repo before/after, no control",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "40 lines of Python and exact commands are included",
     "evidence": "snapshot says 'included below' but contains no code or commands",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "one stale-map failure in 20 PRs",
     "evidence": "self-reported, sample of 20, data not in snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "a nightly full run catches stale-map misses",
     "evidence": "a full run executes every test, but only after merge, up to a day late",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none found; pytest and GitHub Actions are in use but nothing selects tests",
          "burden": "an import-map script, a changed PR workflow, a new nightly full-suite job, and triaging post-merge misses",
          "risks": ["import mapping misses data files, config, conftest fixtures and dynamic imports",
                    "misses reach main and are caught only by the nightly run",
                    "post's code has no stated license; write our own rather than vendor it",
                    "nightly full run eats into the minutes saved"],
          "cost": {"price": "free", "tier": "technique, no product", "limits": "none",
                   "terms": "no license stated for the post's code", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Write an import-map test selector for our pytest suite and replay it offline against the last 20 merged PRs",
                  "owner": "operator",
                  "done_when": "for each of the 20 PRs we have the selected set, whether it caught every failure the full run caught, and projected minutes saved net of one nightly full run",
                  "stop_condition": "stop if it misses a failing test in more than 1 of 20 PRs or projected net saving is under a third of current CI minutes",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```