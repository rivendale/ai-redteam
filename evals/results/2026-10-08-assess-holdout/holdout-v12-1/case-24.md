VERDICT: skip. The summary's "12x faster" is the paper's single best case; its own median over 40 scenes is 1.2x, and none of our goals involves mesh baking.

WHAT IT IS: Paper 2610.00418, "Fast mesh baking by incremental recomputation", a preprint posted 2026-10-02 at papers.example.test. I read it from the saved snapshot captured 2026-10-08, not live. The snapshot shows no authors, venue or code release, so peer review and code license are unknown.

CLAIMS CHECKED:
- **"Paper shows 12x faster mesh baking"** (research agent's summary): **REFUTED**. Table 2 gives a median of 41.0 s → 34.2 s, which is 1.2x. The 12x figure is a "best case… on a scene with a single moved object", and the authors add that "most scenes in practice change many objects." The verdict rests on this.
- **"12x on a scene with a single moved object"** (the fact inside the summary): **PROBABLE**. The paper reports it for one scene, but the snapshot gives no method or variance. The verdict does not rest on this.
- **"Median 1.2x faster over 40 scenes, IQR 1.0x–1.5x"** (paper's main result): **PROBABLE**. This is a preprint, the baseline is not named in the snapshot, and the result is unreplicated. The lower quartile of 1.0x means at least a quarter of scenes saw roughly no gain. The verdict rests on this.
- **"Strong result, recommend we implement it"** (the summary's inference): **REFUTED**. The paper's own numbers show a modest, variable speedup. The verdict rests on this.

FIT:
- **Goal:** none found. The goals are Android build under 10 min, crash noise, five languages, and the devlog. Mesh baking is not named as a build bottleneck. Goal 1 could only be touched if baking turns out to be a large share of the Android build, and nothing here says it is.
- **Overlap:** Unity 6 already does our baking.
- **Burden:** We would have to implement a research algorithm ourselves inside, or alongside, Unity's bake pipeline, then maintain it.
- **Cost:** $0 to read; engineering time to build.
- **Risks:** This is an unreviewed preprint. No code release or license appears in the snapshot, so any code we wrote from it would need the MIT/Apache/BSD/zlib check if shipped. The expected gain is about 1.2x on a step we haven't shown matters.

NEXT ACTION: Reply to the research agent correcting the summary: the median is 1.2x, and 12x is the single-moved-object best case. Close the item.
- **Owner:** operator, or the research agent.
- **Done when:** the summary is corrected wherever it was recorded.
- **Hand-off:** none.
- **What would change this to watch:** a Jenkins build profile showing mesh baking is a large share of the Android build time.

CONFIDENCE: high. The item is resolved from a dated snapshot, the load-bearing claims are settled by the paper's own Table 2, and the context file is present. One limit: the snapshot is short, so details such as the baseline and authors are missing. Those details would not change the verdict.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "paper",
           "identity": "2610.00418, 'Fast mesh baking by incremental recomputation', preprint posted 2026-10-02 (read from snapshot captured 2026-10-08; authors, venue and code release not shown)",
           "resolved": true},
  "claims": [
    {"claim": "paper shows 12x faster mesh baking (research agent's summary)",
     "evidence": "Table 2: median 41.0 s -> 34.2 s (1.2x) over 40 scenes; 12x is a single best-case scene with one moved object, and the authors note most scenes change many objects",
     "status": "REFUTED"},
    {"claim": "12x speedup on a scene with a single moved object",
     "evidence": "reported once in the paper as a best case; no method or variance in the snapshot",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "median 1.2x faster over 40 scenes, IQR 1.0x-1.5x",
     "evidence": "Table 2 of the preprint; baseline not named in the snapshot, unreplicated",
     "status": "PROBABLE"},
    {"claim": "strong result, recommend we implement it (research agent's inference)",
     "evidence": "the paper's own median of 1.2x and lower quartile of 1.0x show a modest, variable gain",
     "status": "REFUTED"}
  ],
  "fit": {"goal": "none found (mesh baking is not named in any goal; goal 1, Android build time, only if baking proves to be a large share of it)",
          "overlap": "Unity 6 already handles baking",
          "burden": "implement and maintain a research algorithm inside or alongside Unity's bake pipeline",
          "risks": ["unreviewed preprint", "no code release or license shown; shipped code must be MIT/Apache-2.0/BSD/zlib", "expected gain about 1.2x on a step not shown to matter"],
          "cost": {"price": "free to read; engineering time to implement", "tier": "n/a", "limits": "none",
                   "terms": "preprint; no code license shown", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the research agent the summary is wrong (median 1.2x; 12x is the single-moved-object best case) and close the item; revisit only if a Jenkins build profile shows baking is a large share of Android build time",
                  "owner": "operator",
                  "done_when": "the corrected summary is recorded and the item is closed",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```