# Redteam review: multi-tenant question answering (`rag.py`, `store.py`, `test_rag.py`)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent. Nothing was run. Every code path below was traced by reading only.

**VERDICT: REWORK.** The tenant filter and the tenant-scoped delete are correct, but the store keeps everything in one process's memory, and the system can answer with no documents at all. Neither is ready for confidential production uploads.

**CONFIDENCE: medium.** Limited by no tools (tests not run, no mutation run), same-context review, and missing inputs: the caller that supplies `tenant`, the deployment model, and the LLM and embedding providers.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, rag.py, store.py, test_rag.py | Seen | – |
| Caller or API layer that supplies `tenant` (authentication) | Not supplied | **Yes.** All isolation rests on it. |
| Deployment model (number of processes or workers, restarts) | Not supplied | **Yes**, for durability and delete. |
| LLM and embedding providers and their data retention | Not supplied | **Yes**, for the deletion promise. |
| Test run output ("3 tests pass") | Not seen | Moderately. The claim is unverified. |

**COVERAGE:**
- **Checked:** `rag.py` (`ingest`, `delete`, `answer`, module docstring), `store.py` (`Store.add`, `Store.query`), `test_rag.py` (all 3 tests, traced against mutations).
- **Not checked:** authentication and tenant derivation, deployment, provider retention, embedding generation at ingest (vectors arrive precomputed).

**SEATS AND GATE:** Local same-context reviewer only. No subagent or cross-vendor seats were available. Sensitivity gate: the work holds code and toy fixtures only, so it is not sensitive.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | `store.py:1-6`, `rag.py:4` | The index is a module-level, in-memory Python list. It is not durable and not shared between processes. | Customers upload documents, then the process restarts (deploy, crash, scale event). Every tenant's index is empty, and questions get answers from no documents (see F2). | Back the index with a durable store that filters on tenant metadata, and re-run the isolation and delete tests against it. Repro: ingest, restart the interpreter, query, and observe 0 hits. | a✓ b✓ c✗ (originals may exist elsewhere, unknown) d✓ |
| F2 | High | PROBABLE (code path CONFIRMED, model behaviour inferred) | A/B | `rag.py:17-19` | Nothing stops the call when retrieval finds nothing relevant. The LLM is called even with empty or irrelevant context. "Answer from this context only" is a soft prompt instruction, and the question text can override it. | A new tenant with zero documents, or a question unrelated to their files, still goes to the LLM, which answers from general knowledge. That breaks "only ever get answers from their own documents". | If `hits` is empty, or below a similarity threshold, return a fixed "no answer in your documents" and do not call `llm`. Test: tenant `"initech"` with no documents; assert `llm` is never called. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | B/R | `rag.py:12-14` | `delete` returns nothing. A wrong `doc_id` or wrong `tenant` gives the same result as a real delete. | A customer asks for deletion and support passes a mistyped id. The call "succeeds" and the customer is told the file is gone, but it is still retrievable. | Return the number of rows removed and raise or alert when it is 0. Repro: `rag.delete("acme", "nope")` returns `None`, the same as a real delete. | a✓ b✓ c✓ d✗ |
| F4 | Medium | PROBABLE | B | `rag.py:14` | `rows[:] = [...]` is a non-atomic read-modify-write with no lock. | If ingest and delete run on concurrent threads, an `append` that lands between building the list and the slice assignment is overwritten. The uploaded document is silently lost. | Add a lock around mutations, or delete through a store method that is atomic. Repro: thread A loops `delete` while thread B ingests N docs; count rows < N. | a✓ b✗ c✓ d✗ |
| F5 | Medium | CONFIRMED | B | `store.py:8-9`, `rag.py:7-8` | Re-ingesting the same `(tenant, doc_id)` appends a second row instead of replacing the first. | A customer re-uploads a corrected document. The old version stays retrievable and can fill the `top_k=3` slots. | Upsert on `(tenant, id)`. Repro: ingest `("acme","a1","v1")`, then `("acme","a1","v2")`; the query returns both texts. | a✓ b✓ c✗ d✓ |
| F6 | Low | CONFIRMED | B | `rag.py:14` | `delete` reaches into `index.rows` and bypasses the `Store` API. | When the store is replaced (needed for F1), `delete` is the piece most likely to be missed or ported wrong. | Add `Store.delete(where=...)` and call it from `rag.delete`. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1. Where `tenant` comes from.** `answer`, `ingest` and `delete` trust the `tenant` argument (`rag.py:7,12,17`).
  - **Settles it:** whether the API layer derives `tenant` from the authenticated session and never from a request field. If it takes it from the request, any customer can read any other customer's documents. That would be Critical.
