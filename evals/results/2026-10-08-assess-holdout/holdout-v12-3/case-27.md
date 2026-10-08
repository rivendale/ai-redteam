VERDICT: try. The 60% figure is unverified because the test games and the measurement script are private, so measure it on our own build before adopting. The trial should also check that it doesn't push the Android release build past the 10-minute goal.

WHAT IT IS: example-org/apkshrink, a Unity Package Manager plugin. MIT licence, 290 stars, last push 2026-09-23, not archived, default branch `main`. This was read from a saved snapshot captured 2026-10-08 (work/meta.json, work/snapshot.md), not live. No commit sha was recorded, and no source code was in the snapshot.

CLAIMS CHECKED:
- **"Cuts your Android APK size by 60%" (load-bearing): UNVERIFIED.**
  - The only evidence is the README line "60% smaller APKs on average across our test games."
  - The README itself says the test games and measurement script are private and not in the repo.
  - There is no sample size, no baseline settings (for example, whether texture compression and code stripping were already on), and no spread. An average across unnamed games says little about ours.
  - What would change this: a reproducible benchmark, or our own before/after measurement.
- **"Works by re-encoding textures and stripping unused code" (not load-bearing): PROBABLE.** This is the README's own description. No source was available to confirm it.
- **"Install from the Unity Package Manager" (not load-bearing): PROBABLE.** This is consistent with our Unity 6 stack, but it is the README's statement only.
- **Licence is MIT (load-bearing): CONFIRMED** by meta.json and the README.
- **Maintained (not load-bearing): CONFIRMED.** The last push and release were 2026-09-23, and the repo is not archived. The 290 stars is a true count, but it is not evidence that the size claim holds.

FIT:
- **Goal:**
  - The sender mentions a size budget, but the context file lists no APK-size goal. That goal is the sender's word only. The operator may want to add it to the context file.
  - It touches goal 1 (Android release build under 10 minutes), but possibly in the wrong direction: re-encoding textures at build time can add build time.
- **Overlap:** Unity 6 is already in use and has its own texture compression settings and managed code stripping. The trial must compare against those settings properly configured, not against defaults, or any gain is overstated.
- **Burden:** one package added to the project, plus one more step in the Jenkins Android build on the Mac mini. It must also work on Windows builds.
- **Cost:** free (MIT, open source, read 2026-10-08). No account or subscription is mentioned.
- **Risks:**
  - The MIT licence is allowed even for code we ship.
  - Aggressive code stripping can remove code that is reached only by reflection, which would cause runtime crashes. That would work against goal 2 (crash noise).
  - Re-encoded textures may lower visual quality.
  - No telemetry or network use is stated, but this cannot be checked without the source.

NEXT ACTION: On a branch, build the Android release once with Unity's own stripping and texture compression tuned, and once with apkshrink added. Record APK size and build time for each, then smoke-test the apkshrink build.
- Owner: whoever owns the Jenkins Android build.
- Done when: both APK sizes and build times are recorded, and the apkshrink build passes a smoke test with no new crashes in Crashlytics.
- Stop if: it saves less than about 10% over the tuned Unity baseline, pushes the build past 10 minutes, introduces crashes or visible texture artefacts, or fails on the Windows build machine.
- Hand-off: none.

CONFIDENCE: medium. Three things limit it:
- The load-bearing 60% claim is UNVERIFIED.
- The item was read from a saved snapshot, with no source code available.
- The size budget the sender cites is not in the context file.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/apkshrink (default branch main, sha not captured; MIT, last push 2026-09-23, not archived, 290 stars; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "cuts Android APK size by 60%", "evidence": "README: '60% smaller APKs on average across our test games'; test games and measurement script are private and not in the repo", "status": "UNVERIFIED"},
    {"claim": "works by re-encoding textures and stripping unused code", "evidence": "README description only; no source in snapshot", "status": "PROBABLE", "load_bearing": false},
    {"claim": "installs from the Unity Package Manager", "evidence": "README statement only", "status": "PROBABLE", "load_bearing": false},
    {"claim": "licensed MIT", "evidence": "meta.json license field and README", "status": "CONFIRMED"},
    {"claim": "actively maintained", "evidence": "meta.json: last push 2026-09-23, not archived; README: last release 2026-09-23", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found in context file (sender's size budget is not a listed goal); touches goal 1 (Android build under 10 minutes), possibly adding build time",
          "overlap": "Unity 6 (in use) already provides texture compression settings and managed code stripping",
          "burden": "one Unity package plus an extra step in the Jenkins Android build; must work on macOS and Windows builds",
          "risks": ["MIT, allowed for shipped code", "code stripping can remove reflection-only code and cause runtime crashes", "texture re-encoding may degrade visuals", "may lengthen build time against goal 1", "no source in snapshot to check for telemetry or network use"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On a branch, build the Android release with Unity's own stripping and texture compression tuned, then with apkshrink added; record APK size and build time for both and smoke-test the apkshrink build",
                  "owner": "owner of the Jenkins Android build",
                  "done_when": "both APK sizes and build times are recorded and the apkshrink build passes a smoke test with no new Crashlytics crashes",
                  "stop_condition": "stop if it saves under about 10% versus the tuned Unity baseline, pushes the build past 10 minutes, introduces crashes or visible texture artefacts, or fails on the Windows build",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```