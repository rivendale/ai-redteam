VERDICT: needs-decision, because connecting our notes uploads every note's text and vectors to NoteSync's cloud, a new third party, and keeps them for 90 days after disconnecting. That needs operator approval (data_to_new_party), and it probably also means a new account, though the snapshot does not say. My lean is skip: we already do semantic search with sqlite-vec, which keeps the data local.

WHAT IT IS: NoteSync, a hosted note-search product. I read its "How NoteSync works" docs page (https://notesync.example.test/docs/how-it-works) from a saved snapshot captured 2026-10-08, not live. Price as captured is "free under 20 users", and meta.json records `data_leaves_machine: true`. The page gives no other terms, tier limits or license.

CLAIMS CHECKED:
- **"NoteSync search is free"** (sender). This splits in two:
  - (a) "Free for teams under 20" is CONFIRMED by the snapshot and meta.json.
  - (b) "Free for us" is UNVERIFIED, because the context file does not give our team size. Not load-bearing.
- **"It does semantic search"** (sender). CONFIRMED by its own docs: it embeds each note with its models and searches the vectors on its servers. Not load-bearing, since we already have this.
- **"Connecting a folder uploads each note, its vectors and a copy of the text to NoteSync's cloud. Searches run on their servers."** CONFIRMED by the snapshot and by `data_leaves_machine: true`. Load-bearing.
- **"Data is retained for 90 days after you disconnect."** CONFIRMED by the snapshot. Load-bearing: we could not quickly pull our notes back out.

FIT:
- **Goal:** goal 3, "Make internal notes searchable by meaning."
- **Overlap:** SQLite with sqlite-vec is already in use for semantic search. NoteSync would do the same job, with the difference that it runs on someone else's servers.
- **Burden:** a new hosted service, folder connection and sync, and probably a new account (the snapshot does not say).
- **Cost:** $0 only if we stay under 20 users. Our size is unknown, and growing past 20 would turn into a paid plan, which needs approval. The snapshot shows no other terms. Checked 2026-10-08 from the snapshot.
- **Risks:**
  - Company notes leave our machines, which breaks the rule "No company data goes to a new third party without approval".
  - Copies stay with NoteSync for 90 days after disconnecting.
  - The embeddings are produced by NoteSync's own models, which is lock-in.
  - Pricing depends on headcount.
  - License, telemetry and project health are not stated.

NEXT ACTION: The operator decides whether internal notes may be sent to NoteSync, with 90-day retention after disconnect. The alternative is to point goal 3 at the existing sqlite-vec setup.
- Owner: operator.
- Done when: the decision is recorded. If it is "no", nothing is connected.
- Stop condition: none, because this is not a trial.
- Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot (2026-10-08, not read live), the context file is present, and every load-bearing claim is CONFIRMED. The one open point is our team size, which affects only the price, not the verdict.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "product",
           "identity": "NoteSync, docs page 'How NoteSync works' (https://notesync.example.test/docs/how-it-works), free under 20 users, read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "free for teams under 20 users", "evidence": "snapshot: 'free for teams under 20'; meta.json price 'free under 20 users'", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "free for us (sender: 'notesync search is free')", "evidence": "context file does not state our team size", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "does semantic search", "evidence": "snapshot: embeds each note with its models, searches run on its servers", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "connecting a folder uploads each note's text and vectors to NoteSync's cloud", "evidence": "snapshot text; meta.json data_leaves_machine: true", "status": "CONFIRMED"},
    {"claim": "data retained for 90 days after disconnect", "evidence": "snapshot: 'Data is retained for 90 days after you disconnect'", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)",
          "overlap": "SQLite with sqlite-vec already provides semantic search locally",
          "burden": "new hosted service and folder sync; likely a new account (not stated)",
          "risks": ["company notes sent to a new third party, which needs approval",
                    "copies retained 90 days after disconnect",
                    "embeddings made by NoteSync's own models (lock-in)",
                    "becomes paid at 20 or more users",
                    "license, telemetry and project health not stated"],
          "cost": {"price": "free", "tier": "teams under 20 users", "limits": "under 20 users",
                   "terms": "uploads note text and vectors to its cloud; 90-day retention after disconnect",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether internal notes may be sent to NoteSync (90-day retention); lean is to keep using sqlite-vec for goal 3",
                  "owner": "operator", "done_when": "decision recorded; nothing is connected unless approved",
                  "stop_condition": "none: not a trial", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```