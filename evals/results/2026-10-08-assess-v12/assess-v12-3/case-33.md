VERDICT: try. The post tunes sqlite-vec, which we already use for goal 3, and its three changes are cheap to test on a copy of our index. Its speedups come from one machine and say nothing about search quality, so measure both before keeping any change.

WHAT IT IS: Blog post "Tuning sqlite-vec for notes search", posted 2026-09-08, at https://posts.example.test/sqlite-vec-tuning. I read the saved snapshot captured 2026-10-08, not the live page. No author is named. Free to read, no account needed.

CLAIMS CHECKED:
- **"Three changes took a 50,000-note index from 480 ms to 70 ms per query."**
  - Evidence: the post's own timing table, which reports median query time on one machine.
  - Not given: hardware, vector dimension, k, query count or number of runs.
  - Status: **PROBABLE** as a result on that machine. It may not transfer to our index or hardware. The verdict rests on this.
- **Each change's contribution (8192 page size: 480→410 ms; metadata pre-filter: →150 ms; int8 vectors: →70 ms).**
  - Evidence: the same table, but the changes are stacked one on another, never measured alone.
  - Each step's gain depends on the steps before it. The pre-filter gain also depends on how selective the filter is, which the post does not report.
  - Status: **PROBABLE**. Not load-bearing.
- **Speed is the whole story (implied: nothing is lost).**
  - The post measures only latency. It gives no recall or accuracy figures for int8 quantization or for pre-filtering, both of which can change which notes come back.
  - Status: **UNVERIFIED**. Nothing in the item settles it either way, and it is what would change the conclusion. The verdict rests on it, which is why this is a try and not an adopt.
- **"The post gives the SQL and the settings."**
  - The captured content contains no SQL or settings beyond the three named changes. The capture may be incomplete, so I am not calling this false.
  - Status: **UNVERIFIED**. Not load-bearing, because the three changes can be applied from the sqlite-vec docs.

FIT:
- **Goal:** goal 3, "make internal notes searchable by meaning". The context file does not say our searches are slow, so the speed gain may not matter much to us.
- **Overlap:** none. The post tunes a tool we already use; it adds nothing new.
- **Burden:** one rebuild of the index on a copy. A page-size change only takes effect after a `VACUUM` or a fresh rebuild. Quantized vectors also have to be regenerated whenever the index is rebuilt.
- **Cost:** free. No account, no subscription.
- **Risks:**
  - int8 quantization and pre-filtering can lower search quality.
  - No data leaves the machine, and there is no license issue.
  - Single-source benchmark from an unnamed author.

NEXT ACTION: On a copy of our sqlite-vec notes index, apply the three changes one at a time. For each, record median query latency and top-10 overlap against the current index on a fixed set of about 50 real queries.
- **Owner:** operator, or whoever maintains notes search.
- **Done when:** latency and top-10 overlap are recorded for each change.
- **Stop condition:** drop any change that cuts top-10 overlap below about 90%. Stop the whole trial if baseline latency is already well under 100 ms, since there is little to gain.
- **Hand-off:** harvest, to capture the settings from the post.

CONFIDENCE: medium. The post is resolved, but only from a saved snapshot. The claim the verdict rests on about search quality is UNVERIFIED, the benchmark is from one machine, and the captured content lacks the SQL it promises.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Tuning sqlite-vec for notes search\", posts.example.test, posted 2026-09-08, author not named; read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "three changes took a 50,000-note index from 480 ms to 70 ms median per query",
     "evidence": "the post's own timing table: medians on one machine, no hardware, dimension, k or run count given",
     "status": "PROBABLE"},
    {"claim": "page size 8192, metadata pre-filter and int8 vectors each contribute the step shown (410, 150, 70 ms)",
     "evidence": "the same table; changes applied cumulatively, never alone, and filter selectivity not given",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "the speedups come without loss of search quality (implied)",
     "evidence": "only latency is measured; no recall or accuracy figures for int8 or pre-filtering",
     "status": "UNVERIFIED"},
    {"claim": "the post gives the SQL and the settings",
     "evidence": "the captured content contains no SQL or settings beyond naming the three changes; the capture may be incomplete",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "make internal notes searchable by meaning (goal 3); the context does not say search latency is a problem",
          "overlap": "none: it tunes sqlite-vec, which is already in use, rather than adding a tool",
          "burden": "one index rebuild on a copy; page size needs VACUUM or a rebuild; int8 vectors must be regenerated on rebuild",
          "risks": ["int8 quantization and pre-filtering may lower recall", "single-machine benchmark from an unnamed author", "no data leaves the machine, no license issue"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "free to read, no account",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On a copy of our sqlite-vec notes index, apply the three changes one at a time and record median latency and top-10 overlap with the current index on a fixed set of about 50 real queries",
                  "owner": "operator",
                  "done_when": "latency and top-10 overlap are recorded for each change",
                  "stop_condition": "drop any change that cuts top-10 overlap below about 90%; stop the whole trial if baseline latency is already well under 100 ms",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```