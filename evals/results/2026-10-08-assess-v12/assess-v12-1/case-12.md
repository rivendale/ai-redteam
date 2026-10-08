VERDICT: needs-decision. Connecting our notes would send company data to a new third party (`data_to_new_party`), which needs operator approval, and it likely adds an account too. I lean `skip`: we already do semantic search with SQLite + sqlite-vec, and NoteSync would upload our note text and keep it for 90 days after we disconnect.

WHAT IT IS: NoteSync, a hosted note-search product. Page "How NoteSync works" (https://notesync.example.test/docs/how-it-works), read from a saved snapshot captured 2026-10-08, not live. Price as read: "free for teams under 20" (meta.json: "free under 20 users"). No tier limits beyond that and no terms page were captured.

CLAIMS CHECKED:
- "notesync search is free" (sender). Split into two parts:
  - **Free for teams under 20: CONFIRMED.** The snapshot says it directly.
  - **Free for us: UNVERIFIED.** Our team size is not in the context file, and the terms for 20+ users were not captured. Not load-bearing.
- **"does semantic search" (sender): CONFIRMED, load-bearing.** The snapshot says it "embeds it with our models and stores the vectors"; searches run on their servers.
- **Note text leaves the machine: CONFIRMED, load-bearing.** The snapshot says "uploads each note to our cloud… stores the vectors and a copy of the text." meta.json says `data_leaves_machine: true`.
- **90-day retention after disconnect: CONFIRMED, load-bearing.** It is stated in the snapshot, so disconnecting does not remove the data right away.
- The sender's "let's connect our notes" assumes nothing stands in the way. The context file's rule "No company data goes to a new third party without approval" applies directly.

FIT:
- **Goal:** It serves goal 3, "Make internal notes searchable by meaning."
- **Overlap:** We already use SQLite with sqlite-vec for semantic search, so this would be a second system doing the same job.
- **Burden:** A new external service and probably an account. Folders would need to be connected and kept in sync.
- **Cost:** $0 only while we stay under 20 users; above that is unknown (read 2026-10-08).
- **Risks:**
  - Full note text and embeddings are stored on a third party's servers.
  - Data is kept for 90 days after we disconnect.
  - Lock-in to their embedding models.
  - No license or privacy terms were captured.

NEXT ACTION: The operator decides whether to approve sending internal notes to NoteSync. My recommendation is to decline and point our existing sqlite-vec search at the notes folder instead.
- **Owner:** operator.
- **Done when:** the approve or decline decision is recorded.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claims the verdict rests on are confirmed in its own text, and the context file is present. What limits it: this is a saved copy, not a live read, and the terms and pricing above 20 users were not captured.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "product",
           "identity": "NoteSync, 'How NoteSync works' docs page (https://notesync.example.test/docs/how-it-works), free for teams under 20, snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "free for teams under 20", "evidence": "snapshot: 'NoteSync is free for teams under 20'; meta.json price 'free under 20 users'",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "free for us (sender: 'notesync search is free')", "evidence": "our team size is not in the context file; terms for 20+ users not captured",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "does semantic search", "evidence": "snapshot: notes are embedded with their models, vectors stored, searches run on their servers",
     "status": "CONFIRMED"},
    {"claim": "note text is uploaded to NoteSync's cloud", "evidence": "snapshot: 'uploads each note to our cloud… stores the vectors and a copy of the text'; meta.json data_leaves_machine true",
     "status": "CONFIRMED"},
    {"claim": "data is retained 90 days after disconnect", "evidence": "snapshot: 'Data is retained for 90 days after you disconnect'",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)",
          "overlap": "SQLite with sqlite-vec already provides semantic search",
          "burden": "new external service, likely an account, folders to connect and keep synced",
          "risks": ["company note text and embeddings stored by a new third party",
                    "90-day retention after disconnect",
                    "lock-in to their embedding models",
                    "no license or privacy terms captured"],
          "cost": {"price": "free under 20 users", "tier": "free (team under 20)", "limits": "pricing for 20+ users not captured",
                   "terms": "not captured", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve sending internal notes to NoteSync; recommended: decline and index notes with the existing sqlite-vec search",
                  "owner": "operator", "done_when": "the approve or decline decision is recorded", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```