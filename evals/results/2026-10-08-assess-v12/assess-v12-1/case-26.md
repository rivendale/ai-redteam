VERDICT: try. The post describes a free, self-built way to cut PR test time that serves goal 2 directly, but its numbers are self-reported and the code and timings were not in our capture, so we should prove the saving on our own repo in a bounded shadow trial before relying on it.

WHAT IT IS: Blog post "Selecting tests by diff, with numbers", posted 2026-09-29 at https://posts.example.test/test-selection-by-diff. I worked from a saved copy (work/snapshot.md, captured 2026-10-08), not a live read. The author is not named in the capture. The post says it includes 40 lines of Python, the exact commands and a timings table for 20 PRs, but none of that is in the captured text. No license is stated for the code.

CLAIMS CHECKED:
- **"On our repo (1,900 tests) CI dropped from 31 to 12 minutes."**
  - Evidence offered: before/after timings for 20 consecutive PRs, which the post says are included but are absent from the snapshot.
  - Status: UNVERIFIED. Nothing we hold settles it. The verdict rests on this claim, and the trial exists to test it.
- **"40 lines of Python" are enough to build the import map and selection.**
  - Evidence: the code itself, which is not in the capture.
  - Status: UNVERIFIED. Not load-bearing, since we would write our own version anyway.
- **"One stale-map failure in 20 PRs; a nightly full run catches it."**
  - Evidence: the authors' own disclosure of a cost, which runs against their interest.
  - Status: PROBABLE for their repo. Load-bearing, because the trade-off is only acceptable if missed failures are rare and get caught.
- **Sender: "useful for goal 2". This splits into two parts:**
  - (a) The technique targets CI test minutes, which is goal 2 ("cut CI minutes by a third"). Status: CONFIRMED by the post's method and our context file.
  - (b) It would cut *our* CI minutes by a third. Status: UNVERIFIED, and not load-bearing. It depends on:
    - what share of our CI minutes is pytest;
    - how much of our suite is reached through static imports, rather than conftest fixtures, data files or dynamic imports;
    - the extra minutes the nightly full run adds back.

FIT:
- **Goal:** goal 2 (cut CI minutes by a third).
- **Overlap:** we have nothing that does test selection. pytest and GitHub Actions are the substrate it would run on, not a competing tool.
- **Burden:**
  - one small script we would own;
  - a test-to-import map that has to stay fresh;
  - a new nightly full-suite job in Actions.
- **Cost:** free, with no account and no service. Read from the snapshot on 2026-10-08.
- **Risks:**
  - Missed regressions between PR and nightly: the post reports 1 in 20 PRs.
  - Static import maps miss conftest, fixture, data-file and dynamic-import dependencies.
  - The post's code has no stated license. Re-implement the idea rather than copying the code into our repo, to stay within our MIT/Apache/BSD rule.
  - No data leaves the machine.

NEXT ACTION:
- **Action:** harvest the method from the post, then write our own import-map selector. Run it in shadow mode on PRs for 20 PRs: compute the selected subset, but still run the full suite. Record the projected minutes and any test that failed but was not selected.
- **Owner:** operator, or whoever owns CI.
- **Done when:** 20 PRs are logged with the full-suite minutes, the projected subset minutes and the count of missed failures.
- **Stop condition:** stop if either of these happens:
  - projected total CI minutes, including the added nightly run, fall by less than a third;
  - the selector misses more than one real failure in the 20 PRs.
- **Hand-off:** harvest.

CONFIDENCE: medium. The item is a saved snapshot whose code and timings table are not in the capture, the author is unnamed, and the load-bearing claims are UNVERIFIED or self-reported. The context file is present.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "post 'Selecting tests by diff, with numbers', posted 2026-09-29, https://posts.example.test/test-selection-by-diff (author not named; read from snapshot captured 2026-10-08; code and timings table not in capture; no code license stated)",
           "resolved": true},
  "claims": [
    {"claim": "on their repo (1,900 tests) CI dropped from 31 to 12 minutes", "evidence": "before/after timings for 20 PRs said to be included, but absent from the snapshot", "status": "UNVERIFIED"},
    {"claim": "40 lines of Python implement the import-map selection", "evidence": "code not present in the captured snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "one stale-map failure in 20 PRs, caught by a nightly full run", "evidence": "authors' own disclosure of a cost", "status": "PROBABLE"},
    {"claim": "sender: the technique targets CI test minutes, which is goal 2", "evidence": "post's method plus context file goal 2 (cut CI minutes by a third)", "status": "CONFIRMED"},
    {"claim": "sender (inference): it would cut our CI minutes by a third", "evidence": "none for our repo; depends on pytest share of CI minutes, static-import coverage, and nightly run overhead", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none; no test selection in use today, it would run on our existing pytest and GitHub Actions",
          "burden": "one self-owned script, an import map to keep fresh, one new nightly full-suite job",
          "risks": ["missed regressions between PR and nightly (post reports 1 in 20 PRs)",
                    "static import maps miss conftest, fixture, data-file and dynamic-import dependencies",
                    "post code has no stated license; re-implement rather than vendor to stay within MIT/Apache/BSD"],
          "cost": {"price": "free", "tier": "none (technique in a public post)", "limits": "none", "terms": "no license stated for the included code",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Harvest the method, write our own import-map selector, and run it in shadow mode (full suite still runs) on 20 PRs, logging projected minutes and any failing test it would have skipped",
                  "owner": "operator",
                  "done_when": "20 PRs logged with full-suite minutes, projected subset minutes and missed-failure count",
                  "stop_condition": "stop if projected total CI minutes (including the nightly full run) fall by less than a third, or the selector misses more than one real failure in 20 PRs",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```