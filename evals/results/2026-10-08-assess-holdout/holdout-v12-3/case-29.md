VERDICT: try. It directly targets goal 1 (Android build under 10 minutes), is free, MIT, pinned to a commit, and adds no account or service. But nothing in it shows how much time it saves on our build, and a cache that misses an input could ship stale bundles, so it needs a short measured trial first.

WHAT IT IS: example-org/unity-bundle-hash, read from the saved snapshot captured 2026-10-08, not live. It is a Unity editor package (Addressables build step). License MIT. 1,300 stars. Last push 2026-09-24. Not archived. Default branch main. Latest release v2.3.1 (2026-09-24), installed by git URL pinned to commit c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2. Source code was not part of the snapshot and was not read.

CLAIMS CHECKED:
- **Skips rebuilding Addressables bundles whose inputs have not changed, using a stored content hash.** PROBABLE. Only the README describes this; no code or benchmark was captured. The verdict rests on it.
- **Works with Unity 6 and Jenkins, as a build step, not a service.** PROBABLE. README statement, and plausible for a pure C# editor package. The verdict rests on it.
- **Pure C#, no dependencies, no network access, no telemetry.** UNVERIFIED. This is the README's own assertion and the source was not read. It is not load-bearing because it runs only in the editor at build time and touches no player data, but the trial should confirm it.
- **MIT license.** CONFIRMED by meta.json and the README.
- **Actively maintained (release 2026-09-24).** CONFIRMED by meta.json last_push.
- **"Issues are answered within a few days."** UNVERIFIED. The issue tracker was not captured. Not load-bearing.
- **1,300 stars.** CONFIRMED as a count. It is not evidence that the package is correct or fast, and the verdict does not rest on it.
- **Implied by the sender: this helps goal 1.** UNVERIFIED. Nothing gives a time saving, and we do not know how much of our Android build is spent on Addressables.

FIT:
- **Goal:** Goal 1, getting the Android release build under 10 minutes.
- **Overlap:** None found. Nothing in use (Jenkins, Git LFS, Unity 6) caches Addressables builds. Unity's own Addressables content-update workflow overlaps in purpose but is not listed as in use.
- **Burden:** One editor package plus one Jenkins build step. There is also a hash file per bundle to keep, which on CI must persist between builds or nothing gets skipped. No accounts and no services.
- **Cost:** Free, open source, MIT, no limits. Read from the snapshot dated 2026-10-08.
- **Risks:**
  - License: MIT is acceptable even for shipped code, and this is an editor tool that does not ship.
  - Install path: low risk, because the git URL is pinned to a full commit SHA.
  - Correctness: if the hash misses an input (build settings, shader variants, platform or compression options), stale bundles could ship. The trial must check for this.
  - Platforms: the "no network" claim is unread, and the snapshot does not mention Windows (we build on macOS and Windows).
  - Lock-in: low, since removing the step returns to normal full builds.

NEXT ACTION:
- **Action:** On the Jenkins Mac mini, add the package at the pinned commit on a branch. Then:
  1. Run two Android release builds back to back with no asset changes.
  2. Run one build after changing a single asset.
  3. Record the Addressables step time and total build time for each, against today's baseline.
  4. Byte-compare the bundles from the changed-asset build with a clean full build.
  5. Skim the package source for network calls.
- **Owner:** operator (or whoever maintains the Jenkins build).
- **Done when:** the timings and the bundle comparison are written down, with a keep or drop call.
- **Stop condition:** drop it if the skipped build saves under 1 minute, if any bundle differs from the clean build's output, or if the source makes network calls.
- **Hand-off:** none (this is using a tool, not borrowing ideas).

CONFIDENCE: Medium. The context file is present and the item is resolved from a dated snapshot, but the core claims rest on the README alone with the source unread. The size of the saving for our build is unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/unity-bundle-hash@c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2 (v2.3.1, MIT, 1,300 stars, last push 2026-09-24, not archived, default branch main; from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose inputs have not changed, using a stored content hash",
     "evidence": "README description only; no code or benchmark in the snapshot", "status": "PROBABLE"},
    {"claim": "works with Unity 6 and Jenkins as a build step, not a service",
     "evidence": "README statement; consistent with a pure C# editor package", "status": "PROBABLE"},
    {"claim": "pure C#, no dependencies, no network access, no telemetry",
     "evidence": "README assertion; source not read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "MIT license", "evidence": "meta.json license field and README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "actively maintained, last release 2026-09-24", "evidence": "meta.json last_push 2026-09-24, not archived",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues are answered within a few days", "evidence": "README statement; issue tracker not captured",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "1,300 stars", "evidence": "meta.json stars count; a count, not evidence of quality",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "sender's implied claim: it helps get the Android build under 10 minutes (goal 1)",
     "evidence": "no timings in the item; our Addressables share of build time is unknown",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: get the Android release build under 10 minutes",
          "overlap": "none found; nothing in use caches Addressables builds",
          "burden": "one editor package and one Jenkins step; per-bundle hash files must persist between CI builds",
          "risks": ["MIT, editor-only tool, not shipped",
                    "install pinned to a full commit SHA",
                    "stale bundles if the hash misses an input (build settings, shader variants, compression)",
                    "no-network claim and Windows support not verified"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On the Jenkins Mac mini, add the package at the pinned commit on a branch, time two unchanged Android builds and one single-asset-change build against today's baseline, byte-compare bundles with a clean full build, and skim the source for network calls",
                  "owner": "operator",
                  "done_when": "timings and the bundle comparison are recorded with a keep or drop call",
                  "stop_condition": "stop if the skipped build saves under 1 minute, any bundle differs from the clean build, or the source makes network calls",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```