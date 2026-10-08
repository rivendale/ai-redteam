VERDICT: try. Picking tests by which source files changed directly serves goal 2 (cut CI minutes by a third), and the method is plain enough to test on our own repo for $0. However, the post's code and timing table are missing from the saved copy, so its headline number cannot be checked.

WHAT IT IS: A blog post, "Selecting tests by diff, with numbers," posted 2026-09-29 at https://posts.example.test/test-selection-by-diff. The saved copy does not name an author. I read the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not the live page. The snapshot says "The 40 lines of Python are included below, with the exact commands and our before and after timings for 20 consecutive PRs," but nothing follows that sentence. The code, commands and timing table were not captured.

CLAIMS CHECKED:
- **Method: map each test file to the source files it imports, and on a PR run only the tests whose imports overlap the diff.** CONFIRMED as a description of what they did. The idea is clear and sound for import-driven Python code. It cannot see changes to conftest.py fixtures, data files, config files or dynamic imports, which is the likely cause of the stale-map failure the post admits to.
- **"On our repo (1,900 tests) CI dropped from 31 to 12 minutes."** UNVERIFIED, and the verdict rests on it. The evidence is a table of 20 consecutive PRs on one repo, and that table is not in the saved copy. Even with the table, it is one repo, no control for PR size, and wall-clock time rather than billed minutes.
- **Inference: the same saving would carry over to our repo.** UNVERIFIED. It depends on how modular our code is and how much of it is shared. A change to a widely imported module selects most of the suite.
- **"Cost: one stale-map failure in 20 PRs; a nightly full run catches it."** PROBABLE as the post's own report. It is a small sample, and the failure reaches main and stays there until the nightly run.
- **"The 40 lines of Python are included below."** UNVERIFIED. The code is missing from the captured copy, so it cannot be read or license-checked.
- **Sender: "seems useful for goal 2."** PROBABLE. The goal fits, but the size of the saving is unproven for us.

FIT:
- **Goal:** goal 2, "Cut CI minutes by a third this quarter." The claimed 31 to 12 minute drop is about 61%, well past a third, if it holds here.
- **Overlap:** Nothing in our context does test selection. It would build on pytest and GitHub Actions, which we already use. It does not replace lychee or anything else.
- **Burden:**
  - a script that builds and refreshes the import map
  - a PR job that calls pytest with the selected tests
  - a nightly full run, which adds roughly one full suite's minutes per day; count that against the saving
  - keeping the map current
- **Cost:** free. It is an idea plus about 40 lines of code. No account and no data leaves our systems. Checked 2026-10-08 from the snapshot.
- **Risks:**
  - Missed failures that merge to main until the nightly run catches them.
  - Blind spots for changes outside imports (fixtures, data files, config).
  - The post's code has no license visible, so do not vendor it. Write our own from the idea, which is about 40 lines.

NEXT ACTION: Write an import-map test selector for our repo and run it in shadow mode on the next 20 PRs. Each PR still runs the full suite, and we record what the selector would have chosen and how long that would have taken.
- **Owner:** operator, or a CI maintainer they choose.
- **Done when:** for 20 PRs we have the minutes for the selected run versus the full run, and a list of every failure the selection would have missed.
- **Stop condition:**
  - stop if the projected saving, net of a nightly full run, is under a third of current CI minutes, or
  - stop if the selection misses a real failure in more than one of the 20 PRs.
- **Hand-off:** `harvest`, to take the method from the post. If the full post with code is fetched later, check that code's license before copying any of it.

CONFIDENCE: medium. The context file is present and the method is clear. The claim the verdict rests on (31 to 12 minutes) is UNVERIFIED because its evidence table and code are missing from the saved copy. I worked only from the 2026-10-08 snapshot, and the author is unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Selecting tests by diff, with numbers\", posted 2026-09-29, author not named, https://posts.example.test/test-selection-by-diff (saved snapshot 2026-10-08; code and timing table referenced but not captured)",
           "resolved": true},
  "claims": [
    {"claim": "map each test file to the source files it imports and run only tests whose imports intersect the PR diff",
     "evidence": "snapshot text describes the method; import-only mapping misses fixture, data-file, config and dynamic-import changes",
     "status": "CONFIRMED"},
    {"claim": "on their repo (1,900 tests) CI dropped from 31 to 12 minutes",
     "evidence": "a 20-PR before/after table the post says is included, but it is absent from the captured snapshot; single repo, no control for PR size",
     "status": "UNVERIFIED"},
    {"claim": "the same saving would carry over to our repo",
     "evidence": "inference only; depends on our module structure and shared imports",
     "status": "UNVERIFIED"},
    {"claim": "cost is one stale-map failure in 20 PRs, caught by a nightly full run",
     "evidence": "post's own report, small sample; failure reaches main until the nightly run",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "40 lines of Python with exact commands are included",
     "evidence": "the snapshot ends before any code; cannot be read or license-checked",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "sender: useful for goal 2",
     "evidence": "goal 2 is cutting CI minutes by a third; the method targets CI minutes, but the size of the saving is unproven here",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "Cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none; would build on existing pytest and GitHub Actions",
          "burden": "import-map script, a selective PR job, a nightly full run (adds about one full suite per day), map upkeep",
          "risks": ["missed failures merge to main until the nightly run",
                    "blind to non-import dependencies (conftest fixtures, data files, config)",
                    "post's code has no visible license; write our own rather than vendor"],
          "cost": {"price": "free", "tier": "n/a (method in a blog post)", "limits": "none",
                   "terms": "no license visible for the post's code", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Write an import-map test selector and run it in shadow mode on the next 20 PRs alongside the full suite, recording selected-run minutes and any failures it would have missed",
                  "owner": "operator",
                  "done_when": "20 PRs have selected-vs-full minutes and a list of missed failures",
                  "stop_condition": "stop if the projected saving net of a nightly full run is under a third of current CI minutes, or if selection misses a real failure in more than 1 of 20 PRs",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```