```
VERDICT: try. The 60% figure comes from private test games and a private script, so nothing supports it yet; one before/after build of our own game will settle whether it helps our size budget, and the plugin is free and MIT-licensed.
WHAT IT IS: example-org/apkshrink, read from a saved snapshot captured 2026-10-08, not live. MIT license, default branch
  main, last push and last release 2026-09-23, not archived, 290 stars. It is a Unity Package Manager plugin that says it
  re-encodes textures and strips unused code. No commit sha was recorded at capture, and the snapshot has no source code.
CLAIMS CHECKED:
  1. "Cuts your Android APK size by 60%" (load-bearing): UNVERIFIED. The headline is stronger than the README's own
     quote, which is "60% smaller APKs on average across our test games". The README also says the test games and the
     measurement script are private and are not in the repository. We cannot see the sample, how size was measured, or
     the baseline (for example, whether the games already used Unity's own texture compression and code stripping).
     The number would change for us if our textures are already compressed or our stripping level is already high.
  2. "Works by re-encoding textures and stripping unused code": UNVERIFIED. The README describes it, but the snapshot
     includes no source to check. Not load-bearing.
  3. License is MIT: CONFIRMED (meta.json and README agree).
  4. Project is active: CONFIRMED as a fact (pushed 2026-09-23, not archived). The 290 stars are a true count, but they
     are not evidence that the 60% claim holds.
  5. Sender: "we have a size budget": not in our context file. No goal there mentions APK size, so this fit rests on
     the sender's word.
FIT:
  Goal: none found in the context file. It serves the sender's size budget. It may also work against goal 1 (release
    build under 10 minutes), because re-encoding textures at build time can add build time.
  Overlap: probably partial. Unity 6 already offers texture compression settings and managed code stripping. The
    context file does not say how ours are set, so check those first to get a fair baseline.
  Burden: one package dependency in the Unity project, plus checking build output after each plugin update.
  Cost: free, open source, MIT (read 2026-10-08). No tiers or account mentioned.
  Risks: MIT is allowed even if parts ship in the game. Aggressive code stripping can remove code that is only reached
    through reflection, which causes runtime crashes and works against goal 2 (crash noise). Re-encoding can visibly
    lower texture quality. The snapshot does not say whether it has telemetry or makes network calls. Builds run on
    macOS and Windows, and the snapshot does not say which platforms the plugin supports.
NEXT ACTION: On a branch, the operator (or whoever owns the Jenkins build) builds the release APK once without the
  plugin and once with it. Record APK size, build time, and a smoke-test pass that covers texture quality and startup.
  Done when: both sizes, both build times and the smoke-test result are written down next to the size budget.
  Stop condition: drop it if the saving does not get us under the size budget, if the build passes 10 minutes, or if
  the smoke test shows a crash or visible texture loss.
  Hand-off: none.
CONFIDENCE: medium. The item is resolved from a dated snapshot and a context file is present, but the claim the
  verdict rests on (60%) is UNVERIFIED. The size budget is also not in the context file.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/apkshrink@main (sha not recorded; MIT, last push 2026-09-23, not archived, 290 stars; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "cuts Android APK size by 60%",
     "evidence": "README: '60% smaller APKs on average across our test games'; test games and measurement script are private and not in the repo",
     "status": "UNVERIFIED"},
    {"claim": "works by re-encoding textures and stripping unused code",
     "evidence": "README description only; no source in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "licensed MIT",
     "evidence": "meta.json license field and README agree",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "project is maintained (last push 2026-09-23, not archived)",
     "evidence": "meta.json read live at capture",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found in the context file; serves the sender's stated APK size budget, and may cost build time against goal 1 (release build under 10 minutes)",
          "overlap": "probably partial: Unity 6 already has texture compression and managed code stripping; our current settings are not in the context file",
          "burden": "one Unity package dependency; checking build output on each plugin update",
          "risks": ["MIT, allowed even if shipped in the game",
                    "code stripping can remove reflection-only code and cause runtime crashes (works against goal 2)",
                    "texture re-encoding can lower visual quality",
                    "telemetry, network calls and macOS/Windows support not stated in the snapshot",
                    "60% figure rests on private test games and a private script"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Build the release APK on a branch with and without apkshrink; record APK size, build time and a smoke-test result",
                  "owner": "operator (Jenkins build owner)",
                  "done_when": "both sizes, both build times and the smoke-test result are written down against the size budget",
                  "stop_condition": "drop it if the saving does not get us under the size budget, the build passes 10 minutes, or the smoke test shows a crash or visible texture loss",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```