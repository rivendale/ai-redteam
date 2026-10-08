VERDICT: watch. The post offers nothing usable for goal 3 as captured: it lists three titles that touch searching by meaning (#3, #8, #9), but gives no links, IDs or authors, so none of those papers can be read or judged yet.

WHAT IT IS: A post titled "Ten papers of the week", dated 2026-10-07, from https://posts.example.test/papers-of-the-week-41. The author is not named in the snapshot. I worked from a saved copy captured on 2026-10-08 (work/snapshot.md, work/meta.json), and the post is resolved. The snapshot holds only ten titles plus the note "Each entry is one sentence. No links." The one-sentence descriptions themselves were not captured. None of the ten papers is resolved: there is no arXiv ID, DOI, author or venue for any of them.

CLAIMS CHECKED:
- **The post gives no links or identifiers for any paper.** Evidence: the snapshot says "No links", and no IDs or authors appear anywhere. CONFIRMED. *Load-bearing.*
- **Some entries bear on goal 3.** This is my inference from titles alone, so the claim is split:
  - The post lists "Retrieval with learned sparse vectors" (#3), "Embedding drift over time" (#8) and "Evaluating RAG pipelines" (#9). CONFIRMED.
  - Those papers are useful for searching our notes by meaning. PROBABLE for #8, which looks like a direct fit because we store embeddings in sqlite-vec and drift affects them. PROBABLE for #3 as a possible sparse+dense hybrid next to our dense search. PROBABLE but weaker for #9. *Load-bearing.*
- **These are notable papers of the week.** Evidence: the post's framing only. UNVERIFIED. Not load-bearing.

FIT:
- **Goal:** goal 3, making internal notes searchable by meaning, through entries #8, #3 and #9. The other seven entries serve none of our goals.
- **Overlap:** we already run semantic search on SQLite with sqlite-vec. Anything from these papers would refine that setup, not replace it.
- **Burden:** reading only. There is nothing to install.
- **Cost:** the post is free. Paper access is unknown until the papers are identified.
- **Risks:** none from the post itself. The real risk is acting on titles alone.

NEXT ACTION: The operator finds the actual papers for #8 "Embedding drift over time" and #3 "Retrieval with learned sparse vectors", for example by searching arXiv by title near 2026-10-07. Then send each one back to `assess` as its own item. Done when each has an arXiv ID or DOI, or is recorded as not findable. Hand-off: none for now. `glean` comes only after a paper is resolved and assessed as useful.

CONFIDENCE: medium. The post and the context file are both present, but the snapshot holds only titles (the one-sentence descriptions were not captured), and the fit judgment rests on those titles, not on the papers.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "\"Ten papers of the week\" post, 2026-10-07, posts.example.test/papers-of-the-week-41, author not named; saved copy captured 2026-10-08, titles only", "resolved": true},
  "claims": [
    {"claim": "the post gives links or identifiers for its papers", "evidence": "snapshot states 'No links'; no ids, authors or venues appear", "status": "REFUTED"},
    {"claim": "the post lists 'Retrieval with learned sparse vectors' (#3), 'Embedding drift over time' (#8) and 'Evaluating RAG pipelines' (#9)", "evidence": "snapshot.md titles", "status": "CONFIRMED"},
    {"claim": "those three papers are useful for searching our notes by meaning", "evidence": "inference from titles only; #8 bears on stored sqlite-vec embeddings, #3 on sparse+dense hybrid, #9 weaker", "status": "PROBABLE"},
    {"claim": "these are the notable papers of the week", "evidence": "the post's own framing; no selection method given", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3: make internal notes searchable by meaning (entries #8, #3, #9); other entries serve no goal",
          "overlap": "SQLite with sqlite-vec already provides semantic search; papers would refine it, not replace it",
          "burden": "reading only",
          "risks": ["acting on titles alone: no paper is identified", "snapshot omits the one-sentence descriptions"],
          "cost": {"price": "free", "tier": "public post", "limits": "paper access unknown until identified", "terms": "not stated", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Find the arXiv id or DOI for #8 'Embedding drift over time' and #3 'Retrieval with learned sparse vectors' and send each to assess as its own item",
                  "owner": "operator", "done_when": "each paper has an arXiv id or DOI, or is recorded as not findable",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```