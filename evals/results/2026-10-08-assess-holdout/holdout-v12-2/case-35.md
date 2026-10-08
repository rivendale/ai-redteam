```
VERDICT: try. The post measured only iOS, and its result does not show that a Library cache helps Android, but the cache is free and uses the Jenkins Mac mini we already have, so a short measured trial on our Android build is a cheap test against goal 1.
WHAT IT IS: Post "An incremental iOS build 3 minutes faster with a Library cache", posted 2026-09-14, read from a saved snapshot captured 2026-10-08 (https://posts.example.test/ios-library-cache). The snapshot names no author. Live resolution was not possible in this session.
CLAIMS CHECKED:
  1. "A warm incremental iOS build went from a median of 14 min to 11 min with a Library cache." Evidence: one 60-scene project, 10 runs per arm, interleaved, same Mac mini and same commit. The ranges (13-15 vs 10-12) do not overlap. The design is reasonable, but it is one project, measured by the author, with no raw data. PROBABLE. Load-bearing.
  2. "This applies to our Android build" (the sender's question). Evidence: none. The post says outright: "The Android build was not measured." UNVERIFIED, which is why the verdict is a trial and not adopt. Load-bearing.
  3. "The cache is a tarball of Library/ restored before the build." This is a description of the method, not a performance claim. CONFIRMED as stated. Not load-bearing.
  Gap to note: the post measured a *warm incremental* build. Goal 1 is the Android *release* build. If our release builds run from a clean workspace, the comparison differs, and the saving could be larger or smaller.
FIT:
  Goal: goal 1 (Android release build under 10 min), indirectly. The evidence is for iOS only.
  Overlap: the context file does not say whether Jenkins already keeps Library/ between builds. If the workspace persists on the Mac mini, a tarball cache adds nothing. Check this first.
  Burden: a restore step and a save step in the Jenkins job, plus disk space for the tarball on the Mac mini.
  Cost: free. It is a technique, with no product, account or license (checked 2026-10-08).
  Risks: a stale or corrupt cache can cause odd import errors, so key the cache on the Unity version and target platform. Library/ is platform-specific, so an iOS cache would not serve Android. No data leaves the machine, and no new party is involved.
NEXT ACTION: Operator first checks whether the Android Jenkins job already keeps Library/. If it does not, add a Library/ tarball restore to that job and run 10 interleaved builds with the cache and 10 without, on the same commit.
  Owner: operator.
  Done when: the medians and ranges for both arms are recorded.
  Stop condition: stop and remove the cache if the Android median improves by less than 1 minute, or if the ranges overlap.
  Hand-off: none.
CONFIDENCE: medium. The item reads clearly and the context file is present, but the claim that matters, transfer to Android, is UNVERIFIED. The iOS result comes from one project, measured by the author, and I worked from a saved snapshot rather than a live read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "post 'An incremental iOS build 3 minutes faster with a Library cache', posted 2026-09-14, author not named in snapshot; saved snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "warm incremental iOS build median went from 14 min to 11 min with a Library cache", "evidence": "one 60-scene project, 10 interleaved runs per arm, same Mac mini and commit, ranges 13-15 vs 10-12; author-measured, no raw data", "status": "PROBABLE"},
    {"claim": "the Library cache speeds up our Android build (sender's question)", "evidence": "post states 'The Android build was not measured.'", "status": "UNVERIFIED"},
    {"claim": "the cache is a tarball of Library/ restored before the build", "evidence": "method described in the post", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes (indirect; evidence is iOS only)",
          "overlap": "unknown whether Jenkins already keeps Library/ between builds; if it does, the cache adds nothing",
          "burden": "restore and save steps in the Jenkins Android job; disk space on the Mac mini",
          "risks": ["stale or corrupt cache causing import errors; key the cache on Unity version and platform", "Library/ is platform-specific, so iOS results may not transfer", "no data leaves the machine"],
          "cost": {"price": "free", "tier": "technique, no product", "limits": "none", "terms": "none",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Check whether the Android Jenkins job already keeps Library/; if it does not, add a Library/ tarball restore and run 10 interleaved builds with the cache and 10 without on the same commit",
                  "owner": "operator", "done_when": "medians and ranges for both arms are recorded",
                  "stop_condition": "stop and remove the cache if the Android median improves by less than 1 minute or the ranges overlap", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```