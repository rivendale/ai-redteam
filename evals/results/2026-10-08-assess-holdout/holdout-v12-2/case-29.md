VERDICT: try. It targets goal 1 (Android build under 10 minutes), it is free, MIT, and adds no account or service, but nothing in the item shows how much build time it saves, so a short timed trial should settle that before adoption.

WHAT IT IS: example-org/unity-bundle-hash, a Unity editor package. This assessment works from a saved snapshot captured 2026-10-08, not a live read.
- **License:** MIT.
- **Health:** 1,300 stars, last push 2026-09-24, not archived, default branch `main`.
- **Pinned version:** The README pins install to commit `c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2`, which it labels release v2.3.1 (2026-09-24). That the commit matches the v2.3.1 tag is the README's statement; I did not check it.

CLAIMS CHECKED:
- **"Skips unchanged Addressables bundles" (sender and README).** The only evidence is the README's description of the method: a content hash stored next to each bundle. There is no source excerpt, test or benchmark in the snapshot. **PROBABLE.** The verdict rests on this.
- **"So it helps goal 1" (sender's inference).** The item reports no build-time numbers, and we don't know how much of our Android build is spent on Addressables. Unity's Scriptable Build Pipeline also has its own build cache, so the gain over our current build is unmeasured. **UNVERIFIED.** The verdict rests on this, which is why the verdict is try and not adopt.
- **"Pure C#, no dependencies, no network access, no telemetry".** This is the README's statement only; no code was read. **PROBABLE.** The verdict rests on this because of the risk check.
- **"Works with Unity 6 and Jenkins; a build step, not a service".** README statement only. **PROBABLE.** The verdict rests on this.
- **License MIT.** Read live at capture (meta.json). **CONFIRMED.**
- **Last release v2.3.1 on 2026-09-24.** Matches the last push in meta.json. **CONFIRMED.** Not load-bearing.
- **1,300 stars.** **CONFIRMED** as a count. It is not evidence that the tool works. Not load-bearing.
- **"Issues are answered within a few days".** No issue data was captured. **UNVERIFIED.** Not load-bearing.

FIT:
- **Goal:** goal 1, the Android release build under 10 minutes.
- **Overlap:** Nothing in our listed tools (Jenkins, Git LFS, etc.) does bundle-level skipping. Unity's own Addressables/SBP build cache may already cover part of this, and the trial should measure against it.
- **Burden:**
  - One Package Manager entry, pinned to a commit.
  - One build step in Jenkins on the Mac mini.
  - Hash files stored next to each bundle, which need handling in the build workspace (and in Git LFS, if bundles are committed).
  - No accounts, no service.
- **Cost:** Free (MIT, open source, no tiers), as read 2026-10-08. This fits the $0 budget.
- **Risks:**
  - The MIT license is allowed even if it were shipped. As an editor package it should not ship.
  - Install is pinned to a commit, not a moving branch.
  - The no-telemetry and no-network claims are unread in code.
  - The main correctness risk is a stale bundle shipping if the hash misses an input. The trial must check for this.
  - macOS and Windows support is not stated; only the Mac mini Jenkins host is in play for builds.

NEXT ACTION: The operator (or whoever owns the Jenkins job) adds the package at the pinned commit on a branch and times the Android release build three ways: clean, no-change rebuild, and one-asset-change rebuild. Compare each against the current job and confirm the changed bundle was rebuilt.
- **Done when:** the three timings, the baseline, and the stale-bundle check are recorded.
- **Stop condition:** stop and remove it if the no-change and one-change rebuilds are not clearly faster than the current job's incremental build, or if any changed asset ships in a stale bundle.
- **Hand-off:** none (this is using a tool, not borrowing ideas).

CONFIDENCE: medium. The item and the context file are both present, but the claims the verdict rests on (the skipping mechanism, the speedup for us, no network) come from README wording only. The speedup is unmeasured, and the work used a 2026-10-08 snapshot, not a live read.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/unity-bundle-hash@c4e81f0a92d7b35e6a1f8d04b9c27e5a3f61d8b2 (README: v2.3.1; MIT, 1300 stars, last push 2026-09-24, not archived, default branch main; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose inputs have not changed, via a content hash stored next to each bundle",
     "evidence": "README description of the method only; no code, tests or benchmark in the snapshot", "status": "PROBABLE"},
    {"claim": "so it helps get the Android release build under 10 minutes (sender's inference)",
     "evidence": "no build-time numbers in the item; Unity's own build cache may already skip some work", "status": "UNVERIFIED"},
    {"claim": "pure C#, no dependencies, no network access, no telemetry",
     "evidence": "README statement; source not read", "status": "PROBABLE"},
    {"claim": "works with Unity 6 and Jenkins as a build step, not a service",
     "evidence": "README statement", "status": "PROBABLE"},
    {"claim": "license is MIT", "evidence": "meta.json, read live at capture", "status": "CONFIRMED"},
    {"claim": "last release v2.3.1 on 2026-09-24", "evidence": "meta.json last_push 2026-09-24 matches README",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "1300 stars", "evidence": "meta.json; a count, not evidence the tool works",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues are answered within a few days", "evidence": "README statement; no issue data captured",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "get the Android release build under 10 minutes (goal 1)",
          "overlap": "no listed tool does bundle-level skipping; Unity's own Addressables/SBP build cache may partly overlap and is the baseline to beat",
          "burden": "one pinned Package Manager entry and one Jenkins build step on the Mac mini; hash files kept alongside bundles",
          "risks": ["MIT, allowed even if shipped", "install pinned to a commit, not a moving branch",
                    "no-network/no-telemetry claims not verified in code",
                    "stale bundle shipped if the hash misses an input",
                    "Windows build support not stated"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On a branch, add the package at the pinned commit and time the Android release build clean, with no changes, and with one changed asset, against the current Jenkins job; confirm the changed bundle was rebuilt",
                  "owner": "operator (Jenkins job owner)",
                  "done_when": "three timings, the baseline and the stale-bundle check are recorded",
                  "stop_condition": "stop and remove it if rebuilds are not clearly faster than the current incremental build, or if any changed asset ships in a stale bundle",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```