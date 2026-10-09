# Redteam report: tenant-isolated RAG (rag.py, store.py, test_rag.py)

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. Nothing was executed. Every trace below was done by hand on the supplied code.

**VERDICT: SHIP WITH FIXES.** Per-tenant filtering and per-tenant delete both hold when traced by hand. One real weakness remains: concurrent deletes and uploads can undo a deletion or silently drop an upload. Two unsupplied inputs also need answers before customer files are loaded: where `tenant` comes from, and whether `store.py` is the production backend.

**CONFIDENCE: medium.** It is limited by three things: no tools (tests were not run and mutations were not executed), a same-context review, and missing inputs. The caller that supplies `tenant` was not given, and neither were the deployment model or the real store.

**INPUTS LEDGER**
- **Seen:**
  - the original request (verbatim)
  - context.md
  - rag.py, store.py, test_rag.py
- **Not seen, and whether each gap matters:**
  - **The API or route layer that calls `answer`, `ingest` and `delete`, and how it derives `tenant`.** Matters a lot. Isolation is only as good as this value.
  - **Deployment model: process count, threading, restarts.** Matters. It decides the impact of finding F1 and of suspicions S2 and S3.
  - **The `llm` and `embed` implementations and their retention.** Matters for the deletion promise.
  - **Raw upload storage, if any.** Matters for deletion.
  - **Actual test run output.** The "3 tests pass" claim is unverified.

**COVERAGE**
- **Checked:**
  - rag.py: `ingest`, `delete`, `answer`
  - store.py: `Store.add`, `Store.query`
  - test_rag.py: all 3 tests, traced by hand, including a hand-mutation check of each test
- **Not checked:**
  - the caller or auth layer, the llm and embed clients, deployment config and upload storage (none supplied)
  - runtime behaviour (no tools)

**SEATS AND GATE:** The sensitivity gate applies. Production use involves confidential customer files. The code supplied contains no personal data, but the work governs confidential data. Cross-vendor seats: not used (no tools, and the user did not ask for them). Reviewer: local same-context only.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | rag.py:13 (`index.rows[:] = [r for r in index.rows if ...]`) | `delete` is a read-copy-write of the whole shared list with no lock. Every tenant shares that list. | **Condition:** the server handles requests on multiple threads. Two deletes run at once (acme deletes a1, globex deletes g1). Each builds its comprehension from the same snapshot. The second slice-assignment writes back the row the first removed, so acme's "deleted" document is retrievable again. A separate case: an `ingest` append that lands between one delete's comprehension and its assignment is discarded, so a customer's upload silently disappears. | **Fix:** guard `add`, `delete` and `query` with one `threading.Lock` in `Store`, or delete in place under the lock. **Reproduction (deterministic, no threads needed):** `snap = list(rag.index.rows)`; then `a = [r for r in snap if r["id"] != "a1"]` and `b = [r for r in snap if r["id"] != "g1"]`; then `rag.index.rows[:] = a`; then `rag.index.rows[:] = b`. Expected: a1 is gone. Observed: `answer(..., "acme", ...)` contains "acme salary bands". A real regression test would run two threads with a `threading.Barrier` inside a patched comprehension. | a Y, b N, c Y, d N (depends on threading, which was not supplied) |
| F2 | Low | CONFIRMED | B | store.py:13 (`where or {}`), rag.py:8, rag.py:17 | Isolation is opt-in at every call site. `Store.query` with no `where` returns every tenant's rows. Neither `ingest` nor `answer` validates `tenant`. A `None` or empty tenant is accepted, and `where={"tenant": None}` matches any row stored with `tenant=None`. | **Condition:** a future call site, such as a "search" endpoint or a debug helper, calls `index.query(vec)` without `where`. It returns other customers' text. A bug that passes `tenant=None` to both ingest and answer creates a shared "null tenant" pool. Today's single call site is correct. | **Fix:** make `tenant` a required positional parameter of `Store.query`, or a per-tenant view, and raise on a falsy tenant in `ingest`, `answer` and `delete`. **Test:** `index.query([1,0])` without a tenant raises, and `rag.answer(..., None, ...)` raises. | a Y, b Y, c N, d N |

## NEEDS VALIDATION (no severity)
- **S1: tenant provenance.** Does the caller derive `tenant` from the authenticated session or token, or from a request field the customer controls? If it comes from the request, any customer can read any other customer's documents, and that would be Critical.
- **S2: store.py is the production backend.** `Store.rows` is a Python list that is never persisted. Is this the store that will hold customer documents? If yes, every restart loses all uploads (data loss, Critical). With more than one worker process, each worker has its own index. A `delete` routed to one worker leaves the document live in another worker that holds a copy. If store.py is only a stand-in for a real vector database, the isolation and delete logic must be re-reviewed against that database's filter and delete semantics, including soft-delete, compaction and replicas.
- **S3: completeness of deletion.** `delete`'s docstring is true for the in-memory index. Is the document also kept in raw upload storage, an embedding cache, logs of prompts sent to `llm` (which contain document text), or provider-side retention? Settled by an inventory of every place uploaded text or vectors are written.
- **S4: "3 tests pass".** I traced by hand that all three would pass. The run itself was not seen.

