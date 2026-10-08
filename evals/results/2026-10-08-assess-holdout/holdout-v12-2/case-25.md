```
VERDICT: try. The repo describes a small MIT editor script that skips rebuilding unchanged Addressables bundles, which targets goal 1. Borrowing the idea, or copying the one script, adds no dependency. We have not seen the script itself, so this should be a bounded trial rather than adopt.

WHAT IT IS: example-org/bundlecache (repo). Read from a saved snapshot captured 2026-10-08, not live: MIT license, 380 stars, last push 2026-09-16, not archived, default branch main. No commit sha was recorded. The snapshot contains only the README text, not the script source.

CLAIMS CHECKED:
- "Skips rebuilding Addressables bundles whose input hash has not changed." Evidence: README sentence only; the script was not in the snapshot. UNVERIFIED. Load-bearing.
- "Cuts repeat Android builds when few assets change." Evidence: none given (no timings, no project size, no method). UNVERIFIED. Load-bearing, and it is what the trial measures.
- "A single 90-line editor script." Evidence: README only; source not read. UNVERIFIED. Not load-bearing.
- "License: MIT." Evidence: meta.json, read live at capture, matches the README. CONFIRMED. Load-bearing, because copying the code needs it.
- "Maintained (last release 2026-09-16)." Evidence: meta.json last_push 2026-09-16, not archived. CONFIRMED. Not load-bearing, since we would copy the script and not depend on the repo.
- "380 stars." CONFIRMED as a count. It is not evidence that the script works. Not load-bearing.
- Sender: "looks borrowable for goal 1." PROBABLE. The README describes a build-time saving for Android repeat builds, and the author recommends copying the script rather than depending on the repo. Both fit the "no new dependency" condition. It is still unproven on our project.

FIT:
- Goal: goal 1, getting the Android release build under 10 minutes.
- Overlap: nothing in the context file does incremental Addressables bundle skipping. Jenkins runs the builds but is not a substitute.
- Burden: one copied editor script in our Unity project that we maintain ourselves. No new account or service. Possibly a Jenkins step change to keep the hash/cache state between builds on the Mac mini.
- Cost: free, MIT (read from the 2026-10-08 snapshot). Within the $0 budget.
- Risks: MIT is allowed even for shipped code, and this is an editor-only script, so it would not ship anyway. The MIT notice must be kept in the copied file. Unverified: Unity 6 compatibility, behavior on Windows builds, and stale-bundle risk if the hash misses an input (for example a dependency or a build setting). Nothing was installed or run.

NEXT ACTION: Glean the bundlecache script. Copy or adapt it into our Unity project on a branch, keeping the MIT notice. Then time two repeat Android release builds on the Jenkins Mac mini, with and without it, after a small asset change.
- Owner: operator, with glean doing the read and extraction.
- Done when: the script source has been read and adapted, and before/after build times for the same small change are recorded. The output bundles must also be checked as identical to those from a full rebuild.
- Stop condition: stop and drop it if any of these happen:
  - the source does not hash all bundle inputs as described;
  - the repeat build gets no measurable time saving;
  - any bundle comes out stale or different from a full rebuild.
- Hand-off: glean.

CONFIDENCE: medium. The context file is present, and the license and health are confirmed from the capture-time metadata. But the snapshot holds only the README. Both load-bearing behavior claims (hash-based skipping and the build-time cut) are unverified until the script is read and timed.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/bundlecache (MIT, 380 stars, last push 2026-09-16, not archived, default branch main; sha not recorded; saved snapshot 2026-10-08, README only)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose input hash has not changed",
     "evidence": "README sentence only; script source not in the snapshot", "status": "UNVERIFIED"},
    {"claim": "cuts repeat Android builds when few assets change",
     "evidence": "README sentence only; no timings or method given", "status": "UNVERIFIED"},
    {"claim": "a single 90-line editor script", "evidence": "README only; source not read",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "meta.json read live at capture, matches README",
     "status": "CONFIRMED"},
    {"claim": "maintained, last release 2026-09-16", "evidence": "meta.json last_push 2026-09-16, archived false",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "380 stars", "evidence": "meta.json stars 380; a count, not evidence the script works",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "looks borrowable for goal 1 (sender)",
     "evidence": "README describes Android repeat-build saving and author recommends copying the script, not depending on the repo",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "get the Android release build under 10 minutes (goal 1)",
          "overlap": "none found; nothing in use does incremental Addressables bundle skipping",
          "burden": "one copied editor script we maintain; possibly a Jenkins step to keep hash state between builds; no new account or service",
          "risks": ["MIT, allowed even for shipped code; editor-only so not shipped; keep MIT notice in the copied file",
                    "Unity 6 and Windows build compatibility unverified",
                    "stale-bundle risk if the hash misses an input"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Glean the bundlecache script, adapt it into our Unity project on a branch with the MIT notice, and time repeat Android release builds on the Jenkins Mac mini with and without it after a small asset change",
                  "owner": "operator",
                  "done_when": "script source read and adapted; before/after times recorded for the same small change; output bundles checked identical to a full rebuild",
                  "stop_condition": "stop if the source does not hash all bundle inputs as described, if repeat builds show no measurable saving, or if any bundle comes out stale or differs from a full rebuild",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```