- **S2. Missing or empty tenant.**
  - **The risk:** `store.py:13` uses `r.get(k) == v`, so `tenant=None` or `""` from an unauthenticated path would put many callers into one shared bucket.
  - **Settles it:** whether the caller can ever pass None or empty. Either way, the fix is to reject a falsy `tenant` in all three functions.
- **S3. Multi-worker deployment.** With more than one process, each worker holds its own index, so a delete in one worker leaves the document retrievable in the others.
  - **Settles it:** the deployment's process count.
- **S4. Deletion beyond the index.** Document text is sent to `llm` in prompts (`rag.py:19`), and probably to an embedding service at upload. The `delete` docstring ("removes ... at once") covers only the in-memory row.
  - **Settles it:** the providers' retention terms (zero retention or not).
- **S5. Test strength.** By trace, each test would fail under its matching mutation:
  - removing `where` would let `"globex layoff plan"` into the prompt;
  - dropping the tenant condition in `delete` would remove globex's `a1`;
  - a no-op `delete` would leave `"acme salary"` in the prompt.
  - **Settles it:** apply each mutation in a scratch copy and confirm red. "3 tests pass" is also unverified.

## Refuted

- **C1. Cross-tenant leak at retrieval.** Refuted: `store.py:13` filters rows by `where` before ranking, and `answer` always passes `{"tenant": tenant}` (`rag.py:18`).
- **C2. Delete by `doc_id` removes another tenant's document with the same id.** Refuted: the condition requires both `id` and `tenant` (`rag.py:14`), and test 2 covers it.
- **C3. A malicious document in tenant A exfiltrates tenant B's data through prompt injection.** Refuted: the prompt contains only tenant A's rows, so the LLM never receives B's data in this code.

## What holds up

- The tenant filter is applied before ranking, on every query.
- Delete is scoped to both tenant and id.
- The three tests target the right properties and, by trace, are not tautological.
- No cross-tenant data enters any prompt.

## Unverified claims

- **"3 tests pass."** Confirm by running `python -m unittest test_rag`.
- **"Deleting removes the tenant's document ... at once"** (`rag.py:13`). True only within one process's memory. Confirm against the deployment model (S3) and provider retention (S4).
- **"every query is filtered by tenant"** (`rag.py:1`). True in `rag.py`. It still depends on S1.

## Questions for the author

1. How is `tenant` derived? Is it from the authenticated session only?
2. How many processes serve this, and where is the index persisted?
3. What do the LLM and embedding providers retain from prompts and uploads?

## Decision-maker summary

The isolation logic is sound, but the storage is in memory and per process, and the model answers even when a customer has no matching documents. Do not load customer files until the store is durable, empty retrieval refuses to answer, deletes confirm what they removed, and S1 (the tenant comes from authentication) is confirmed. If you proceed now, the realistic risks are lost indexes after a restart, answers not grounded in the customer's files, and deletions reported as done that did not happen.

## Owner summary

