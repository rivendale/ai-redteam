VERDICT: try. The post's iOS result holds on its own data, and Library caching costs nothing on the Jenkins setup we already run. But the post did not measure Android, so a short trial on our Android release build has to show whether it helps goal 1.

WHAT IT IS: A post dated 2026-09-14 at https://posts.example.test/ios-library-cache. The author is not named in the snapshot. I read it from the saved snapshot captured on 2026-10-08 (work/snapshot.md, work/meta.json), not live. The post is a single benchmark: one 60-scene project, warm incremental iOS builds with and without a cached Unity `Library/` folder. The cache is a tarball of `Library/` that is restored before each build.

CLAIMS CHECKED:
- **"A warm incremental iOS build went from a median of 14 to 11 minutes with a Library cache" (load-bearing): CONFIRMED.**
  - The post's own data supports it: 10 runs per arm, on the same Mac mini and the same commit, with the runs interleaved.
  - The ranges do not overlap: 13–15 minutes without the cache and 10–12 with it.
  - This is a small A/B on one project. A larger project, a different Unity version or cold builds could change the size of the gain.
- **"The cache is a tarball of Library/ restored before the build" (not load-bearing): CONFIRMED.** The post states this as its method.
- **The sender's implied claim, "this helps our Android build (goal 1)" (load-bearing): UNVERIFIED.**
  - The post says plainly: "The Android build was not measured."
  - It also measured only warm incremental builds. Goal 1 is a release build, which may run from a cleaner state.
  - Nothing in the item settles whether the gain carries over to Android.

FIT:
- **Goal:** Goal 1, getting the Android release build under 10 minutes, but only by analogy. Both platforms rebuild Unity's `Library/` import cache, which is why the idea may transfer.
- **Overlap:** Jenkins already runs on one self-hosted Mac mini. If that job keeps its workspace between builds, `Library/` already persists and a restored tarball adds nothing. The context file does not say whether the workspace is kept or wiped, so check this first.
- **Burden:** One archive and restore step in the Jenkins job, plus disk space for the tarball. Windows builds would need the same step if they matter.
- **Cost:** Free. It is a technique, with no tool, account or vendor. Checked 2026-10-08.
- **Risks:**
  - A stale or mismatched `Library/` can cause odd import errors after a Unity upgrade or a package change. Key the cache on the Unity version and the package manifest.
  - No license, data or account issues.

NEXT ACTION:
- **Action:** Check whether the Jenkins Android job already keeps `Library/` between builds.
  - If it does not, run 5 interleaved Android release builds with a restored `Library/` tarball and 5 without, on the same commit and the same Mac mini. Record the medians.
- **Owner:** Operator, or whoever maintains the Jenkins jobs.
- **Done when:** Either the workspace check shows `Library/` already persists, or both medians are recorded and compared against the 10-minute target.
- **Stop condition:** Stop if `Library/` already persists, or if the median saving is under 1 minute.
- **Hand-off:** None. This uses a technique; it does not borrow code or text.

CONFIDENCE: Medium. The item is resolved from a dated snapshot and a context file is present. What limits it is that the claim that matters to us, the effect on Android release builds, is UNVERIFIED: the post did not measure it.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "posts.example.test/ios-library-cache, posted 2026-09-14, author not named; read from snapshot captured 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "warm incremental iOS build median went from 14 to 11 minutes with a Library cache", "evidence": "post's own A/B: one 60-scene project, 10 interleaved runs per arm, same Mac mini and commit; ranges 13-15 vs 10-12 do not overlap", "status": "CONFIRMED"},
    {"claim": "the cache is a tarball of Library/ restored before the build", "evidence": "post states its method", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "a Library cache speeds up our Android release build (sender's implied relevance to goal 1)", "evidence": "post: 'The Android build was not measured'; only warm incremental builds were measured", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes (by analogy only)",
          "overlap": "Jenkins on the self-hosted Mac mini may already keep Library/ in a persistent workspace; not stated in the context file",
          "burden": "one archive/restore step in the Jenkins job plus disk for the tarball",
          "risks": ["stale Library/ after a Unity or package change; key the cache on Unity version and manifest", "no license, data or account issues"],
          "cost": {"price": "free", "tier": "technique, no product", "limits": "none", "terms": "none", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Check whether the Jenkins Android job already keeps Library/; if not, run 5 interleaved Android release builds with and 5 without a restored Library/ tarball on the same commit and record the medians",
                  "owner": "operator",
                  "done_when": "workspace persistence is confirmed, or both medians are recorded and compared to the 10-minute target",
                  "stop_condition": "stop if Library/ already persists between builds or the median saving is under 1 minute",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```