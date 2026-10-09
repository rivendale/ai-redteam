# Redteam review: tenant-isolated document Q&A (rag.py, store.py, test_rag.py)

**VERDICT: REWORK (storage layer only).** The tenant filter and the tests are sound, but the store is an in-memory list. As written, every restart wipes all customers' documents, and nothing settles whether deletion and isolation still hold once deployed. Keep the filter design and the tests; replace the store and add the guards below before loading customer documents.

**CONFIDENCE: medium.**
- I had no tools, so nothing was run. Every trace below is by reading.
- I am a single reviewer. No subagent or second seat was available.
- The code that supplies `tenant` was not provided, and the isolation guarantee depends on it.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `rag.py`, `store.py`, `test_rag.py`.
- Not seen, and it matters:
  - The API or auth layer that calls `ingest`, `answer` and `delete` and decides `tenant`.
  - The deployment model: worker count, restarts, persistence.
  - Upload storage, the embedding and LLM providers, logs and backups. These are where copies of a "deleted" document could survive.
- Not seen, and it does not matter: the `llm` and `embed` implementations, for isolation purposes.

**COVERAGE**
- Checked:
  - `rag.py`: `ingest`, `delete`, `answer`.
  - `store.py`: `Store.add`, `Store.query`.
  - `test_rag.py`: all 3 tests, including a traced mutation check on each.
  - The claim "filtered by tenant inside the query".
  - The claim "deleting removes … at once".
  - The claim "3 tests pass".
- Not checked: the caller and auth layer, deployment, provider-side retention. None were supplied.

**SEATS AND GATE**
- Ran: same-session reviewer only.
- No subagent or cross-vendor seats were available because the session had no tools.
- Sensitivity gate: not sensitive. The work is code with placeholder strings.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | `store.py:1-6`, `rag.py:4` | The production index is a module-level Python list with no persistence. | Any restart, deploy or crash empties the index for every customer, and Q&A silently returns context-free answers until everything is re-ingested. With more than one worker process, each worker holds a different subset of documents. | Use a persistent store that filters on tenant on the server side, and make deletion a store operation. Repro: ingest a doc, restart the process, call `answer` and observe empty context. | a✔ b✔ c✘ (whether originals survive elsewhere is unknown) d✔ |
| F2 | Medium | PROBABLE | B | `rag.py:7-8`, `rag.py:16-17`, `store.py:14` | A tenant of `None` or `""` is accepted. Because `r.get("tenant") == None` matches rows stored with `tenant=None`, every falsy tenant shares one bucket. | An upstream path yields `tenant=None` for two different customers (missing claim, failed lookup). Customer B then retrieves customer A's documents. | Raise in `ingest`, `answer` and `delete` when `tenant` is falsy or not a `str`. Repro test: `ingest(None,"x",[1,0],"secret")`, then `answer(..., None, ...)`; expect a raise, observe "secret" in the prompt. | a✔ b✘ c✔ d✘ |
| F3 | Medium | PROBABLE | B | `rag.py:13` | `delete` rebuilds the list and then slice-assigns it, which is not atomic against a concurrent `ingest`. | In a threaded server, an `ingest` that appends after the comprehension finishes but before `rows[:] =` is silently lost. The affected customer may be any tenant. | Guard `rows` with a lock in `add`, `delete` and `query`, or move to a store with transactional delete. Repro: two threads looping `ingest` and `delete` concurrently, then compare row counts. | a✔ b✘ c✔ d✘ |
| F4 | Low | CONFIRMED | B | `store.py:11`, `store.py:14` | `Store.query(where=None)` returns every tenant's rows, so isolation depends on every caller remembering the filter. | A future endpoint (admin search, debug, reindex) calls `index.query(vec)` and mixes tenants. | Make `tenant` a required parameter of the store's query and fail if it is missing. Test: `query(v)` with no tenant raises. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED | B | `rag.py:11-13` | `delete` returns nothing and never reports whether anything was removed. | A deletion request with a mistyped `doc_id` "succeeds", so the customer is told their file is gone when it is not. | Return the removed count and fail loudly on 0. Test: `delete("acme","nope")` raises or returns 0. | a✔ b✔ c✘ d✘ |
| F6 | Low | PROBABLE | A/B | `rag.py:17-19` | There is no relevance threshold and no empty-context guard. Grounding rests only on a prompt instruction. | A tenant with no documents, or no relevant ones, gets an answer drawn from the model's general knowledge. That contradicts "only ever get answers from their own documents" on the strict reading. | When `hits` is empty or below a score floor, return "no answer in your documents" without calling the LLM. Test: query an empty tenant and assert the LLM is not called. | a✔ b✘ c✘ d✔ |