The part that keeps each customer's documents separate from other customers' documents works correctly. However, the system currently stores everything in temporary memory that is wiped on restart, and it will still answer a question even when it found nothing in the customer's files. Fix these, and confirm how customers are identified, before any real customer documents are uploaded.

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
    {"item": "caller/API layer supplying tenant", "status": "not_seen", "matters": true},
    {"item": "deployment model (processes, restarts)", "status": "not_seen", "matters": true},
    {"item": "LLM and embedding provider retention terms", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code and toy fixtures only; no real customer data in the work."},
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
      {"unit": "authentication / tenant derivation", "reason": "not supplied"},
      {"unit": "deployment configuration", "reason": "not supplied"},
      {"unit": "LLM and embedding provider retention", "reason": "not supplied"},
      {"unit": "test execution and mutation runs", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:1-6, rag.py:4",
     "scenario": "Customers upload documents into the module-level in-memory index; the process restarts (deploy, crash, scaling) and every tenant's index is empty, so questions are answered from no documents.",
     "fix": "Back the index with a durable store supporting tenant metadata filtering; re-run the isolation and delete tests against it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Ingest a document, restart the interpreter, call answer for that tenant; observe zero hits, expect the document."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "rag.py:17-19",
     "scenario": "A tenant with no documents, or a question unrelated to their files, still triggers the LLM call with empty or irrelevant context; the model answers from general knowledge, violating 'only ever get answers from their own documents'.",
     "fix": "If hits are empty or below a similarity threshold, return a fixed no-answer response without calling the LLM.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Call answer(llm, embed, 'initech', 'q') with no initech documents; expect llm not called, observe it called with an empty context."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "rag.py:12-14",
     "scenario": "A deletion request with a mistyped doc_id or tenant removes nothing yet returns the same as a successful delete; the customer is told their file is gone while it remains retrievable.",
     "fix": "Return the count of removed rows and raise or alert when it is zero.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "rag.delete('acme', 'nope') returns None, identical to a real delete."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:14",
     "scenario": "With concurrent threads, an ingest append landing between the list comprehension and the slice assignment is overwritten and silently lost.",
     "fix": "Guard store mutations with a lock or use an atomic store-level delete.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Thread A loops delete on an unrelated id while thread B ingests N documents; observe fewer than N rows."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:8-9, rag.py:7-8",
     "scenario": "A customer re-uploads a corrected document under the same id; the old version stays retrievable alongside the new one.",
     "fix": "Upsert on (tenant, id) instead of appending.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Ingest ('acme','a1','v1') then ('acme','a1','v2'); query returns both texts."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:14",
     "scenario": "delete mutates index.rows directly, bypassing the Store API; when the store is replaced, deletion is the piece most likely to be ported incorrectly.",
     "fix": "Add Store.delete(where=...) and call it from rag.delete.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace Store with any class lacking a rows list; rag.delete fails while ingest and answer still work."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rag.py:7,12,17",
     "suspicion": "Isolation trusts the tenant argument; if it comes from a request field, any customer can read another's documents.",
     "unresolved_fact": "Whether the caller derives tenant solely from the authenticated session."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:13",
     "suspicion": "tenant=None or empty string would create a shared bucket across unauthenticated callers.",
     "unresolved_fact": "Whether any caller can pass a falsy tenant."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rag.py:4",
     "suspicion": "With multiple workers, each holds its own index, so a delete in one leaves the document retrievable in others.",
     "unresolved_fact": "Deployment process count."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "rag.py:13,19",
     "suspicion": "Document text sent to the LLM (and likely an embedding service) may be retained after deletion, contradicting the delete docstring.",
     "unresolved_fact": "Provider retention terms for prompts and embedding inputs."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "test_rag.py",
     "suspicion": "Tests are claimed to pass and, by trace, would fail under their mutations, but neither was run.",
     "unresolved_fact": "Results of running the suite and of each mutation (remove where filter, drop tenant condition in delete, no-op delete) in a scratch copy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Other tenants' documents can be retrieved.",
     "evidence": "store.py:13 filters by where before ranking and rag.py:18 always passes the tenant filter."},
    {"id": "C2", "candidate": "Deleting a doc_id removes another tenant's document with the same id.",
     "evidence": "rag.py:14 requires both id and tenant to match; test 2 covers this."},
    {"id": "C3", "candidate": "Prompt injection in one tenant's document exfiltrates another tenant's data.",
     "evidence": "The prompt contains only the querying tenant's rows; the LLM never receives other tenants' data."}
  ]
}
```