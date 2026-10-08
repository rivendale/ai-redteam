VERDICT: try. The paper is a cheap, relevant idea for goal 3. On 6 datasets it reports a 4x smaller index for about −0.4 Recall@10, but nothing shows that holds for our notes, so measure it on our own index before changing anything.

WHAT IT IS: Preprint "Int8 embeddings for local semantic search", id 2608.11873, posted 2026-08-21. It was read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The snapshot holds only an abstract-length summary:
- no authors are listed;
- the six datasets are not named;
- the repository link and its contents are not included.

CLAIMS CHECKED:
1. **"int8 quantization reduced index size 4x".**
   - Evidence: the paper's own result. It also follows arithmetically from 32-bit floats becoming 8-bit integers.
   - Status: CONFIRMED. The verdict rests on this.
2. **"Recall@10 changed by −0.4 points on average (range −1.1 to +0.2), with 95% intervals, on 6 retrieval datasets".**
   - Evidence: the design is a benchmark comparison across 6 datasets, measuring Recall@10 against an unquantized baseline, with intervals reported.
   - What I could not check: the datasets are unnamed, and the per-dataset tables are not in the snapshot.
   - What would change the conclusion: datasets that look nothing like short internal notes, or a different embedding model from ours.
   - Status: PROBABLE. The verdict rests on this.
3. **Split from claim 2: "so the recall loss will be similarly small on our notes".**
   - This is our inference, not the paper's claim.
   - Nothing in the item covers our corpus, queries or embedding model.
   - Status: UNVERIFIED. Not load-bearing; it is exactly what the trial tests.
4. **"Code and the exact evaluation script are in the linked repository (Apache-2.0)".**
   - Evidence: the paper's statement only. The repository was not read and is not in the snapshot.
   - Status: UNVERIFIED. Not load-bearing.

FIT:
- **Goal:** goal 3, "make internal notes searchable by meaning". It makes the index smaller and possibly faster. Note that the context file names no size or speed problem with the current index, so the gain may be small.
- **Overlap:** we already run semantic search on SQLite with sqlite-vec. This paper offers a technique to apply inside that setup, not a replacement. Check what our sqlite-vec setup already supports for int8 vectors before adding anything new.
- **Burden:**
  - a one-off re-index of the notes into int8;
  - a small set of our own queries with known good results, used to compare recall;
  - no new service or account.
- **Cost:** free (a paper, as read 2026-10-08).
- **Risks:**
  - Recall loss on our data is unknown.
  - The code's license is stated as Apache-2.0, which our rules allow, but it is unverified. Check the repo's LICENSE before vendoring any of it.
  - No data leaves the machine.

NEXT ACTION:
- **Action:** Build a 20–50 query test set from real note searches. Re-index the notes as int8 alongside the current float index, then compare Recall@10 and index size.
- **Owner:** operator.
- **Done-when:** both indexes have been scored on the same queries and the size and recall deltas are written down.
- **Stop condition:** stop and keep float vectors if Recall@10 drops more than about 1 point on our queries, or if the size saving makes no practical difference to us.
- **Hand-off:** `glean` on the paper and its evaluation script, for the quantization and evaluation method.

CONFIDENCE: medium. Limits:
- It was judged from a saved, abstract-only snapshot with no authors, unnamed datasets and an unread repository.
- It is unknown whether the result carries over to our notes and embedding model.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "2608.11873, 'Int8 embeddings for local semantic search', preprint posted 2026-08-21 (saved snapshot captured 2026-10-08; authors and datasets not in snapshot)",
           "resolved": true},
  "claims": [
    {"claim": "int8 quantization reduced index size 4x", "evidence": "paper's reported result; follows from 32-bit to 8-bit storage", "status": "CONFIRMED"},
    {"claim": "Recall@10 changed by -0.4 points on average (range -1.1 to +0.2) across 6 retrieval datasets, with 95% intervals", "evidence": "paper's benchmark summary; datasets unnamed and tables not in snapshot", "status": "PROBABLE"},
    {"claim": "the recall loss will be similarly small on our internal notes", "evidence": "inference only; nothing in the item covers our corpus or embedding model", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "code and exact evaluation script are in a linked Apache-2.0 repository", "evidence": "paper's statement only; repository not read and not in snapshot", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3): smaller index for the same search",
          "overlap": "SQLite with sqlite-vec already does semantic search; this is a technique to apply inside it, not a replacement",
          "burden": "one-off re-index into int8 plus a small set of our own test queries; no new service or account",
          "risks": ["recall loss on our notes is unknown", "repo license stated as Apache-2.0 but unverified; check before vendoring", "context names no index-size problem, so the gain may be small"],
          "cost": {"price": "free", "tier": "paper", "limits": "none", "terms": "code license stated as Apache-2.0, unverified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Re-index the notes as int8 alongside the current float index and compare Recall@10 and index size on 20-50 real note queries",
                  "owner": "operator", "done_when": "both indexes are scored on the same queries and the size and recall deltas are recorded",
                  "stop_condition": "stop and keep float vectors if Recall@10 drops more than about 1 point on our queries or the size saving makes no practical difference",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```