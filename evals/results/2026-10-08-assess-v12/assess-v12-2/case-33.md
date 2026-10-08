VERDICT: try. Yes, it is worth a read: it targets goal 3 (semantic search over notes) on the sqlite-vec we already run, and its three changes can be tested on our own index at no cost, but its speedup comes from one machine and says nothing about search quality after int8 quantization.

WHAT IT IS: Blog post "Tuning sqlite-vec for notes search," posted 2026-09-08 at https://posts.example.test/sqlite-vec-tuning, author not named in the snapshot. Assessed from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not a live read. The snapshot holds the summary and the timing table only. The SQL and settings the post says it gives are not in the captured text.

CLAIMS CHECKED:
- **"sqlite-vec, which we already use"** (sender's words). The context file lists "SQLite with sqlite-vec for semantic search." CONFIRMED. Not load-bearing.
- **Page size, a metadata pre-filter and int8 vectors took a 50,000-note index from 480 ms to 70 ms per query.** The evidence is a median-latency table, one row per change, with the changes stacked cumulatively, "all on one machine."
  - The numbers are internally consistent.
  - The post does not give hardware, embedding dimension, k, filter selectivity, run count or variance.
  - PROBABLE for their setup. Load-bearing.
- **Per-change contributions:** page size −70 ms, pre-filter −260 ms, int8 −80 ms. These come from the same table. Because the changes are stacked, the order affects each one's share. PROBABLE. Not load-bearing.
- **"The post gives the SQL and the settings."** These are not present in the snapshot, so nothing captured settles this. UNVERIFIED. Load-bearing, because the trial depends on having concrete settings.
- **Not measured: what int8 quantization does to result quality (recall).** The post measures speed only. A 70 ms query that returns worse notes may not be a win. This is a gap in the evidence, not a claim the post makes.
- **Inference that the speedup would carry over to our index.** The post offers no evidence for this. The size of the pre-filter gain depends on how selective our metadata filters are. UNVERIFIED. Not load-bearing; this is what the trial tests.

FIT:
- **Goal:** Goal 3, "make internal notes searchable by meaning."
- **Overlap:** None. These are tuning tips for the tool already in use, not a replacement for it.
- **Burden:** Reading the post, then a one-off benchmark on a copy of our index. Changing page size likely means rebuilding or VACUUMing the database. No new service or account.
- **Cost:** Free to read, checked 2026-10-08 from the snapshot.
- **Risks:**
  - int8 quantization may lower recall.
  - The page-size change needs a database rebuild.
  - The single-machine benchmark may not transfer to our setup.
  - Nothing to install, no data leaves the machine, and no license applies to ideas taken from a post.

NEXT ACTION:
- **Action:** Read the full post live to get the SQL and settings. Then apply the three changes one at a time to a copy of our notes index. Record median query latency and recall@10 against the current index on a fixed set of 20–50 real queries.
- **Owner:** Whoever maintains the notes search (operator to assign).
- **Done when:** There is a table of latency and recall for each change on our data, with a keep or drop decision for each change.
- **Stop condition:** Stop if the post's SQL/settings cannot be obtained, or if no change cuts median latency by at least 25% without dropping recall@10 by more than 2 points.
- **Hand-off:** `harvest`, to take the post's settings into our notes.

CONFIDENCE: medium. Limits:
- I worked from a saved snapshot that lacks the SQL and settings the post promises.
- The speed claim rests on one undocumented machine.
- Recall after int8 quantization is not measured.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "\"Tuning sqlite-vec for notes search\", posts.example.test, posted 2026-09-08, author not named; saved snapshot captured 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "we already use sqlite-vec (sender)", "evidence": "context file: 'SQLite with sqlite-vec for semantic search'", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "page size + metadata pre-filter + int8 vectors took a 50,000-note index from 480 ms to 70 ms median per query", "evidence": "one cumulative median-latency table, single machine; no hardware, dimension, k, filter selectivity or run count given", "status": "PROBABLE"},
    {"claim": "per-change gains: page size -70 ms, pre-filter -260 ms, int8 -80 ms", "evidence": "same table; changes stacked, so order affects attribution", "status": "PROBABLE", "load_bearing": false},
    {"claim": "the post gives the SQL and the settings", "evidence": "not present in the captured snapshot text", "status": "UNVERIFIED"},
    {"claim": "the speedup would carry over to our index", "evidence": "none; one machine, recall after int8 not measured, pre-filter gain depends on filter selectivity", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)", "overlap": "none; tunes sqlite-vec, which is already in use", "burden": "read the post, one-off benchmark on a copy of the index; page-size change needs a rebuild", "risks": ["int8 quantization may cut recall, which the post did not measure", "single-machine benchmark may not transfer", "nothing installed, no data leaves the machine"], "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "none relevant to borrowing ideas", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Read the full post live for its SQL and settings, then apply the three changes one at a time to a copy of our notes index and record median latency and recall@10 against the current index on 20-50 real queries", "owner": "notes-search maintainer (operator assigns)", "done_when": "a latency and recall table for each change on our data exists, with a keep or drop decision for each change", "stop_condition": "stop if the SQL/settings cannot be obtained, or if no change cuts median latency by at least 25% without dropping recall@10 by more than 2 points", "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```