## NEEDS VALIDATION

- **Where `tenant` comes from.** If it is taken from a request parameter or body rather than an authenticated session, any customer can read any other customer's documents. This settles whether isolation holds at all, and it lies outside the supplied code.
- **Copies outside the index.** Do uploaded originals, embedding-API logs, LLM-provider logs, caches and backups keep a document after `delete`? This settles whether the deletion promise to customers is true.
- **Process model.** If there are multiple workers, a `delete` reaches only one process's list, so the document can stay retrievable in the worker that ingested it. The worker and replica count in production settles this.
- **Chunking.** If real ingestion splits a document into several rows with distinct ids such as `a1#0`, then `delete(tenant, "a1")` removes none of them. The ingestion pipeline's id scheme settles this.

## REFUTED

- **"The tests are written to pass and prove nothing."** Traced mutations show each test would go red:
  - Removing the `where` filter makes test 1 fail, because both docs share the vector `[1,0]` and "globex" enters the prompt.
  - Making `delete` ignore the tenant makes test 2 fail, because globex's `a1` would be removed.
  - Making `delete` a no-op makes test 3 fail.
- **"The type or case of the tenant can leak across tenants."** Strict `==` fails closed: `1 != "1"` and `"Acme" != "acme"`. That gives no cross-tenant match, only possible self-denial.

## WHAT HOLDS UP

- Retrieval filters on tenant before ranking (`store.py:14`). Top-k therefore never sees another tenant's rows, so the filter cannot be bypassed by score.
- `delete` scopes on both `id` and `tenant`, so ids reused across tenants are handled correctly.
- Prompt injection inside a document can affect only its own tenant's answers, because other tenants' text never enters the prompt.
- All three tests assert real behaviour and would fail under the matching mutation.

## UNVERIFIED CLAIMS

- **"3 tests in test_rag.py pass."** Not run. By reading, they would pass on this code. Confirm with `python -m unittest test_rag`.
- **"Deleting removes … from the index at once."** This is true for the single in-process list. It is unverified for any real deployment (see NEEDS VALIDATION).

## QUESTIONS FOR THE AUTHOR

1. Is `store.py` what runs in production, or a stand-in for a real vector database?
2. Where does `tenant` come from on each call, and can a client influence it?
3. Where else does an uploaded document's text exist (originals, provider logs, backups), and what does deletion do there?

## DECISION-MAKER SUMMARY

The isolation logic is correct, but the storage is a toy. As written, a restart loses everything, and nothing shows that deletion or tenant identity hold once deployed. Before loading customer files:
- replace the store,
- reject empty tenants,
- show where `tenant` is authenticated,
- document every place a deleted file still lives.

Proceeding now risks lost data and, if the tenant source is client-controlled, cross-customer exposure.

## OWNER SUMMARY

