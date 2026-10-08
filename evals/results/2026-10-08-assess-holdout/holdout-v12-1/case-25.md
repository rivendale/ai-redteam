VERDICT: try. Copying the script's skip-unchanged-bundles idea into our own Unity editor code is a borrow, not a dependency, and it targets goal 1 directly. But nothing in the snapshot shows the saving, and we don't know whether our Jenkins release builds are repeat builds at all, so it needs a measured trial first.

WHAT IT IS: example-org/bundlecache on default branch `main`. The commit sha was not captured. It is MIT licensed, last pushed 2026-09-16, not archived, and has 380 stars. I worked from a saved snapshot (work/snapshot.md and meta.json, captured 2026-10-08), not a live read. The snapshot contains only the README text, not the script's source.

CLAIMS CHECKED:
- "Skips rebuilding Addressables bundles whose input hash has not changed": the evidence is the README's description only, and the code is not in the snapshot. **UNVERIFIED.** The verdict rests on this.
- "Cuts repeat Android builds when few assets change": the README gives no timings, method or sample. **UNVERIFIED.** The verdict rests on this. The claim also covers only *repeat* builds where *few assets change*. A clean release build gets nothing from it.
- "A single 90-line editor script": the line count is stated in the README, and no code was captured to check it. **UNVERIFIED**, not load-bearing. It matters only for how cheap the copy is.
- "The author recommends copying the one script rather than depending on the repository": the README says exactly this. **CONFIRMED**, not load-bearing. It fits the sender's "no new dependency".
- License is MIT: meta.json `"license": "MIT"` and the README agree. **CONFIRMED.**
- Last release 2026-09-16 and 380 stars: meta.json matches. **CONFIRMED** as facts, not load-bearing. The star count says nothing about whether the hashing is correct.
- Sender's claim "looks borrowable for goal 1": the skip-unchanged idea does map to build time (goal 1). Whether it helps depends on the two UNVERIFIED claims and on our build setup. **PROBABLE**, and the verdict rests on it.

FIT:
- **Goal:** Goal 1, "Get the Android release build under 10 minutes."
- **Overlap:** Nothing in the context file does incremental bundle builds. The context file does not say whether we use Addressables at all. The trial should also compare the script against what Unity 6's own build pipeline already caches, so we don't rebuild something Unity does for us.
- **Burden:** One editor script that we copy into our repo, after which we own it. We must also keep the bundle cache between builds in the Jenkins workspace on the Mac mini, and must notice when a stale hash produces a wrong bundle. There are no accounts and no services.
- **Cost:** Free (MIT, read 2026-10-08), within the $0 budget.
- **Risks:**
  - MIT is allowed even for shipped code, and editor scripts don't ship anyway. Copying MIT code still requires keeping the copyright and license notice.
  - A hash that misses an input could ship stale bundles.
  - The script was not read, so its hashing logic, any network calls and any telemetry are unchecked.
  - There is no install path risk because we copy the script rather than install it.

NEXT ACTION: Hand the repo to `glean` to read the one script and port the skip-if-hash-unchanged logic into our editor build code, keeping the MIT notice. The operator then runs it for a bounded trial on the Jenkins Mac mini.
- **Owner:** operator, or whoever owns the Jenkins Android build.
- **Done when:** We have timed two consecutive Android release builds with a small asset change between them, with and without the ported logic, and checked that the bundles are byte-identical, or rebuilt where an input changed.
- **Stop condition:** Stop and drop it if any of these turn out true:
  - Our release builds are clean builds, so there is no cache to reuse.
  - We don't use Addressables.
  - The saving is under one minute.
  - Unity's own build cache already skips those bundles.
- **Hand-off:** `glean`.

CONFIDENCE: medium. The item is a saved snapshot without the source code. The load-bearing claims about what the script does and how much it saves are UNVERIFIED. The context file doesn't say whether we use Addressables or whether Jenkins builds are incremental.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/bundlecache@main (sha not captured; MIT, last push 2026-09-16, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "skips rebuilding Addressables bundles whose input hash has not changed",
     "evidence": "README description only; the script's source is not in the snapshot", "status": "UNVERIFIED"},
    {"claim": "cuts repeat Android builds when few assets change",
     "evidence": "README statement, no timings, method or sample; applies to repeat builds only", "status": "UNVERIFIED"},
    {"claim": "a single 90-line editor script",
     "evidence": "README statement; no code captured to count", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the author recommends copying the script rather than depending on the repository",
     "evidence": "README says so", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "licensed MIT",
     "evidence": "meta.json license field and README agree", "status": "CONFIRMED"},
    {"claim": "last release 2026-09-16, 380 stars",
     "evidence": "meta.json last_push and stars match the README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "sender: the bundle-skipping approach is borrowable for goal 1",
     "evidence": "skipping unchanged bundles maps to build time; benefit depends on incremental builds and Addressables use, neither stated in the context file",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "Get the Android release build under 10 minutes (goal 1)",
          "overlap": "none found in the context file; compare against Unity 6's own build cache during the trial",
          "burden": "one copied editor script we maintain; bundle cache must persist in the Jenkins workspace",
          "risks": ["MIT: allowed, keep the notice in the copied file",
                    "a hash that misses an input could ship stale bundles",
                    "source not read: hashing logic, network calls and telemetry unchecked",
                    "no benefit if release builds are clean builds"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "glean the script, port the skip-if-hash-unchanged logic into our editor build code, then time two consecutive Android release builds on Jenkins with and without it",
                  "owner": "operator",
                  "done_when": "timings with and without the logic are recorded and the produced bundles are checked as correct",
                  "stop_condition": "stop if release builds are clean, we don't use Addressables, Unity's own cache already skips them, or the saving is under one minute",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```