## REFUTED
- **R1: "The tenant filter can leak another tenant's rows."** `Store.query` keeps only rows where `r.get("tenant") == tenant` (store.py:13). `answer` always passes `where={"tenant": tenant}` (rag.py:17). Traced with the test data: the acme query returns only the a1 row.
- **R2: "delete removes another tenant's document with the same id."** The predicate is `r["id"] == doc_id and r["tenant"] == tenant` (rag.py:13). Traced: globex's a1 survives acme's delete.
- **R3: "delete leaves the vector behind while removing the text."** Text and vector live in the same row dict (store.py:10), so removing the row removes both.
- **R4: "The tests can't fail (no positive control)."** This was a hand mutation, not a run. Remove `where` → test 1 sees "globex" and fails. Drop the tenant clause in delete → test 2 loses globex's a1 and fails. Make delete a no-op → test 3 sees "acme salary" and fails. Each test guards its property.

## WHAT HOLDS UP
- The single retrieval path always filters by tenant before ranking, so cross-tenant text never reaches the prompt.
- Delete is scoped to (tenant, id) and removes text and vector together.
- The three tests assert real behaviour, and each one would go red under the mutation that breaks its property.
- Prompt injection inside a document can only affect the answers of the tenant who uploaded it. There is no cross-tenant path.

## UNVERIFIED CLAIMS
- **"3 tests in test_rag.py pass":** run `python -m unittest test_rag -v`.
- **rag.py's docstring, "every query is filtered by tenant":** true for this file. It must be confirmed for every caller of `index.query`. Grep for `.query(` across the repo, with `rag.py:17` as the positive control.
- **delete's docstring, "removes … at once":** true in-process only. It needs S2 and S3 resolved.

## QUESTIONS FOR THE AUTHOR
1. Where does `tenant` come from in the request handler: auth claims or request input?
2. Is `store.Store` what production uses? How many processes and threads serve requests?
3. Where else is uploaded text or are vectors stored or logged, including the LLM provider?

## DECISION-MAKER SUMMARY
The isolation logic in the supplied code is correct and tested. Add a lock to the store (F1) and require a tenant on every query (F2). Before loading customer files, get answers to S1 and S2. If the tenant comes from the request body, or this in-memory store is the production store, proceeding would risk cross-customer exposure or lost and undeleted documents.

## OWNER SUMMARY
The code correctly keeps each customer's answers limited to their own documents, and its tests check this properly. There is a small risk that two deletions at the same moment could bring a deleted file back, which a simple fix prevents. Before real customer files go in, the team should confirm how the system knows which customer is asking and where the documents are actually stored.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "API/route layer that supplies tenant", "status": "not_seen", "matters": true},
    {"item": "deployment model (processes, threads, restarts)", "status": "not_seen", "matters": true},
    {"item": "llm and embed implementations and retention", "status": "not_seen", "matters": true},
    {"item": "raw upload storage", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "rag.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_rag.py", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Production system holds confidential customer documents; no external or cross-vendor seats."},
  "coverage": {
    "checked": [
      {"unit": "rag.py", "kind": "file"},
      {"unit": "rag.py:ingest", "kind": "function"},
      {"unit": "rag.py:delete", "kind": "function"},
      {"unit": "rag.py:answer", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "store.py:Store.add", "kind": "function"},
      {"unit": "store.py:Store.query", "kind": "function"},
      {"unit": "test_rag.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "caller/auth layer deriving tenant", "reason": "not supplied"},
      {"unit": "llm/embed clients", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "runtime test execution", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:13",
     "scenario": "Under a threaded server, two concurrent deletes each rebuild the shared row list from the same snapshot; the later slice-assignment restores the row the earlier one removed, so a deleted document is retrievable again; an ingest landing between comprehension and assignment is silently dropped.",
     "fix": "Guard Store add/delete/query with a single threading.Lock (or delete in place under the lock).",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "snap=list(rag.index.rows); a=[r for r in snap if r['id']!='a1']; b=[r for r in snap if r['id']!='g1']; rag.index.rows[:]=a; rag.index.rows[:]=b; expect a1 gone, observe 'acme salary bands' in answer(...,'acme',...)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:13; rag.py:8; rag.py:17",
     "scenario": "A future call to index.query(vec) without where returns every tenant's rows; tenant=None is accepted at ingest and answer, creating a shared null-tenant pool.",
     "fix": "Make tenant a required argument of Store.query and reject falsy tenant in ingest/answer/delete.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call rag.index.query([1,0]) with no where; expect an error, observe rows from both acme and globex."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rag.py:16 (tenant parameter)",
     "suspicion": "Tenant may be taken from customer-controlled request input.",
     "unresolved_fact": "Whether the caller derives tenant from authenticated identity."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:1-6",
     "suspicion": "In-memory per-process store loses all uploads on restart and leaves deleted docs live in other workers.",
     "unresolved_fact": "Whether store.Store is the production backend and how many processes serve requests."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rag.py:12",
     "suspicion": "Deletion may not cover raw uploads, caches, logs or LLM-provider retention of prompts containing document text.",
     "unresolved_fact": "Inventory of every place uploaded text or vectors are written."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_rag.py",
     "suspicion": "Claim that 3 tests pass was not observed.",
     "unresolved_fact": "Output of python -m unittest test_rag -v."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Tenant filter leaks other tenants' rows.", "evidence": "store.py:13 keeps only rows with r.get('tenant') == tenant; rag.py:17 always passes it."},
    {"id": "R2", "candidate": "delete removes another tenant's same-id document.", "evidence": "rag.py:13 requires both id and tenant to match."},
    {"id": "R3", "candidate": "delete leaves vector behind.", "evidence": "Text and vector are in one row dict (store.py:10); removing the row removes both."},
    {"id": "R4", "candidate": "Tests cannot fail.", "evidence": "Hand-mutation: removing where, the tenant clause in delete, or delete itself makes tests 1, 2, 3 fail respectively."}
  ]
}
```