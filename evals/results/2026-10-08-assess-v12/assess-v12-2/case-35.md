VERDICT: watch. The paper's result looks sound, but our goal 3 is search by meaning, not a smaller index. Nothing in our context says index size or memory is a problem, and sqlite-vec, which we already use, is the place we would apply it anyway.

WHAT IT IS: Paper 2608.11873, "Int8 embeddings for local semantic search", a preprint posted 2026-08-21. I read it from the saved snapshot captured 2026-10-08 (work/meta.json), not live. The snapshot has only an abstract-level summary. It does not give authors, dataset names, embedding models or the float baseline (fp32 or fp16).

CLAIMS CHECKED:
- **int8 quantization cuts index size 4x.** The paper reports this. It matches the arithmetic for fp32 to int8 vectors, but the snapshot does not state the baseline. **PROBABLE.** The verdict rests on this claim.
- **Recall@10 changes by -0.4 points on average (range -1.1 to +0.2) across 6 retrieval datasets.** Results come from 6 datasets, but the snapshot does not name them or the models. The size of the change is small and is consistent with the range. **PROBABLE.** The verdict rests on this claim. Three things would change the conclusion:
  - our notes being out of domain for those datasets;
  - a different embedding model;
  - a baseline that is already fp16.
- **95% intervals are reported.** The snapshot states this but does not show the intervals. **PROBABLE**, not load-bearing.
- **The code and exact eval script are in a linked repository under Apache-2.0.** The repo was not read, so its license and contents are unknown. **UNVERIFIED**, not load-bearing.
- No text in the snapshot tries to direct the reader.

FIT:
- **Goal:** Goal 3, making internal notes searchable by meaning. This paper touches the index size and cost of that search, not its quality.
- **Overlap:** We already use SQLite with sqlite-vec. sqlite-vec has int8 and bit vector types. I know that from general knowledge and did not check it in this session. Using this paper would mean changing a setting in our current index, not adding a tool.
- **Burden:** Small if we ever do it: re-embed or convert the index, then check recall on our own queries.
- **Cost:** The paper is free (checked 2026-10-08). The linked repo's terms were not read.
- **Risks:** We would see a small recall loss on our data and have to measure it. No data leaves the machine, and nothing gets installed.

NEXT ACTION: The operator notes the paper against goal 3, with this trigger: revisit if the sqlite-vec notes index grows large enough that disk, memory or query latency becomes a problem.
- **Owner:** operator.
- **Done when:** the note and its trigger are recorded.
- **Hand-off:** none for now. If the trigger fires, hand off to `glean` to read the paper and repo for the exact method and eval script.

CONFIDENCE: medium. The snapshot is thin: it gives no authors, datasets, models or baseline precision, and the repo was not read. Our current index size is not in the context file, and that is what decides whether this helps us.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "paper", "identity": "2608.11873, 'Int8 embeddings for local semantic search', preprint posted 2026-08-21 (saved snapshot captured 2026-10-08; authors, datasets and models not in snapshot)",
           "resolved": true},
  "claims": [
    {"claim": "int8 quantization reduces index size 4x", "evidence": "reported in the paper; matches fp32-to-int8 arithmetic, but the baseline precision is not stated in the snapshot", "status": "PROBABLE"},
    {"claim": "Recall@10 changes by -0.4 points on average (range -1.1 to +0.2) on 6 retrieval datasets", "evidence": "reported results on 6 datasets; datasets and models not named in the snapshot", "status": "PROBABLE"},
    {"claim": "95% intervals are reported", "evidence": "stated in the snapshot; the intervals themselves are not shown", "status": "PROBABLE", "load_bearing": false},
    {"claim": "code and exact evaluation script are in a linked repository under Apache-2.0", "evidence": "stated in the snapshot; the repository was not read", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3 (notes searchable by meaning), but it addresses index size, not search quality",
          "overlap": "SQLite with sqlite-vec already runs our semantic search; sqlite-vec has int8 vector types (general knowledge, not checked here), so this would be a setting in the current index, not a new tool",
          "burden": "if applied: convert or re-embed the index and check recall on our own queries",
          "risks": ["small recall loss on our data, which would need measuring", "linked repo license not read", "no data leaves the machine"],
          "cost": {"price": "free", "tier": "open preprint", "limits": "none", "terms": "repo stated Apache-2.0, not verified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Note the paper against goal 3 with a trigger: revisit if the sqlite-vec notes index size, memory or query latency becomes a problem",
                  "owner": "operator", "done_when": "the note and its trigger are recorded",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```