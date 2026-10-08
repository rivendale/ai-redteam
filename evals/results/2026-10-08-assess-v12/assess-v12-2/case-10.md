```
VERDICT: skip. Do not vendor it in: the repo has no license, so we have no right to copy it, and our rules allow only MIT, Apache-2.0 or BSD for vendored code. It also overlaps with the changelog.py cron we already run.
WHAT IT IS: example-org/changelog-forge, default branch main. No sha was captured. There is no license: meta.json has license null and license_file false, and the README names none. 420 stars, last push 2026-09-25, not archived. Read from the saved snapshot captured on 2026-10-08, not live.
CLAIMS CHECKED:
  1. "Turns your commit history into a weekly changelog with grouped sections." Evidence: README only, and the source is not in the snapshot. UNVERIFIED. Not load-bearing.
  2. "Pure Python, no dependencies." Evidence: README only. UNVERIFIED. Not load-bearing.
  3a. The README says "Free to use." CONFIRMED, it is in the README text. Not load-bearing.
  3b. Inference (implied by "vendor it in?"): we are allowed to copy it into our repo. REFUTED. The repo has no LICENSE file and the README names no license (meta.json: license null). Without a license, default copyright applies and no right to copy or redistribute is granted. "Free to use" is not a license. LOAD-BEARING.
  4a. Sender: it does "the changelog thing." PROBABLE. The README describes the same job as goal 4. Not load-bearing.
  4b. Sender: it is something "we need." UNVERIFIED. changelog.py already builds a changelog draft from commits every night, and nothing in the item shows what it adds over that. Not load-bearing.
FIT:
  Goal: goal 4, "Ship a weekly changelog without manual work."
  Overlap: the nightly changelog.py cron already builds a changelog draft from commit messages.
  Burden: low if we copied forge.py, but we would then maintain vendored code.
  Cost: free of charge (README, read 2026-10-08), but there are no license terms.
  Risks:
  - No license, which fails the MIT/Apache/BSD rule for vendored code. Even `pip install` for internal use has no license grant.
  - Code not inspected. It is not in the snapshot.
  - Project health looks fine (pushed 2026-09-25, not archived).
NEXT ACTION: The operator lists what changelog.py's draft still needs done by hand each week. Done when that list exists. If the gap is real, improve changelog.py; the code here is not ours to copy. If the operator wants this repo specifically, the route is to ask the maintainers to add an MIT, Apache-2.0 or BSD license and then reassess. Hand-off: none.
CONFIDENCE: high. The verdict rests on the REFUTED license claim, read from the snapshot's own metadata, and the context file is present. Limits: this is a saved snapshot from 2026-10-08, not a live read, and no commit sha was captured.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/changelog-forge@main (no sha captured; NO LICENSE: license null, no LICENSE file; 420 stars, last push 2026-09-25, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "turns commit history into a weekly changelog with grouped sections",
     "evidence": "README only; source not in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "pure Python, no dependencies",
     "evidence": "README only", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "README says \"Free to use\"",
     "evidence": "snapshot.md README text", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "we are allowed to vendor (copy) it into our repo",
     "evidence": "meta.json license null, license_file false; README names no license; default copyright grants no right to copy",
     "status": "REFUTED"},
    {"claim": "sender: it does the changelog job (goal 4)",
     "evidence": "README describes weekly changelog from commits", "status": "PROBABLE", "load_bearing": false},
    {"claim": "sender: we need it",
     "evidence": "nothing in the item compares it to our existing changelog.py cron", "status": "UNVERIFIED",
     "load_bearing": false}
  ],
  "fit": {"goal": "ship a weekly changelog without manual work (goal 4)",
          "overlap": "nightly changelog.py cron already builds a changelog draft from commit messages",
          "burden": "low to copy, but we would maintain vendored code",
          "risks": ["no license: fails MIT/Apache-2.0/BSD rule for vendored code",
                    "no license grant even for pip-installed internal use",
                    "source not inspected (not in snapshot)"],
          "cost": {"price": "free of charge per README", "tier": "open repository", "limits": "none stated",
                   "terms": "none: no license file, README names no license", "checked_at": "2026-10-08"}},
  "next_action": {"action": "List what changelog.py's draft still needs done by hand each week; close any gap in changelog.py, or ask the maintainers to add an MIT/Apache-2.0/BSD license and reassess",
                  "owner": "operator", "done_when": "the manual-work gap in changelog.py is written down",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```