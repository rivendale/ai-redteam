```
VERDICT: skip. The paper's own Table 2 refutes the summary's "12x faster": the median speedup is 1.2x, and no goal in our context file involves mesh baking.
WHAT IT IS: Paper 2610.00418, "Fast mesh baking by incremental recomputation", a preprint posted 2026-10-02. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The snapshot holds only the title line and the Table 2 passage. Authors, venue and license are not in it.
CLAIMS CHECKED:
  - "paper shows 12x faster mesh baking" (the research agent's summary). REFUTED. Table 2 gives a median of 41.0 s baseline vs 34.2 s, which is 1.2x over 40 scenes. 12x is a single best case on "a scene with a single moved object". The paper itself adds: "Most scenes in practice change many objects." The verdict rests on this.
  - "strong result" (the summary's inference). REFUTED. The interquartile range of the speedup is 1.0x to 1.5x, so a quarter of the scenes gain little or nothing.
  - Median 1.2x over 40 scenes (the paper's claim). PROBABLE. It is a self-reported benchmark, and the snapshot shows no scene set, hardware or method. Not load-bearing.
  - 12x on one single-moved-object scene (the paper's claim). PROBABLE as a reported best case. It is n=1 and the authors say it is not typical. Not load-bearing.
FIT:
  Goal: none found. Our goals are a sub-10-minute Android build, crash noise, five languages and the devlog. Mesh baking appears in none of them. It could only touch goal 1 if baking runs inside the release build, and the context file does not say it does. Even then, 1.2x on one step is a small gain.
  Overlap: Unity 6 already does our baking. Implementing this would mean custom engine-side work beside it.
  Burden: implementing a research algorithm in our pipeline and then maintaining it.
  Cost: free to read. The paper's license and any code release are not in the snapshot. Checked 2026-10-08.
  Risks: building on an unreviewed preprint. Any reference code would need a license check against our MIT/Apache/BSD/zlib rule for shipped code.
NEXT ACTION: Reply to the research agent with the correction: the paper's median speedup is 1.2x (IQR 1.0x–1.5x), and 12x is a single best case. Do not implement it. Owner: operator. Done when the agent's recommendation is withdrawn or corrected. Hand-off: none.
CONFIDENCE: high. The item is resolved from a dated snapshot, the load-bearing claim is REFUTED by the paper's own table, and a context file is present. Limits: the snapshot is an excerpt, and the context file does not say whether mesh baking is part of the Android build.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "paper",
           "identity": "2610.00418, 'Fast mesh baking by incremental recomputation', preprint posted 2026-10-02 (read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "paper shows 12x faster mesh baking (research agent's summary)",
     "evidence": "Table 2: median 41.0 s vs 34.2 s = 1.2x over 40 scenes; 12x is a single best case with one moved object",
     "status": "REFUTED"},
    {"claim": "strong result (research agent's summary)",
     "evidence": "Table 2: interquartile range of the speedup is 1.0x to 1.5x",
     "status": "REFUTED", "load_bearing": false},
    {"claim": "median speedup of 1.2x over 40 scenes",
     "evidence": "Table 2, self-reported; method, scenes and hardware not in the snapshot",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "12x speedup on a scene with a single moved object",
     "evidence": "reported best case, n=1; the paper says most real scenes change many objects",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are Android build time, crash noise, localization, devlog)",
          "overlap": "Unity 6 already handles baking; this would be custom work beside it",
          "burden": "implementing and maintaining a research algorithm in our pipeline",
          "risks": ["unreviewed preprint", "license of any reference code not stated in the snapshot"],
          "cost": {"price": "free to read", "tier": "n/a", "limits": "none", "terms": "license not stated in snapshot",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the research agent that the paper's median speedup is 1.2x (IQR 1.0x-1.5x), that 12x is a single best case, and do not implement it",
                  "owner": "operator",
                  "done_when": "the research agent's recommendation is withdrawn or corrected",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```