The part that keeps one customer's documents away from another's is built correctly and properly tested. However, the documents are kept only in temporary memory, so they would vanish on any restart. It is also not yet shown that deletion requests are fully honoured or that the system always knows which customer is asking. Those points need fixing and checking before real customer files are uploaded.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "rag.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_rag.py", "status": "seen", "matters": true},
    {"item": "caller/auth layer supplying tenant", "status": "not_seen", "matters": true},
    {"item": "deployment model (workers, restarts, persistence)", "status": "not_seen", "matters": true},
    {"item": "upload storage, embedding/LLM provider retention, backups", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code with placeholder strings; no real customer data."},
  "coverage": {
    "checked": [
      {"unit": "rag.py", "kind": "file"},
      {"unit": "rag.py:ingest", "kind": "function"},
      {"unit": "rag.py:delete", "kind": "function"},
      {"unit": "rag.py:answer", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "store.py:Store.add", "kind": "function"},
      {"unit": "store.py:Store.query", "kind": "function"},
      {"unit": "test_rag.py", "kind": "file"},
      {"unit": "every query is filtered by tenant inside the query", "kind": "claim"},
      {"unit": "deleting removes text and vector from the index at once", "kind": "claim"},
      {"unit": "3 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "caller/auth layer", "reason": "not supplied"},
      {"unit": "deployment configuration", "reason": "not supplied"},
      {"unit": "provider-side and backup retention", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:1-6, rag.py:4",
     "scenario": "Any restart, deploy or crash empties the in-memory index for every customer; with multiple worker processes each worker holds a different subset of documents.",
     "fix": "Use a persistent store with server-side tenant filtering and store-level delete.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Ingest a document, restart the process, call answer for that tenant; expect the document in context, observe empty context."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:7-8, rag.py:16-17, store.py:14",
     "scenario": "An upstream path passes tenant=None or \"\" for two different customers; both share one bucket and one retrieves the other's documents.",
     "fix": "Reject falsy or non-str tenant in ingest, answer and delete.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "ingest(None,'x',[1,0],'secret'); answer(llm, embed, None, 'q'); expect raise, observe 'secret' in the prompt."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:13",
     "scenario": "In a threaded server an ingest appending between the list comprehension and the slice assignment is silently lost.",
     "fix": "Lock rows in add, delete and query, or use a store with transactional delete.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Run concurrent threads looping ingest and delete; compare final row count with the expected count."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:11, store.py:14",
     "scenario": "A future caller invokes index.query(vec) without where and receives every tenant's rows.",
     "fix": "Make tenant a required argument of the store query and fail when it is missing.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "index.query([1,0]) after ingesting two tenants returns both."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:11-13",
     "scenario": "A deletion request with a wrong doc_id silently succeeds and the customer is told the file is gone.",
     "fix": "Return the removed count and fail on zero.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "delete('acme','nope') returns None with no error; expect an error or 0."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "A",
     "location": "rag.py:17-19",
     "scenario": "A tenant with no or no relevant documents gets an answer from the model's general knowledge instead of their documents.",
     "fix": "If hits are empty or below a score floor, return 'no answer in your documents' without calling the LLM.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Query a tenant with no rows; assert the LLM is not called; observe it is called with empty context."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "caller of rag.answer/ingest/delete",
     "suspicion": "tenant may be client-controlled, allowing any customer to read any other's documents.",
     "unresolved_fact": "Whether tenant is derived from an authenticated session rather than request input."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "rag.py:11-13",
     "suspicion": "Deleted documents may persist in upload storage, provider logs, caches or backups.",
     "unresolved_fact": "Retention and deletion behaviour of each system holding document text."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rag.py:4",
     "suspicion": "With multiple workers, delete reaches one process only, so the document stays retrievable elsewhere.",
     "unresolved_fact": "Production worker/replica count and process model."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rag.py:7-13",
     "suspicion": "Chunked documents with per-chunk ids are not removed by delete(tenant, doc_id).",
     "unresolved_fact": "The id scheme used by the real ingestion pipeline."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The tests would pass even if isolation or deletion were broken.",
     "evidence": "Traced: removing the where filter fails test 1 (shared vector [1,0]); a tenant-blind delete fails test 2; a no-op delete fails test 3."},
    {"id": "C2", "candidate": "Tenant type or case mismatch leaks across tenants.",
     "evidence": "Strict == at store.py:14 fails closed: 1 != '1', 'Acme' != 'acme'."}
  ]
}
```