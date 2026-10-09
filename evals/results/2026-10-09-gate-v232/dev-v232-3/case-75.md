**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools, no subagent and no other reviewers. Every result below comes from reading the three files by hand. Nothing was run.

VERDICT: **REWORK**. The tenant filter is correct within one process, but the index lives only in memory, so customer documents vanish on restart. The code that decides which tenant a request belongs to was not supplied, and the isolation guarantee depends entirely on it.

CONFIDENCE: **medium**. Limited by no tools (nothing executed), same-context review, and a missing caller/authentication layer that carries the whole guarantee.

INPUTS LEDGER:
- Seen: request.md, context.md, rag.py, store.py, test_rag.py.
- Not seen (matters):
  - The caller of `answer`/`ingest`/`delete`, which is where `tenant` comes from.
  - The `llm` and `embed` implementations and their providers' retention terms.
  - The deployment model (single or multiple processes).
- Not seen (matters less): any test-run output. "3 tests pass" is only asserted.

COVERAGE:
- Scope: whole work.
- Checked:
  - request.md, context.md
  - rag.py: module docstring, `ingest`, `delete`, `answer`
  - store.py: `Store.add`, `Store.query`
  - test_rag.py: all 3 tests, each traced against a hand mutation
  - Claims: the "filtered by tenant" and "removes … at once" docstrings, and "3 tests pass"
- Not checked:
  - The tenant-source caller (not_supplied).
  - The LLM and embedding services (not_supplied).
  - The raw bytes of the files, for hidden characters (no_tools).
  - The actual test run (no_tools).

SEATS AND GATE: Only one reviewer ran, the local single-context one. The work does not contain sensitive data itself (the test strings are synthetic), but production will hold confidential customer files. No cross-vendor seats were requested, and none were possible without tools.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED (traced) | B | rag.py:4, store.py:5-6 | The index is a module-level, in-memory list. There is no persistence, and each process gets its own copy. | In production a deploy or crash restarts the process, and every customer's indexed documents are gone; questions get empty context. With several workers, a document ingested on worker 1 is invisible to worker 2, and a delete on one worker leaves copies on the others. | Fix: use a persistent store shared by all workers, with tenant filtering enforced at query time. Repro: `ingest("acme","a1",[1,0],"x")`, start a fresh interpreter, `import rag`, observe `rag.index.rows == []`. | y/y/n/y |
| F2 | Medium | CONFIRMED (traced) | B | rag.py:17-19 | `llm` is called even when `hits` is empty. Nothing enforces "Answer from this context only". | A tenant with no documents (new, or all deleted) asks a question. The model gets an empty context and may answer from its general knowledge. The answer is not from the customer's documents, as the request requires. | Fix: if `not hits`, return a fixed "no matching documents" reply without calling `llm`. Repro: with no rows, call `answer(stub, lambda q:[1,0], "acme", "q")`. Expected: no LLM call. Observed: the stub is called with an empty context. | y/y/n/n |
| F3 | Medium | PROBABLE | B | rag.py:7-8, 16-17; store.py:14 | `tenant` is never validated. `None` or `""` is a valid tenant, and `r.get("tenant") == None` also matches rows that have no tenant key. | If the upstream tenant lookup fails and returns `None` for two customers, both customers' uploads go into one shared `None` bucket. Each customer can then retrieve the other's documents. | Fix: reject a falsy or non-string `tenant` in `ingest`, `delete` and `answer`. Repro: `ingest(None,"x",[1,0],"cust A secret")`, then `answer(stub, e, None, "?")`. Observed: the prompt contains "cust A secret". | y/n/y/n |
| F4 | Medium | CONFIRMED (traced) | B/R | rag.py:11-13 | `delete` returns `None` whether or not anything matched, and it writes no record of the deletion. | A customer asks for deletion and the caller passes a mistyped `doc_id`. Nothing is deleted, the caller cannot tell, and the customer is told the file is gone. No audit trail shows what was removed or when. | Fix: return the number of rows removed, raise an error on zero, and write an audit entry (tenant, doc_id, time, count). Repro: `delete("acme","typo")` returns `None`, the same as a successful delete. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | rag.py:7-8, store.py:8-9 | `ingest` appends without replacing an existing row with the same `(tenant, doc_id)`. | A customer re-uploads a corrected document. Both the old and new versions stay indexed, and answers can cite the outdated text. | Fix: upsert on `(tenant, doc_id)`. Repro: ingest "acme"/"a1" twice with different text, query "acme", and observe both texts in the prompt. | y/y/n/n |
| F6 | Low | CONFIRMED (traced) | B | store.py:11, 14 | `query(where=None)` returns rows from all tenants, so the filter fails open by default. | A future caller forgets `where` and leaks across tenants. Today the only caller (rag.py:17) passes it, so no boundary is crossed yet. | Fix: make tenant a required argument of `query`, or raise when `where` is missing. Repro: `index.query([1,0])` returns rows for both acme and globex. | y/y/n/n |
| F7 | Low | CONFIRMED (traced) | B | test_rag.py:23-27, 16-21 | The tests miss a delete that ignores `doc_id`, and they never cover a `None` tenant or empty hits. | A regression that makes `delete` wipe every document a tenant owns would still pass all three tests. | Fix: add a test with two acme documents, delete one, and assert the other survives. Repro: change rag.py:13 to `not r["tenant"] == tenant` and trace; tests 2 and 3 both still pass. | y/y/n/n |
| F8 | Low | CONFIRMED (traced) | B | store.py:12-13 | `zip` silently truncates vectors of different lengths. | After a change of embedding model, old and new vectors are compared on a prefix only. Ranking is silently wrong and no error is raised. | Fix: assert `len(a) == len(b)` in `dot`, and store the embedding-model ID per row. Repro: `query([1,0,0], ...)` against `[1,0]` rows raises no error. | y/y/n/n |

