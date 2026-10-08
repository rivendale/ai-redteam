VERDICT: skip. poolkit is GPL-3.0, and its own README says anything that links it must be released under the GPL. Our rules allow only MIT, Apache-2.0, BSD or zlib for code we ship in the game, and the sender's plan is to compile it into the game.

WHAT IT IS: example-org/poolkit (repo), read from a saved snapshot captured 2026-10-08, not live. License GPL-3.0, 2,400 stars, last push and last release 2026-08-30, not archived, default branch `main`. No commit SHA was recorded in the capture.

CLAIMS CHECKED:
- **The license is GPL-3.0, and anything that links it must be GPL.** Both meta.json and the README say so. CONFIRMED. The verdict rests on this claim.
- **"We'd compile it into the game"** (sender's words). This is the plan, and it is the condition that triggers the GPL requirement. CONFIRMED as the intended use. The verdict rests on this claim.
- **Zero allocations in the hot path.** The README asserts it but gives no benchmark or profiler evidence. UNVERIFIED. Not load-bearing.
- **Pre-warmed pools and automatic return.** These are feature claims with no code shown in the snapshot. UNVERIFIED. Not load-bearing.
- **"A nice pooling library"** (sender's words). This is split into two parts:
  - The fact behind it, 2,400 stars, is CONFIRMED.
  - The inference that it is good quality has no evidence. Popularity is not quality, so this part is UNVERIFIED. Not load-bearing.
- **Maintained.** The last push was 2026-08-30, about 5 weeks before capture. CONFIRMED. Not load-bearing.

FIT:
- **Goal:** none found. None of the four goals is about this:
  1. build time
  2. crash noise
  3. localization
  4. devlog
- **Overlap:** Unity 6 ships a built-in `UnityEngine.Pool.ObjectPool<T>`. This comes from general knowledge of Unity, not from the item. Any pooling need can likely be met there with no new dependency.
- **Burden:** low. It is a folder dropped into Assets/.
- **Cost:** free, open source. Read 2026-10-08 from the snapshot.
- **Risks:**
  - The license blocks it. GPL-3.0 in shipped code violates the shipping-license rule, and the copyleft would force the game itself under the GPL.
  - The install path (copy into Assets/) is fine.
  - No telemetry is mentioned.

NEXT ACTION: Close this as skip, with the license reason noted.
- Owner: operator.
- Done when: the request is answered "no, GPL-3.0 can't ship in the game." If a pooling need comes up, it goes to Unity's built-in `ObjectPool` or to an MIT, Apache-2.0, BSD or zlib library.
- Hand-off: none.

CONFIDENCE: high. The license fact and the shipping plan are both confirmed, and the context file is present. One limit: the snapshot is a saved copy from 2026-10-08, so a later relicense would not show here.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo", "identity": "example-org/poolkit (GPL-3.0, 2,400 stars, last push 2026-08-30, not archived, default branch main; saved snapshot 2026-10-08, no SHA recorded)",
           "resolved": true},
  "claims": [
    {"claim": "licensed GPL-3.0; anything that links it must be released under the GPL", "evidence": "meta.json license field and README license line", "status": "CONFIRMED"},
    {"claim": "we'd compile it into the game (sender)", "evidence": "sender's stated plan; README says drop the folder into Assets/", "status": "CONFIRMED"},
    {"claim": "zero allocations in the hot path", "evidence": "README assertion only, no benchmark or profiler data", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "pre-warmed pools and automatic return", "evidence": "README feature list, no code in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "2,400 stars", "evidence": "meta.json and README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "it is a nice (good-quality) library, inferred from popularity", "evidence": "only star count offered; popularity is not quality evidence", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "actively maintained", "evidence": "last push and release 2026-08-30, not archived", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found", "overlap": "Unity 6 includes UnityEngine.Pool.ObjectPool<T> (general knowledge, not from the item)",
          "burden": "low: copy a folder into Assets/",
          "risks": ["GPL-3.0 violates the rule that shipped game code be MIT, Apache-2.0, BSD or zlib", "copyleft would require releasing the game under the GPL"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "GPL-3.0, copyleft on anything that links it",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Answer the sender: skip, GPL-3.0 cannot ship in the game; use Unity's built-in ObjectPool or a permissively licensed library if pooling is needed",
                  "owner": "operator", "done_when": "the request is closed as skip with the license reason recorded",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```