VERDICT: try. Goal 1 is the Android release build, and the post measured only iOS, so its saving does not transfer on its own. But a Library cache costs nothing and needs no new account or service, so a short timed trial on our Jenkins Android job will settle whether it helps.

WHAT IT IS: A blog post, "An incremental iOS build 3 minutes faster with a Library cache", posted 2026-09-14, at https://posts.example.test/ios-library-cache. I read it from a saved snapshot captured 2026-10-08 (`work/snapshot.md`, `work/meta.json`), not live. The snapshot gives no author.

CLAIMS CHECKED:
- **"A warm incremental iOS build went from a median of 14 minutes to 11 with a Library cache."** PROBABLE, and the verdict rests on it.
  - The design is sound: one 60-scene project, 10 runs per arm, same Mac mini, same commit, runs interleaved.
  - The ranges do not overlap (13–15 against 10–12).
  - The limits: it is one project, the raw timings are not shown, and only warm incremental builds were measured. Clean or release builds were not.
- **The sender's implied claim that this applies to our Android build.** UNVERIFIED, and the verdict rests on it.
  - The post says "The Android build was not measured."
  - Our goal is a *release* build, and the post measured *warm incremental* builds. Nothing in the post shows the saving carries over to either Android or release builds.
- **"The cache is a tarball of Library/ restored before the build."** CONFIRMED as the post's description of its own method. The verdict does not rest on it.

FIT:
- **Goal:** Goal 1, getting the Android release build under 10 minutes. The post does not give our current Android time, so we cannot tell whether a saving of about 3 minutes would close the gap.
- **Overlap:** There may be none, or we may already have this. Jenkins runs on one self-hosted Mac mini. If the job keeps its workspace between runs, `Library/` already stays warm, and a tarball cache adds nothing. The context file does not say, so someone must check the Jenkins job before changing anything.
- **Burden:** One restore step and one save step in the Jenkins Android job, plus disk space on the Mac mini for the tarball.
- **Cost:** Free. It is a technique, with no product, tier or terms (checked 2026-10-08).
- **Risks:**
  - A stale or incompatible `Library/` after a Unity 6 upgrade or a package change could cause odd build results. Key the cache to the Unity version and the lockfile.
  - The tarball takes disk space on the only build machine.
  - No license issue, no new account, no data leaving our machines.

NEXT ACTION: The operator (or whoever owns the Jenkins job) does two things:
1. Check whether the Android release job wipes `Library/` between runs.
2. If it does, run 10 interleaved builds each with and without a restored `Library/` tarball, on the same commit, and compare the medians.

- **Done when:** both medians are recorded, along with the current Android release build time.
- **Stop condition:** stop if the job already keeps `Library/` between runs, or if the cached median saves less than 1 minute.
- **Hand-off:** none.

CONFIDENCE: Medium. The item is resolved only from a saved snapshot, and the claim the verdict depends on (that the saving transfers to Android release builds) is UNVERIFIED. We also don't know our current Android build time or whether Jenkins already keeps `Library/` between runs.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "posts.example.test/ios-library-cache, posted 2026-09-14, author not given; read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "a warm incremental iOS build went from a median of 14 min to 11 min with a Library cache",
     "evidence": "10 interleaved runs per arm, same Mac mini, same commit, one 60-scene project; ranges 13-15 vs 10-12; raw data not shown",
     "status": "PROBABLE"},
    {"claim": "the saving applies to our Android release build (sender's question)",
     "evidence": "post: 'The Android build was not measured'; only warm incremental builds were timed, not release builds",
     "status": "UNVERIFIED"},
    {"claim": "the cache is a tarball of Library/ restored before the build",
     "evidence": "post's own method description",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes",
          "overlap": "possibly none, or already in effect: if the Jenkins job on the self-hosted Mac mini keeps its workspace, Library/ is already warm",
          "burden": "a restore step and a save step in the Jenkins Android job; disk space on the Mac mini",
          "risks": ["stale Library/ after a Unity or package change; key the cache to the Unity version and lockfile",
                    "tarball disk use on the only build machine",
                    "no license, account or data-sharing risk"],
          "cost": {"price": "free", "tier": "technique, not a product", "limits": "none",
                   "terms": "none", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Check whether the Jenkins Android release job wipes Library/; if it does, time 10 interleaved builds each with and without a restored Library/ tarball on the same commit",
                  "owner": "operator",
                  "done_when": "both medians and the current Android release build time are recorded",
                  "stop_condition": "stop if Library/ already persists between runs or the cached median saves less than 1 minute",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```