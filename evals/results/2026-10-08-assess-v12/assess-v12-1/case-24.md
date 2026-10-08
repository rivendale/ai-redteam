VERDICT: watch. The paper does not show a 30% gain: its own Table 2 shows +0.02 Recall@10 (+2.8% relative, p = 0.34, not significant), so there is no quality reason to switch. Its real claim, a 4x smaller embedding with no significant loss, may matter later for goal 3 (semantic search over internal notes).

WHAT IT IS: Paper 2610.00412, "Compact embeddings for local search", an arXiv-style preprint posted 2026-10-03 at papers.example.test. I worked only from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json) and could not open the live page. The snapshot holds the abstract, Table 2 and one Discussion sentence. It does not name the two embedding models, their licenses, dimensions or the four tasks.

CLAIMS CHECKED:
- **"This paper shows a 30% gain in retrieval quality"** (the sender's agent's claim). **REFUTED.** Table 2 gives Recall@10 of 0.71 for the standard embedding and 0.73 for the compact one. That is +0.02, or +2.8% relative, with paired bootstrap p = 0.34, which the paper itself calls not significant. No figure in the snapshot is near 30%. *The verdict rests on this claim.*
- **"So we should switch embeddings"** (the sender's inference, split from the fact above). The premise is refuted. The paper's evidence does not show the compact embedding retrieves better: the difference is within noise. Whether switching would help on our notes is something nothing in the item settles. **UNVERIFIED**, and the verdict does not rest on it.
- **"The compact embedding is 4x smaller"** (the paper, Discussion). This is stated, but the snapshot shows no sizes or dimensions to check it against. **PROBABLE.** The verdict does not rest on it.
- **"No significant loss in quality"** (the paper). The design is a paired comparison on 4 retrieval tasks with a paired bootstrap. The snapshot does not give the task size or corpus. A non-significant difference is not proof that the two are equivalent: the paper gives no equivalence margin, and 4 tasks is a small sample. A per-task breakdown would change the conclusion if it showed a large loss on any task like ours, meaning short internal notes. **PROBABLE.** The verdict does not rest on it.

FIT:
- **Goal:** Goal 3, "Make internal notes searchable by meaning". It touches only the size of the semantic index, not its quality.
- **Overlap:** Semantic search already runs on SQLite with sqlite-vec. A switch would replace the embedding model in that setup, not add a capability. It would also mean re-embedding every note and re-checking search quality.
- **Burden:** A model swap, a full re-index, and a before/after quality check on our own notes.
- **Cost:** Reading the paper is free. The models' cost and licenses are unknown because the snapshot does not name them. That must be checked against our license rule (MIT, Apache-2.0 or BSD if we ship it). If the compact model is a hosted API, using it would send company data to a new party and would need approval.
- **Risks:**
  - The models are unnamed, so license and hosting are unknown.
  - The paper is an unreviewed preprint with 4 tasks.
  - The "no loss" result is non-significance, not demonstrated equivalence.
  - The 30% figure being passed around is wrong.

NEXT ACTION: The operator, or whoever owns the colleague's agent, replies to the colleague. The reply corrects the figure: Table 2 shows +2.8% relative, p = 0.34, not 30%. It says there is no quality case for switching, and that we will revisit only if index size or local search speed becomes a problem for goal 3, and only once the models and their licenses are named.
- Done when: the correction is sent and the item is logged as watch with that trigger.
- Hand-off: none. If the trigger fires later, hand the paper to `glean`.

CONFIDENCE: high. The item is resolved from a dated snapshot. The load-bearing claim is REFUTED by the paper's own table, and the context file is present. Two things limit any later switching decision, though not this verdict: the snapshot is abridged, and the models and their licenses are unnamed.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "paper",
           "identity": "2610.00412, 'Compact embeddings for local search', arXiv-style preprint posted 2026-10-03 (saved snapshot captured 2026-10-08; models not named)",
           "resolved": true},
  "claims": [
    {"claim": "the paper shows a 30% gain in retrieval quality (sender's agent)",
     "evidence": "Table 2: Recall@10 0.71 vs 0.73, +2.8% relative, paired bootstrap p = 0.34, not significant",
     "status": "REFUTED"},
    {"claim": "so switching embeddings would improve our retrieval quality (sender's inference)",
     "evidence": "premise refuted; paper reports no significant difference; nothing in the item tests our notes",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the compact embedding is 4x smaller",
     "evidence": "Discussion sentence; no sizes or dimensions given in the snapshot",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "no significant loss in quality",
     "evidence": "paired comparison on 4 retrieval tasks, p = 0.34; non-significance, no equivalence margin",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3), index size only",
          "overlap": "semantic search already runs on SQLite with sqlite-vec; a switch replaces the model and needs a full re-index",
          "burden": "model swap, re-embed all notes, before/after quality check",
          "risks": ["models and licenses not named; must meet MIT/Apache-2.0/BSD if shipped",
                    "if hosted, company data would go to a new party (needs approval)",
                    "unreviewed preprint, 4 tasks, non-significance is not equivalence"],
          "cost": {"price": "free to read", "tier": "n/a", "limits": "model cost unknown",
                   "terms": "model licenses not stated in snapshot", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the colleague correcting the figure (+2.8% relative, p = 0.34, not 30%); log as watch, revisit only if index size or local search speed becomes a problem and the models and licenses are named",
                  "owner": "operator",
                  "done_when": "correction sent and item logged as watch with its trigger",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```