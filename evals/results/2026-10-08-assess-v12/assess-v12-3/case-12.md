```
VERDICT: needs-decision — connecting our notes uploads company data to a new third party (NoteSync's cloud), which needs operator approval (it probably also needs a new account, though the snapshot does not say so). My lean is skip: SQLite with sqlite-vec already does semantic search for us locally.
WHAT IT IS: NoteSync, a hosted product. Source is the docs page "How NoteSync works" (https://notesync.example.test/docs/how-it-works), read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. Price as read: free for teams under 20 users. Data leaves the machine (meta.json: data_leaves_machine: true).
CLAIMS CHECKED:
  - "free" (sender) → split:
      · free for teams under 20: CONFIRMED by the snapshot ("free for teams under 20") and meta.json ("free under 20 users"). Not load-bearing.
      · free for us: UNVERIFIED. Our team size is not in the context file, and pricing for 20 or more users is not given. Not load-bearing.
  - "does semantic search" (sender): CONFIRMED. The snapshot says it "embeds it with our models and stores the vectors"; "Searches run on our servers." Load-bearing, because it is the same job as our existing sqlite-vec setup.
  - Connecting a folder sends note contents off our machines: CONFIRMED. The snapshot says it "uploads each note to our cloud" and "stores … a copy of the text". Load-bearing.
  - Data is kept after disconnecting: CONFIRMED. The snapshot says "retained for 90 days after you disconnect." Load-bearing, because disconnecting does not undo the exposure.
  No text in the item tries to direct the reader.
FIT:
  - Goal: goal 3, "Make internal notes searchable by meaning".
  - Overlap: SQLite with sqlite-vec already does semantic search. NoteSync would duplicate it, not fill a gap.
  - Burden: a connected folder and a new external service. An account is likely but not stated.
  - Cost: free under 20 users, read 2026-10-08. Pricing at 20 or more users is unknown. The budget is $0 without approval.
  - Risks: full note text is uploaded to a third party (the constraint "No company data goes to a new third party without approval" applies), 90-day retention after disconnect, embeddings depend on their models and servers (lock-in), and the snapshot shows no license or terms.
NEXT ACTION: The operator decides whether internal notes may go to NoteSync. My recommendation is to decline and keep sqlite-vec for goal 3. Owner: operator. Done when the decision is recorded. Hand-off: none.
CONFIDENCE: high. The item is resolved from the 2026-10-08 snapshot, every load-bearing claim is CONFIRMED, and the context file is present. Limits: this is a saved copy, not a live read, and the account requirement and full terms are not in the snapshot.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "product",
           "identity": "NoteSync docs 'How NoteSync works' (https://notesync.example.test/docs/how-it-works), free under 20 users, snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "free for teams under 20", "evidence": "snapshot: 'free for teams under 20'; meta.json price 'free under 20 users'",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "free for us", "evidence": "team size not in context file; pricing at 20+ users not stated",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "does semantic search", "evidence": "snapshot: embeds notes with their models, stores vectors, searches run on their servers",
     "status": "CONFIRMED"},
    {"claim": "connecting a folder uploads note contents to NoteSync's cloud", "evidence": "snapshot: 'uploads each note to our cloud' and stores 'a copy of the text'; meta.json data_leaves_machine true",
     "status": "CONFIRMED"},
    {"claim": "data is retained after disconnecting", "evidence": "snapshot: 'retained for 90 days after you disconnect'",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)",
          "overlap": "SQLite with sqlite-vec already provides semantic search",
          "burden": "new external service and connected folder; account likely but not stated",
          "risks": ["full note text uploaded to a new third party", "90-day retention after disconnect",
                    "lock-in to their embedding models and servers", "no license or terms shown in snapshot"],
          "cost": {"price": "free under 20 users", "tier": "free team tier", "limits": "under 20 users; pricing above not stated",
                   "terms": "data retained 90 days after disconnect; other terms not in snapshot",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether internal notes may be sent to NoteSync; recommendation is to decline and keep sqlite-vec for goal 3",
                  "owner": "operator", "done_when": "the decision is recorded", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```