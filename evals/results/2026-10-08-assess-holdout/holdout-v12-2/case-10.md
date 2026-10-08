VERDICT: skip. poolkit is GPL-3.0, and our context file allows only MIT, Apache-2.0, BSD or zlib for code we ship in the game. Compiling it into the game would break that rule, and it serves none of our four goals.

WHAT IT IS: example-org/poolkit (repo). I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. No commit SHA was captured.
- **License:** GPL-3.0.
- **Health:** 2,400 stars, last push and last release 2026-08-30, not archived, default branch `main`.
- **What it does:** object pooling for Unity, installed by dropping a folder into Assets/.

CLAIMS CHECKED:
- **"Licensed GPL-3.0; anything that links this library must itself be released under the GPL."** The evidence is the snapshot's license line and meta.json `license: GPL-3.0`. **CONFIRMED.** The verdict rests on this claim.
- **Sender: "we'd compile it into the game. adopt?"** This implies the library is fit to ship. The item's own license text contradicts it: shipping it would require GPL-licensing the game, and our rules allow GPL only for tools we never ship. **REFUTED.** The verdict rests on this claim.
- **"Zero allocations in the hot path."** The only evidence is the README statement, with no benchmark or code in the snapshot. **UNVERIFIED.** The verdict does not rest on it.
- **Sender: "a nice pooling library."** This is split into two parts:
  - The fact "2,400 stars" is **CONFIRMED** from meta.json.
  - The inference "so it is good" is **UNVERIFIED**, because popularity is not evidence of quality.
  - The verdict does not rest on either part.

FIT:
- **Goal:** none found. Our goals are Android build time, crash noise, five languages and the devlog. Runtime pooling serves none of them.
- **Overlap:** Unity 6 ships a built-in `UnityEngine.Pool.ObjectPool<T>`. That comes from my general knowledge of Unity, not from the snapshot, so verify it in the engine docs.
- **Burden:** low. It is a vendored folder in Assets/.
- **Cost:** free and open source, with GPL-3.0 terms, as read on 2026-10-08.
- **Risks:**
  - The GPL-3.0 copyleft would extend to the shipped game, which violates the context's license rule.
  - Distributing GPL code through app stores raises further compatibility questions.

NEXT ACTION: Nothing to do with poolkit.
- **If the game needs pooling,** a developer checks whether Unity 6's built-in `UnityEngine.Pool.ObjectPool<T>` covers the use case.
- **Done when:** the developer has answered yes or no for the specific pooling need.
- **If no,** look for an MIT, Apache-2.0, BSD or zlib licensed alternative and run that through assess.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, the license claims the verdict rests on are CONFIRMED and REFUTED from the item's own text, and a context file is present. The one limit is that I worked from the snapshot, not a live read. A relicensing after 2026-10-08 would change the answer.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/poolkit (GPL-3.0, last push 2026-08-30, not archived, 2,400 stars; read from snapshot captured 2026-10-08, no SHA recorded)",
           "resolved": true},
  "claims": [
    {"claim": "licensed GPL-3.0; anything that links this library must itself be released under the GPL",
     "evidence": "snapshot.md license line and meta.json license: GPL-3.0", "status": "CONFIRMED"},
    {"claim": "sender: it can be compiled into the game and adopted",
     "evidence": "item's own GPL-3.0 terms require the linking game to be GPL; context allows only MIT, Apache-2.0, BSD or zlib for shipped code",
     "status": "REFUTED"},
    {"claim": "zero allocations in the hot path", "evidence": "README statement only, no benchmark or code in snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "2,400 stars", "evidence": "meta.json stars: 2400", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "sender: it is a nice (good-quality) pooling library",
     "evidence": "only popularity offered; no code or benchmarks in snapshot", "status": "UNVERIFIED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "Unity 6 includes UnityEngine.Pool.ObjectPool<T> (from general knowledge, not the snapshot)",
          "burden": "low: vendored folder in Assets/",
          "risks": ["GPL-3.0 copyleft would extend to the shipped game, violating the shipped-code license rule",
                    "GPL distribution via app stores is a further compatibility problem"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "GPL-3.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "If pooling is needed, check whether Unity 6's built-in UnityEngine.Pool.ObjectPool<T> covers the use case; otherwise find a permissively licensed alternative and assess it",
                  "owner": "game developer",
                  "done_when": "a yes/no answer on whether the built-in pool covers the need",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```