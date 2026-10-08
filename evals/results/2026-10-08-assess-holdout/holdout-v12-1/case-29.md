VERDICT: try. It plausibly serves goal 1, it is free, MIT, editor-only and needs no account. The snapshot does not show how much of our Android build is spent rebuilding Addressables, and the "skips unchanged" behaviour is backed only by the README. A bounded, measured trial is the right next step.

WHAT IT IS: example-org/unity-bundle-hash, repo, read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live.
- License: MIT.
- Health: 1,300 stars, last push 2026-09-24, not archived, default branch `main`.
- Release: v2.3.1 (2026-09-24). The README says to install with a Package Manager git URL pinned to commit `c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2`. That this commit is the v2.3.1 tag is the README's statement; the snapshot does not show it independently.
- What it does: a Unity editor package that stores a content hash next to each Addressables bundle and skips rebuilding bundles whose inputs have not changed.
- No source code was read; only the README text is in the snapshot.

CLAIMS CHECKED:
- **"Skips rebuilding Addressables bundles whose inputs have not changed"** (sender's and README's claim): PROBABLE.
  - The only evidence is the README description. No benchmark, no source and no list of which inputs are hashed.
  - What would change the conclusion: the hash misses some input (dependencies, build settings, Unity version or target platform), so a changed bundle is skipped and stale content ships.
  - The verdict rests on this claim.
- **"It serves goal 1"** (the sender's question), split in two:
  - (a) It reduces Android build time: PROBABLE, but only if Addressables rebuilds are a real share of our build. The context file gives no build-time breakdown. The verdict rests on this part.
  - (b) It gets the build under 10 minutes: UNVERIFIED. Nothing here gives the current build time or the share spent on bundles.
- **"Pure C#, no dependencies, no network access, no telemetry"**: UNVERIFIED.
  - This is a README statement only; no source was read.
  - It matters because the editor package would run on our build machine. The verdict rests on it.
- **"Works with Unity 6 and Jenkins (a build step, not a service)"**: PROBABLE.
  - This is a README statement. It is consistent with being an editor package, but there is no CI example or Unity version matrix.
- **"License: MIT"**: CONFIRMED. meta.json, read live at capture, agrees with the README.
- **"Install pinned to a commit"**: CONFIRMED that the README gives a full-sha pinned URL rather than a moving branch.
- **"Issues are answered within a few days"**: UNVERIFIED.
  - The snapshot has no issue data. 1,300 stars is a true count, but it is not evidence of quality or responsiveness.
  - The verdict does not rest on this claim.

FIT:
- **Goal:** goal 1, Android release build under 10 minutes.
- **Overlap:** nothing in our tool list does incremental Addressables builds. Unity's own Scriptable Build Pipeline has a build cache that may already skip some unchanged work. The trial should compare against our current setup with that cache enabled, not against a cold build.
- **Burden:**
  - One package entry in the project manifest and possibly one Jenkins build-step change.
  - The hash files must be kept next to the bundles between Jenkins runs on the Mac mini.
  - Clean builds must be forced when the Unity version changes.
- **Cost:** free and open source, MIT, read 2026-10-08. No tiers and no account. This fits the $0 budget.
- **Risks:**
  - **License:** MIT is allowed even for shipped code. It is editor-only, so it should not ship at all.
  - **Install path:** pinned to a full commit sha via git URL, which is good.
  - **Telemetry and network:** the README says none; this is unverified from source.
  - **Correctness:** a missed input in the hash means stale bundles ship, which is the main risk.
  - **Platforms:** pure C#, so it should run on both macOS and Windows builds; this is unverified.
  - **Project health:** active (push 16 days before capture, not archived). It is a single-org project.
  - **No player data involved.**

NEXT ACTION:
- **Action:** on a branch, add the package at the pinned commit and run the Jenkins Android release build three ways:
  1. A clean build.
  2. A rebuild with no changes.
  3. A rebuild after editing one asset in one group.

  Compare total time and Addressables time against the same three builds without it. Diff the output bundles of runs 2 and 3 against a clean build. Before installing, read its editor scripts for network calls and for the list of hashed inputs.
- **Owner:** operator, or whoever maintains the Jenkins Android job.
- **Done when:** a table of the six build times exists, the bundle diff is recorded, and the source read confirms or refutes the no-network claim and lists the hashed inputs.
- **Stop condition:** stop and remove it if any skipped bundle differs from a clean-build bundle. Also stop if the no-change rebuild saves under one minute over our current cached build. Also stop if the source shows network calls.
- **Hand-off:** none.

CONFIDENCE: medium.
- The item is resolved from a dated snapshot and a context file is present.
- Two claims the verdict rests on are below PROBABLE or CONFIRMED: "no network or telemetry" is unverified, and "under 10 minutes" is unverified.
- We do not know what share of the Android build Addressables takes.
- No source code was read.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/unity-bundle-hash (README pins c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2 as v2.3.1; MIT, 1300 stars, last push 2026-09-24, not archived, default branch main; from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose inputs have not changed",
     "evidence": "README description only; no source, benchmark or list of hashed inputs in the snapshot",
     "status": "PROBABLE"},
    {"claim": "it reduces Android build time (serves goal 1)",
     "evidence": "follows from skipping bundles only if Addressables rebuilds are a real share of the build; context gives no build-time breakdown",
     "status": "PROBABLE"},
    {"claim": "it gets the Android build under 10 minutes",
     "evidence": "nothing in the item or context gives current build time or the share spent on bundles",
     "status": "UNVERIFIED"},
    {"claim": "pure C#, no dependencies, no network access, no telemetry",
     "evidence": "README statement only; source not read",
     "status": "UNVERIFIED"},
    {"claim": "works with Unity 6 and Jenkins as a build step",
     "evidence": "README statement; consistent with an editor package, no CI example given",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "license is MIT",
     "evidence": "meta.json (read live at capture) and README agree",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "install is pinned to a commit, not a moving branch",
     "evidence": "README gives a git URL with a full 40-character sha",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues are answered within a few days",
     "evidence": "no issue data in the snapshot; star count is a fact but not evidence of responsiveness",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes",
          "overlap": "nothing in use does incremental Addressables builds; Unity's Scriptable Build Pipeline build cache may already skip some work, so compare against it",
          "burden": "one package entry, possibly one Jenkins step change, keeping hash files next to bundles between runs, forcing clean builds on Unity upgrades",
          "risks": ["MIT, editor-only so not shipped",
                    "install pinned to full commit sha",
                    "no-network/no-telemetry is a README claim not checked in source",
                    "a missed hash input would ship stale bundles",
                    "macOS and Windows support assumed from pure C#, not verified",
                    "active but single-org project"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On a branch, read the package's editor scripts for network calls and hashed inputs, then run the Jenkins Android build clean, no-change and one-asset-change, with and without the package pinned at c4e81f0, and diff the bundles against a clean build",
                  "owner": "operator (Jenkins Android job maintainer)",
                  "done_when": "six build times are tabulated, the bundle diff is recorded, and the source read confirms or refutes no-network and lists hashed inputs",
                  "stop_condition": "stop and remove if any skipped bundle differs from a clean build, if the no-change rebuild saves under one minute versus the current cached build, or if the source makes network calls",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```