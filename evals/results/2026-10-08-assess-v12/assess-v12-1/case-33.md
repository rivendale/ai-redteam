VERDICT: try. It tunes sqlite-vec, which we already use for goal 3, and the read is free. But the speedups come from one machine, and the int8 step's effect on search quality is not measured. Measure our own index before changing anything.

WHAT IT IS: Post "Tuning sqlite-vec for notes search", https://posts.example.test/sqlite-vec-tuning, posted 2026-09-08. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. No author is named in the snapshot. The post says it "gives the SQL and the settings", but the captured text contains only the summary and the timing table. Either the capture is partial or the post does not include them.

CLAIMS CHECKED:
- **"We already use sqlite-vec"** (sender). The context file lists "SQLite with sqlite-vec for semantic search". **CONFIRMED.**
- **The three changes took a 50,000-note index from 480 ms to 70 ms median per query.**
  - Evidence: a cumulative timing table (480 → 410 → 150 → 70 ms) and the post's own note "all on one machine".
  - Not given: hardware, vector dimension, query count, warm or cold cache, or variance.
  - The numbers are internally consistent, but this is a single run on one machine. **PROBABLE.** Load-bearing.
- **Each change's contribution:** page size 8192 saves about 70 ms, the metadata pre-filter about 260 ms, int8 about 80 ms.
  - The steps were measured cumulatively, in one order, so the per-change shares depend on that order.
  - The pre-filter gain also depends on how selective the filter is, and the post does not report that. **PROBABLE.** Not load-bearing.
- **Int8 quantization is a free win** (implied by presenting it as a plain speedup). The table measures latency only. Nothing measures recall or result quality, which quantization can lower. **UNVERIFIED.** Load-bearing for that step.
- **The post gives the SQL and the settings.** None appear in the snapshot. **UNVERIFIED.** Not load-bearing.
- **The same changes would speed up our search** (inference from the above). Nothing in the item covers our index size, hardware or filters, and the context file does not say our search is slow. **UNVERIFIED.** Load-bearing.

FIT:
- **Goal:** goal 3, make internal notes searchable by meaning. It improves the speed of a tool we already use for that.
- **Overlap:** none. It tunes our existing stack and does not replace anything.
- **Burden:**
  - page size: a one-time database rebuild
  - pre-filter: a query change
  - int8: re-indexing the vectors, plus checking result quality
- **Cost:** free; a public post, checked 2026-10-08 from the snapshot.
- **Risks:**
  - int8 may degrade search quality, and the post does not measure this.
  - Changing page size means rebuilding the database, so keep a backup.
  - Results from one machine may not transfer to ours.
  - The snapshot may be missing the SQL.
  - No data leaves the machine, and there is no license issue in reading a post.

NEXT ACTION:
- **Action:** The operator records the current median query time and a small recall check (say 20 known queries) on our notes index. Then they apply the post's three changes one at a time on a copy of the database, re-measuring both after each.
- **Done-when:** a table of latency and recall per change on our index, with a keep-or-drop call for each change.
- **Stop condition:** stop before changing anything if current latency is already acceptable. Drop int8 if recall falls noticeably on the known queries.
- **Hand-off:** `harvest`, to capture the post's SQL and settings from the live page, since the snapshot lacks them.

CONFIDENCE: medium. Limited by:
- reading a saved snapshot, not the live page
- benchmarks from one machine with no method details
- no measurement of int8's effect on quality
- the SQL is missing from the capture
- the context file does not say whether our search latency is a problem

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "\"Tuning sqlite-vec for notes search\", https://posts.example.test/sqlite-vec-tuning, posted 2026-09-08, author not named; read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "we already use sqlite-vec", "evidence": "context file: 'SQLite with sqlite-vec for semantic search'", "status": "CONFIRMED"},
    {"claim": "three changes took a 50,000-note index from 480 ms to 70 ms median per query", "evidence": "cumulative timing table, one machine, no hardware or method given", "status": "PROBABLE"},
    {"claim": "per-change gains: page size ~70 ms, pre-filter ~260 ms, int8 ~80 ms", "evidence": "cumulative table in one order; filter selectivity not given", "status": "PROBABLE", "load_bearing": false},
    {"claim": "int8 quantization is a free speedup", "evidence": "table measures latency only; no recall or quality measurement", "status": "UNVERIFIED"},
    {"claim": "the post gives the SQL and the settings", "evidence": "not present in the captured snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the same changes would speed up our search", "evidence": "nothing about our index size, hardware or filters; context does not say our search is slow", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3)", "overlap": "none; it tunes sqlite-vec, already in use",
          "burden": "one database rebuild for page size, a query change for the pre-filter, re-indexing and a recall check for int8",
          "risks": ["int8 may reduce recall; not measured", "page-size change needs a rebuild; back up first", "single-machine benchmark may not transfer", "snapshot lacks the SQL"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "reading only",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Baseline median latency and a 20-query recall check on our notes index, then apply the three changes one at a time on a copy and re-measure both",
                  "owner": "operator", "done_when": "a per-change table of latency and recall on our index with a keep-or-drop call for each",
                  "stop_condition": "stop before changing anything if current latency is already acceptable; drop int8 if recall falls noticeably",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```