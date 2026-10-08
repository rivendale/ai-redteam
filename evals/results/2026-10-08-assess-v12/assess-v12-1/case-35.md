VERDICT: try. A short, bounded trial of int8 embeddings in our existing sqlite-vec notes index is cheap. But the context file names no index-size or memory problem, so this improves goal 3's current setup rather than closing a gap.

WHAT IT IS: Paper, preprint id 2608.11873, "Int8 embeddings for local semantic search", posted 2026-08-21. I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The snapshot holds only abstract-level text. It does not name the authors, the 6 datasets, the embedding models, or any tables.

CLAIMS CHECKED:
- **"int8 quantization reduced index size 4x":** PROBABLE. This follows from the arithmetic: float32 is 4 bytes per value and int8 is 1. The snapshot shows no measurement of the full index, including overhead. Not load-bearing.
- **"Recall@10 changed by −0.4 points on average (range −1.1 to +0.2) across 6 retrieval datasets":** PROBABLE, and load-bearing. The design is a benchmark comparison on 6 datasets, with 95% intervals said to be reported. The snapshot has no tables, does not name the datasets, and does not give the models or the quantization method (per-dimension or global scaling, calibration). Two things would change the conclusion: datasets unlike our internal notes, or an embedding model that quantizes worse than the ones tested.
- **"Code and the exact evaluation script are in the linked repository (Apache-2.0)":** UNVERIFIED. I did not read the repo, so its existence, license and contents are not checked. Not load-bearing, because we would reimplement the idea rather than vendor the code. Apache-2.0 would pass our license rule if confirmed.
- **No text in the item tries to direct the reader.**

FIT:
- **Goal:** goal 3, "make internal notes searchable by meaning". The paper offers a smaller index at nearly the same recall.
- **Overlap:** we already run SQLite with sqlite-vec for semantic search. The paper is a storage technique for that setup, not a new tool. Any change happens inside our existing index.
- **Burden:** a quantization step at index time and a re-index. No new service or account.
- **Cost:** free. It is a paper, and the trial uses our own tooling. Checked 2026-10-08.
- **Risks:**
  - Some recall loss on our own corpus, which the paper did not test.
  - The context file states no size or memory pressure, so the benefit may be small.
  - No data leaves the machine.

NEXT ACTION:
- **Action:** Pull the method details from the paper with `glean`. Then the operator builds an int8 copy of the notes index in sqlite-vec and compares Recall@10 against the float32 index on 20–30 real queries.
- **Owner:** operator.
- **Done when:** the index size and recall for both versions are recorded side by side.
- **Stop condition:** stop and keep float32 if Recall@10 drops by more than 1 point, or if the current index size causes no real problem.
- **Hand-off:** `glean` for the paper.

CONFIDENCE: medium. The context file is present, and the load-bearing claim is PROBABLE. Three things limit confidence: I worked from an abstract-only snapshot rather than a live read, the paper's datasets and models are unnamed, and nothing tells us whether our notes corpus behaves like its benchmarks.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "preprint 2608.11873, 'Int8 embeddings for local semantic search', posted 2026-08-21 (read from saved snapshot captured 2026-10-08; abstract-level text only)",
           "resolved": true},
  "claims": [
    {"claim": "int8 quantization reduces index size 4x", "evidence": "stated in snapshot; consistent with float32 to int8 arithmetic, no full-index measurement shown", "status": "PROBABLE", "load_bearing": false},
    {"claim": "Recall@10 changes by -0.4 points on average (range -1.1 to +0.2) across 6 retrieval datasets, with 95% intervals", "evidence": "abstract-level statement in snapshot; datasets, models, method and tables not in snapshot", "status": "PROBABLE"},
    {"claim": "code and exact evaluation script are in a linked Apache-2.0 repository", "evidence": "repo not read; only the paper's own statement", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3); improves the existing setup, no stated size problem",
          "overlap": "SQLite with sqlite-vec already provides semantic search; this is a storage technique for it, not a new tool",
          "burden": "a quantization step at index time and a one-off re-index",
          "risks": ["recall loss on our notes corpus is untested", "benefit may be small since no index-size pressure is stated", "repo license unverified (irrelevant if we reimplement)"],
          "cost": {"price": "free", "tier": "paper", "limits": "none", "terms": "preprint; linked code claimed Apache-2.0, unverified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Glean the method details, then build an int8 copy of the notes index in sqlite-vec and compare Recall@10 and size against float32 on 20-30 real queries",
                  "owner": "operator", "done_when": "size and Recall@10 for both indexes are recorded side by side",
                  "stop_condition": "stop and keep float32 if Recall@10 drops more than 1 point or the current index size causes no real problem", "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```