F1 sibling search: I looked for other module-level mutable state in rag.py and store.py, and found only `index`. It is not a security finding: it affects availability and deletion consistency, not the tenant boundary inside one process.

## Needs validation
- **S1 (tenant source):** The whole requirement depends on where `tenant` comes from. Unresolved fact: is it derived server-side from an authenticated session, or taken from the request (body, header, query string)? If it comes from the request, any user can name any tenant.
- **S2 (deletion completeness):** Document text is sent to `llm` in every prompt. Unresolved fact: the LLM provider's retention and logging terms. Deletion from the index does not cover provider-side copies, and the `delete` docstring ("at once") covers only the index.
- **S3 (lost update):** If `ingest` runs in another thread between the comprehension and the slice assignment at rag.py:13, the newly appended row may be dropped. Unresolved fact: is the store accessed by multiple threads?
- **S4 (tests):** Unresolved fact: the actual `python -m unittest test_rag` output. Unrun.
- **S5 (hidden characters):** Unresolved fact: a byte-level scan of the three files for zero-width or bidirectional characters. Not possible without tools.

## Refuted
- **Cross-tenant leakage through top_k ranking:** store.py:14 filters by tenant before the sort at :15, so other tenants' rows never compete for slots.
- **Delete leaving the vector behind:** text and vector live in one row dict, and rag.py:13 removes the whole row.
- **Delete crossing tenants on a shared doc_id:** the predicate at rag.py:13 requires both `id` and `tenant` to match. test_rag.py:16-21 covers this, and it would go red if `tenant` were dropped from the predicate (traced).
- **test_other_tenant passes vacuously:** both rows have vector `[1,0]` and top_k=3. Without `where`, "globex layoff plan" enters the prompt and :14 fails (traced).
- **Prompt injection crossing tenants:** retrieval is filtered before the prompt is built, and `llm` has no tools, so the question can only steer the model over the tenant's own context.

## What holds up
Within one process, isolation is correct. The filter is applied before ranking, delete is scoped to the tenant, and test 1 and test 2 genuinely guard those two properties.

## Unverified claims
- "3 tests pass": run the tests and paste the output.
- "Every query is filtered by tenant": true inside rag.py, but unproven end to end until the caller's tenant derivation is supplied (S1).
- "Deleting removes … at once": true for the in-process list only; see F1, S2 and S3.

## Questions for the author
1. Where does `tenant` come from in the HTTP or API layer, and can a client influence it?
2. What replaces `Store` in production, and does it enforce the tenant filter itself?
3. What retention terms apply at the LLM provider for prompt contents?

## Decision-maker summary
Do not load customer documents into this build. The tenant filter logic is sound, but the in-memory store (F1) loses data and breaks deletion across processes, and the tenant source (S1) is unreviewed. If you proceed anyway, expect lost uploads on every restart and deletions you cannot prove were done.

