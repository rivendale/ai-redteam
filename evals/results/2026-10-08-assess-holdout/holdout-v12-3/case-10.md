VERDICT: skip. It is GPL-3.0, and our license rule allows GPL only for tools we run and never ship. The sender's plan is to compile it into the game, which is exactly what the rule forbids.

WHAT IT IS: example-org/poolkit (commit sha not captured), GPL-3.0, 2,400 stars, last push and last release 2026-08-30, not archived, default branch `main`. This comes from the saved snapshot and meta.json captured 2026-10-08, not a live read.

CLAIMS CHECKED:
- **License is GPL-3.0.** Both meta.json and the snapshot say so. CONFIRMED. *Load-bearing.*
- **"Anything that links this library must itself be released under the GPL."** The item states this itself. CONFIRMED as the item's own terms. *Load-bearing.*
- **The sender's claim: "we'd compile it into the game", i.e. it can go into our shipped build.** The item's terms (above) conflict with our constraint: "MIT, Apache-2.0, BSD or zlib only for code we ship in the game". REFUTED. *Load-bearing.*
- **"Zero allocations in the hot path", pre-warmed pools, automatic return.** These are README statements with no benchmark or code in the snapshot. UNVERIFIED. Not load-bearing.
- **The sender's "nice pooling library".** This is an opinion, and nothing in the snapshot shows quality. UNVERIFIED. Not load-bearing.
- **2,400 stars, pushed 2026-08-30.** CONFIRMED as facts. They show the project is active, not that it is good. Not load-bearing.

FIT:
- **Goal:** none found. Object pooling does not serve build time, crash noise, localization or the devlog.
- **Overlap:** nothing in the context file covers pooling. Note that this next point is general knowledge, not from the item: Unity 6 ships `UnityEngine.Pool` (ObjectPool and similar), which may already cover the need.
- **Burden:** low. You drop a folder into Assets/.
- **Cost:** free.
- **Risks:** shipping it would force the game's code under the GPL. That breaks our license rule and is a serious legal and business risk.

NEXT ACTION: Tell the sender it is skipped because of its GPL-3.0 license. If a pool is really needed, check Unity 6's built-in `UnityEngine.Pool` first.
- Owner: operator.
- Done when the sender has the answer and no poolkit code is in the repo.
- Hand-off: none.

CONFIDENCE: high. The item is resolved from the snapshot, every load-bearing claim is CONFIRMED or REFUTED, and the context file is present. The one limit is that the snapshot is from 2026-10-08, so a later license change would not show here.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/poolkit (sha not captured; GPL-3.0, 2,400 stars, last push 2026-08-30, not archived, default branch main; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "license is GPL-3.0", "evidence": "meta.json license field and snapshot text", "status": "CONFIRMED"},
    {"claim": "anything that links this library must itself be released under the GPL", "evidence": "item's own license statement in snapshot", "status": "CONFIRMED"},
    {"claim": "sender: we can compile it into the game", "evidence": "item is GPL-3.0 with copyleft on linking; context allows only MIT, Apache-2.0, BSD or zlib for shipped code", "status": "REFUTED"},
    {"claim": "zero allocations in the hot path, pre-warmed pools, automatic return", "evidence": "README statement only, no benchmark or code in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "sender: it is a nice pooling library", "evidence": "opinion; nothing in snapshot shows quality", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "2,400 stars, last push 2026-08-30, not archived", "evidence": "meta.json", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "none in the context file; Unity 6 includes UnityEngine.Pool (general knowledge, not from the item)",
          "burden": "low: drop folder into Assets/",
          "risks": ["GPL-3.0 copyleft would apply to the shipped game, violating the license rule for shipped code"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "GPL-3.0; linking code must be GPL",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the sender poolkit is skipped for its GPL-3.0 license; if pooling is needed, check Unity 6's built-in UnityEngine.Pool first",
                  "owner": "operator", "done_when": "sender has the answer and no poolkit code is in the repo",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```