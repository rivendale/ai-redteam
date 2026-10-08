```
VERDICT: try, because borrowing one MIT editor script's hash-skip idea could serve goal 1 (Android release build under 10 minutes) without adding a dependency, but nothing in the item shows how much time it saves.
WHAT IT IS: example-org/bundlecache on GitHub, read from a saved snapshot captured 2026-10-08 (no commit sha recorded). MIT, last push and release 2026-09-16, not archived, default branch main, 380 stars. The README describes a single 90-line Unity editor script that skips rebuilding Addressables bundles whose input hash has not changed. Only the README text was captured. The script itself was not read.
CLAIMS CHECKED:
  - "Skips rebuilding Addressables bundles whose input hash has not changed": the README says so, but the code is not in the snapshot. UNVERIFIED. The verdict rests on this.
  - "Cuts repeat Android builds when few assets change": no timings, project size or method are given. UNVERIFIED. The verdict rests on this, and it is why this is a try and not an adopt.
  - "A single 90-line editor script": README statement only. UNVERIFIED. Not load-bearing.
  - "The author recommends copying the one script rather than depending on the repo": stated in the README. CONFIRMED. This fits the sender's "no new dependency" condition.
  - License MIT: meta.json and README agree. CONFIRMED.
  - 380 stars, last push 2026-09-16: CONFIRMED as facts. They show the project is alive but are not evidence that the script works. Not load-bearing.
  - Sender: "looks borrowable for goal 1": PROBABLE. The idea targets repeat Android builds. The context file does not say whether we use Addressables or whether Jenkins keeps a warm workspace between release builds. If release builds are clean builds, there is no cache to skip against.
FIT:
  - Goal: goal 1, getting the Android release build under 10 minutes.
  - Overlap: nothing in our tool list does bundle-level build skipping. Unity's own Addressables build cache may already cover part of this. Check that before writing anything.
  - Burden: one editor script we own and maintain, plus a persisted hash cache on the Jenkins Mac mini. No new account or service.
  - Cost: free (MIT), checked 2026-10-08. $0, so within budget.
  - Risks:
    - MIT is allowed for shipped code, and an editor script does not ship anyway.
    - Main risk is correctness. If the input hash misses a dependency, an import setting or the Unity version, the build skips a bundle it should rebuild and ships stale assets.
    - The cache must also be safe on the Windows builds.
    - No telemetry or data egress is described, but the code was not read.
NEXT ACTION: Run glean on example-org/bundlecache's script to extract the hash-skip approach into our own Addressables editor step. Then time two Jenkins Android release builds (one changed asset) against today's baseline.
  - Owner: operator (build owner).
  - Done when: both timings are recorded and a forced-change test confirms the changed bundle is rebuilt.
  - Stop if: we do not build with Addressables, release builds start from a clean workspace, or the saving is under 1 minute per build.
  - Hand-off: glean.
CONFIDENCE: medium. The item is resolved and the context file is present. But the load-bearing claims (that it works, and that it saves time) are UNVERIFIED, because only the README was captured. Our use of Addressables and the Jenkins workspace policy are also unknown.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/bundlecache@main (sha not recorded; MIT, last push 2026-09-16, not archived, 380 stars; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose input hash has not changed",
     "evidence": "README statement only; the script's code is not in the snapshot", "status": "UNVERIFIED"},
    {"claim": "cuts repeat Android builds when few assets change",
     "evidence": "README statement; no timings, project size or method given", "status": "UNVERIFIED"},
    {"claim": "a single 90-line editor script", "evidence": "README statement; code not captured",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "author recommends copying the one script rather than depending on the repository",
     "evidence": "stated in the README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "meta.json and README agree", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "380 stars and last push 2026-09-16", "evidence": "meta.json read live at capture; shows activity, not that the script works",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "sender: the approach looks borrowable for goal 1",
     "evidence": "the idea targets repeat Android builds, but the context file does not say whether we use Addressables or whether Jenkins keeps a warm workspace",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes",
          "overlap": "nothing in our tool list does bundle-level skipping; Unity's own Addressables build cache may already cover part of it",
          "burden": "one editor script we own and maintain plus a persisted hash cache on the Jenkins Mac mini; no new account or service",
          "risks": ["MIT, allowed and the editor script is not shipped",
                    "an incomplete input hash ships stale bundles",
                    "cache must behave the same on macOS and Windows builds",
                    "code not read, so no telemetry check was possible"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Glean the hash-skip approach from the script into our own Addressables editor step, then time two Jenkins Android release builds (one changed asset) against today's baseline",
                  "owner": "operator",
                  "done_when": "both timings are recorded and a forced-change test confirms the changed bundle is rebuilt",
                  "stop_condition": "stop if we do not use Addressables, if release builds start from a clean workspace, or if the saving is under 1 minute per build",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```