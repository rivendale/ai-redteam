VERDICT: skip. It does fit goal 3, but it does the same job as the SQLite + sqlite-vec semantic search already in use, so it would be a second tool, not a new capability.

WHAT IT IS: example-org/vecsearch-lite (default branch `main`, no commit sha in the snapshot), Apache-2.0, 860 stars, last push and last release 2026-09-02, not archived. A Python 3.9+ package installed from PyPI (`pip install vecsearch-lite`). Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). Only the README text was captured, not the source.

CLAIMS CHECKED:
- **"Local semantic search over notes" (sender and README).** This splits into three parts:
  - **It does semantic search over a notes folder: PROBABLE.** The README says it embeds each note, stores the vectors in a SQLite file and answers "find notes about X". This is the item's own description; no code or demo was captured.
  - **The vectors are stored locally: PROBABLE.** The README says "stores the vectors in a SQLite file".
  - **Embedding happens on the machine: UNVERIFIED.** The README says "local" but never names the embedding model or says where embeddings are computed. Nothing in the snapshot rules out a remote embedding API. If it uses one, note text would leave the machine.
- **"Goal 3, right?" (sender).** This also splits:
  - **It matches goal 3: CONFIRMED.** Goal 3 is "Make internal notes searchable by meaning," and the README describes exactly that.
  - **It would be a useful addition for goal 3: not supported.** The context file already lists "SQLite with sqlite-vec for semantic search," which uses the same approach. The verdict rests on this part.
- **Apache-2.0 license: CONFIRMED** (meta.json and README agree).
- **Maintained: CONFIRMED.** Pushed 2026-09-02 and not archived. The 860 stars are popularity, not evidence of quality.

FIT:
- **Goal:** goal 3 (notes searchable by meaning).
- **Overlap:** SQLite with sqlite-vec is already in use for semantic search. vecsearch-lite is also a vector index in a SQLite file. The context file does not say whether the existing setup already indexes the internal notes. Goal 3 is still listed as open, so there may be a gap, but it would be closer to fill it with the stack already in place.
- **Burden:** a new pip dependency, a second vector index to keep in sync, and re-embedding the notes.
- **Cost:** free and open source (Apache-2.0), checked 2026-10-08 from the snapshot.
- **Risks:**
  - The license is allowed for shipping and vendoring.
  - The embedding model and where it runs are unknown, so data might leave the machine. If it does, that needs approval under the "no company data to a new third party" rule.
  - It may download a model on first use, which the snapshot does not mention.
  - Project health looks fine.

NEXT ACTION: Whoever owns the sqlite-vec setup checks whether it already indexes the internal notes. If it does not, they scope extending it to the notes folder rather than adding vecsearch-lite.
- **Owner:** the owner of the sqlite-vec setup, or the operator.
- **Done when:** there is a written yes/no on whether the notes are covered by sqlite-vec today, and a short plan if they are not.
- **Hand-off:** none.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. What limits confidence:
- Only the README was captured, with no source and no commit sha.
- The context file does not say whether sqlite-vec already covers the notes. That decides whether goal 3 has a gap at all, though the overlap itself is clear either way.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/vecsearch-lite@main (no sha in snapshot; Apache-2.0, 860 stars, last push 2026-09-02, not archived; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "does semantic search over a notes folder", "evidence": "README: embeds each note, stores vectors in SQLite, answers 'find notes about X'; no code captured", "status": "PROBABLE", "load_bearing": false},
    {"claim": "vectors are stored locally", "evidence": "README: 'stores the vectors in a SQLite file'", "status": "PROBABLE", "load_bearing": false},
    {"claim": "embedding runs on the machine (fully local)", "evidence": "README says 'local' but names no embedding model or where embeddings are computed", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it matches goal 3 (notes searchable by meaning)", "evidence": "README description matches goal 3 text in context file", "status": "CONFIRMED"},
    {"claim": "it would add a capability we do not already have", "evidence": "context file: SQLite with sqlite-vec already in use for semantic search, same approach", "status": "REFUTED"},
    {"claim": "license is Apache-2.0", "evidence": "meta.json and README agree", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "project is maintained", "evidence": "meta.json: last push 2026-09-02, archived false", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)",
          "overlap": "SQLite with sqlite-vec is already in use for semantic search; same job and approach",
          "burden": "new pip dependency, a second vector index to keep in sync, re-embedding the notes",
          "risks": ["Apache-2.0, allowed by license rules",
                    "embedding model and location unknown; note text could leave the machine via a remote API",
                    "may download a model on first use (not stated)"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Check whether the existing sqlite-vec setup already indexes the internal notes; if not, scope extending it to the notes folder instead of adding vecsearch-lite",
                  "owner": "owner of the sqlite-vec setup (or operator)",
                  "done_when": "written yes/no on whether notes are covered today, plus a short extension plan if not",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```