## Owner summary
The part that keeps each customer's documents separate works as intended, but the documents are held only in temporary memory and would be lost whenever the system restarts. We also have not yet seen the part that identifies which customer is asking, and that part is what actually keeps customers apart. Deletions leave no record and do not confirm that anything was removed, which matters for customers who ask us to delete files.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "rag.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_rag.py", "status": "seen", "matters": true},
    {"item": "caller that supplies tenant (API/auth layer)", "status": "not_seen", "matters": true},
    {"item": "llm and embed implementations and provider retention terms", "status": "not_seen", "matters": true},
    {"item": "deployment model (process count)", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains only synthetic test strings; production data will be confidential and must not go to external seats."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "rag.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_rag.py", "kind": "file"},
      {"unit": "rag.py:ingest", "kind": "function"},
      {"unit": "rag.py:delete", "kind": "function"},
      {"unit": "rag.py:answer", "kind": "function"},
      {"unit": "store.py:Store.add", "kind": "function"},
      {"unit": "store.py:Store.query", "kind": "function"},
      {"unit": "every query is filtered by tenant inside the query", "kind": "claim"},
      {"unit": "deleting removes text and vector at once", "kind": "claim"},
      {"unit": "3 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "tenant-source caller", "reason": "not_supplied"},
      {"unit": "llm/embed providers", "reason": "not_supplied"},
      {"unit": "byte-level hidden character scan", "reason": "no_tools"},
      {"unit": "actual test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:4, store.py:5-6",
     "scenario": "A process restart erases every customer's indexed documents; with multiple workers, ingests and deletes apply only to the worker that handled them, so deleted documents can remain retrievable elsewhere.",
     "fix": "Replace the module-level in-memory Store with a persistent store shared by all workers, with tenant filtering enforced at query time.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "ingest('acme','a1',[1,0],'x'); start a fresh interpreter; import rag; observe rag.index.rows == [] (expected the document to persist).",
     "security": false,
     "siblings_searched": {"searched": "module-level mutable state in rag.py and store.py", "found": "only rag.index"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:17-19",
     "scenario": "A tenant with no documents asks a question; the LLM receives empty context and may answer from general knowledge, not from the customer's documents.",
     "fix": "If hits is empty, return a fixed 'no matching documents' reply without calling llm.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With no rows, call answer(stub, lambda q:[1,0], 'acme', 'q'); expected no llm call, observed the stub is called with empty context."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:7-8,16-17; store.py:14",
     "scenario": "If the upstream tenant lookup returns None for two customers, their uploads share a None bucket and each retrieves the other's documents.",
     "fix": "Reject a falsy or non-string tenant in ingest, delete and answer.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "ingest(None,'x',[1,0],'cust A secret'); answer(stub, lambda q:[1,0], None, '?'); observe the prompt contains 'cust A secret'.",
     "security": true,
     "boundary": {"principal": "a customer whose tenant resolves to None or ''", "input": "the tenant argument", "control": "no tenant validation", "crossed": "customer to customer", "resource": "other customers' documents in the None bucket"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:11-13",
     "scenario": "A deletion request with a wrong doc_id deletes nothing, returns the same None as success, and leaves no audit record; the customer is told the file is gone.",
     "fix": "Return the count removed, raise an error on zero, and write an audit entry (tenant, doc_id, time, count).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "delete('acme','typo') returns None, indistinguishable from a successful delete; no record is written."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:7-8, store.py:8-9",
     "scenario": "Re-uploading a corrected document keeps the old version indexed, so answers can cite outdated text.",
     "fix": "Upsert on (tenant, doc_id).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ingest acme/a1 twice with different text; query acme; observe both texts in the prompt."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:11,14",
     "scenario": "A future caller that omits where gets every tenant's rows; the filter fails open by default.",
     "fix": "Make tenant a required argument of query, or raise when where is missing.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "index.query([1,0]) returns both acme and globex rows."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_rag.py:16-27",
     "scenario": "A regression making delete remove all of a tenant's documents passes all three tests.",
     "fix": "Add a test with two acme documents: delete one and assert the other survives. Add tests for a None tenant and for empty hits.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change rag.py:13 to drop the doc_id condition; tests 2 and 3 still pass (traced)."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:12-13",
     "scenario": "After an embedding-model change, vectors of different lengths are compared on a prefix only and ranking is silently wrong.",
     "fix": "Assert equal lengths in dot, and store the embedding-model ID per row.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "query([1,0,0]) against [1,0] rows raises no error."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "callers of rag.answer/ingest/delete",
     "suspicion": "tenant may be taken from client-controlled input.",
     "unresolved_fact": "Whether tenant is derived server-side from an authenticated session."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "rag.py:19",
     "suspicion": "Document text sent to the LLM provider may be retained after deletion.",
     "unresolved_fact": "The LLM provider's retention and logging terms."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rag.py:13",
     "suspicion": "Concurrent ingest during delete may be lost.",
     "unresolved_fact": "Whether the store is accessed from multiple threads."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_rag.py",
     "suspicion": "The '3 tests pass' claim is unverified.",
     "unresolved_fact": "The actual unittest run output."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "rag.py, store.py, test_rag.py",
     "suspicion": "Hidden characters were not scanned.",
     "unresolved_fact": "A byte-level scan for zero-width, bidirectional and tag characters."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Other tenants' rows leak via top_k ranking.", "evidence": "store.py:14 filters by tenant before the sort at :15."},
    {"id": "R2", "candidate": "Delete leaves the vector behind.", "evidence": "Text and vector are one row dict; rag.py:13 removes the whole row."},
    {"id": "R3", "candidate": "Delete crosses tenants on a shared doc_id.", "evidence": "The rag.py:13 predicate requires both id and tenant; test_rag.py:16-21 would fail without tenant (traced)."},
    {"id": "R4", "candidate": "test_other_tenant_is_never_retrieved passes vacuously.", "evidence": "Without where, 'globex layoff plan' enters the prompt and :14 fails (traced)."},
    {"id": "R5", "candidate": "Prompt injection crosses tenants.", "evidence": "Retrieval is filtered before the prompt is built; llm has no tools."}
  ]
}
```