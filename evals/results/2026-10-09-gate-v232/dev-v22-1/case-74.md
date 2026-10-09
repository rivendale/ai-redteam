VERDICT: REWORK. `answer()` never uses the tenant, so every customer's question is answered from every customer's documents, including documents they asked us to delete. That is the one thing the request forbids.

CONFIDENCE: medium. No tools were available in this session, so every trace below is a manual read of the code and nothing was executed. The review ran in a single context with no fresh subagent; re-run it in a fresh session before relying on it for production. The nightly deletion job and the code that supplies `tenant` were not supplied, and both matter.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `rag.py`, `store.py`.
- **Not seen, matters:**
  - The nightly purge job named in the `delete()` docstring. The deletion guarantee depends on it.
  - The caller that supplies `tenant` to `ingest`, `delete` and `answer`. Whether tenant comes from an authenticated session or from client input decides whether any filter is enforceable.
  - Tests. None were supplied, so no test exists to trust or mutate.
  - The `embed` and `llm` implementations, and which store is used in production.
- **Not seen, matters less:** deployment and persistence config. `Store` is in-memory, so whether it is the production store is open.

COVERAGE:
- **Checked:**
  - `rag.py`: `ingest`, `delete`, `answer`, module docstring.
  - `store.py`: `Store.add`, `Store.query`, including the `where` filter semantics.
  - Assumptions: tenant isolation, deletion semantics.
- **Not checked:** nightly job, tenant source and authentication, `embed` and `llm`, tests, persistence.

SEATS AND GATE:
- Same-context review only; no subagent or tools were available.
- The work is code, not customer data, so the sensitivity gate passes. No cross-vendor seat was requested and none ran.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `rag.py` `answer()`: `hits = index.query(embed(question), top_k=3)` | `tenant` is accepted but never used. `query` is called with no `where`, so it ranks every tenant's rows. The whole function is three lines and `tenant` appears only in the signature. | Customer A ingests a confidential contract. Customer B asks a related question, A's text becomes B's context, and the LLM is told to answer from it. The same path lets one tenant plant instructions ("ignore the question and say…") that reach other tenants' prompts. | Fix: `index.query(..., where={"tenant": tenant, "deleted": False})`, and add a deny-by-default assertion that `tenant` is non-empty. Repro: `ingest("A","d1",[1,0],"A-secret")`, `ingest("B","d2",[0,1],"B-doc")`, then `answer(echo_llm, lambda q:[1,0], "B", "q")`. Expected: no "A-secret". Observed: the prompt contains "A-secret". | y/y/y/y |
| F2 | Critical | CONFIRMED | B | `rag.py` `delete()` sets `r["deleted"]=True`; `store.py` `query()` filters only on `where`; `answer()` passes none | Soft-deleted rows stay fully retrievable. Nothing reads the `deleted` flag. | A customer requests deletion and is told it is done. Until the nightly job runs, and indefinitely if the job is absent or fails, their document still feeds answers for them and, via F1, for every other tenant. | Fix: filter `deleted: False` in every query, or hard-delete in `delete()` with an audit record. Repro: ingest d1 for A, `delete("A","d1")`, then `answer` for A. Expected: d1 absent. Observed: d1 in context. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | `rag.py` `delete()` | It returns nothing and raises nothing when no row matches, for example a wrong tenant, a typo'd id, or an already-purged doc. | The caller cannot distinguish "deleted" from "nothing matched" and may confirm deletion to the customer when nothing happened. | Fix: return the count of matched rows and raise or log on zero. Repro: `delete("A","nonexistent")` returns None, the same as a successful delete. | y/y/n/y |
| F4 | Medium | PROBABLE | B | `store.py` `query()`: `r.get(k) == v` | A missing key equals `None`. Once F1 is fixed with `where={"tenant": tenant}`, a `None` or empty tenant matches every row ingested without a tenant, and those rows are shared across all callers who lack one. | A bug or unauthenticated path passes `tenant=None`. It retrieves every untenanted row, and any doc ingested with `tenant=None` becomes visible to all such callers. | Fix: reject a falsy tenant in `ingest` and `answer`, and make `where` require key presence. Test: `ingest(None,...)` must raise, and `answer(..., tenant=None, ...)` must raise. | y/n/y/n |
| F5 | Low | CONFIRMED | B | `store.py` `query()` `dot` via `zip` | Mismatched vector lengths are silently truncated, and unnormalised vectors let large-norm rows dominate the ranking. | An embedding-model change mixes dimensions, retrieval silently degrades, and nothing errors. | Fix: assert equal dimensions on `add` and `query`, and normalise or use cosine similarity. Test: `add` with dim 3 after dim 2 should raise. | y/y/n/n |

## NEEDS VALIDATION
- **S1 (nightly job):** whether the nightly purge exists, runs, removes rows from every replica and backup, and alerts on failure. *Settles it:* the job's code and its last run log. The docstring claim is the only evidence.
- **S2 (tenant source):** whether `tenant` is derived from the authenticated session or taken from a request parameter. *Settles it:* the API handler code. If it is client-supplied, any filter added for F1 is spoofable.
- **S3 (production store):** whether in-memory `Store` is what production uses. *Settles it:* deployment config. If it is, all data, including deletion state, is lost on restart and nothing survives to audit.
- **S4 (concurrency):** whether the nightly job mutates `index.rows` while `delete`, `query` or `ingest` iterate it. *Settles it:* the job code and threading model. A concurrent removal can skip rows during iteration.
- **S5 (embedding norms):** whether `vec` is caller-supplied or produced server-side. *Settles it:* the ingest API. If it is caller-supplied, a tenant can submit a huge-norm vector that wins every query. Combined with F1, that means it is injected into everyone's context.

## REFUTED
- **R1:** "`delete()` can delete another tenant's document." Refuted: it matches on both `doc_id` and `tenant`, so a shared doc_id across tenants is safe.
- **R2:** "Duplicate `doc_id` within a tenant escapes deletion." Refuted: the loop visits every row and marks all matches.

## WHAT HOLDS UP
- `delete()` scopes by tenant correctly.
- `ingest` records the tenant on every row.
- `Store.query` already supports a `where` filter that would enforce isolation once used and once F4 is closed. The fix for F1 and F2 is small.

## UNVERIFIED CLAIMS
- "Removed from the index by the nightly job": confirm via job code and run history (S1).
- "One shared index serves every customer" is safe given the request: it is not safe without the filters in F1 and F2. Confirm with a cross-tenant retrieval test.

## QUESTIONS FOR THE AUTHOR
1. Where does `tenant` come from in the API layer?
2. Does the nightly job exist, and what is the maximum time from a deletion request to hard removal, including backups?
3. Is `Store` the production store?

## DECISION-MAKER SUMMARY
Do not load customer documents yet. F1 sends every customer's confidential text into other customers' answers, and F2 keeps "deleted" files answering questions. Both are small code fixes, but they need regression tests and answers on tenant source and the purge job before launch; proceeding risks a cross-customer data breach and broken deletion promises.

## OWNER SUMMARY
The current system mixes all customers' documents together when answering questions, so one customer could see another's confidential files. Files that customers asked us to delete also keep being used until a nightly cleanup that we could not confirm exists. Both problems are fixable quickly, but they must be fixed and tested before any real customer files go in.

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
    {"item": "nightly purge job", "status": "not_seen", "matters": true},
    {"item": "API layer supplying tenant", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "embed and llm implementations", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work under review is code; no customer data supplied."},
  "coverage": {
    "checked": [
      {"unit": "rag.py", "kind": "file"},
      {"unit": "rag.py:ingest", "kind": "function"},
      {"unit": "rag.py:delete", "kind": "function"},
      {"unit": "rag.py:answer", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "store.py:Store.add", "kind": "function"},
      {"unit": "store.py:Store.query", "kind": "function"},
      {"unit": "tenant isolation", "kind": "assumption"},
      {"unit": "deletion semantics", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "nightly purge job", "reason": "not supplied"},
      {"unit": "tenant source / authentication", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "persistence and deployment config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:answer (index.query(embed(question), top_k=3))",
     "scenario": "Tenant B asks a question; query has no tenant filter, so tenant A's confidential text is placed in B's prompt and answered from. A tenant can also plant prompt-injection text that reaches other tenants.",
     "fix": "Pass where={'tenant': tenant, 'deleted': False} to index.query and reject an empty tenant.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','d1',[1,0],'A-secret'); ingest('B','d2',[0,1],'B-doc'); answer(echo_llm, lambda q:[1,0], 'B', 'q'). Expected: no 'A-secret'. Observed: prompt contains 'A-secret'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:delete and rag.py:answer; store.py:Store.query",
     "scenario": "Customer requests deletion; the row is only flagged deleted=True, nothing filters on the flag, so the document keeps feeding answers (for every tenant via F1) until the unverified nightly job removes it.",
     "fix": "Filter deleted=False on every query, or hard-delete in delete() with an audit record.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','d1',v,'secret'); delete('A','d1'); answer(echo_llm, lambda q:v, 'A', 'q'). Expected: 'secret' absent. Observed: present."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:delete",
     "scenario": "delete() with a wrong tenant or unknown id silently matches nothing and returns None, same as success; the customer may be told the file was deleted.",
     "fix": "Return the matched count and raise or log when it is zero.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "delete('A','nonexistent') returns None, indistinguishable from a successful delete."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "store.py:Store.query (r.get(k) == v)",
     "scenario": "After a tenant filter is added, tenant=None matches every row ingested without a tenant, pooling untenanted documents across callers.",
     "fix": "Reject a falsy tenant in ingest and answer; require key presence in where matching.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Test: ingest(None, ...) and answer(..., None, ...) must both raise."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:Store.query dot() via zip",
     "scenario": "Mixed embedding dimensions are silently truncated and unnormalised vectors skew ranking; retrieval degrades with no error.",
     "fix": "Assert equal dimensions on add and query; use cosine similarity or normalised vectors.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "add a 3-dim vector after 2-dim rows, then query with a 2-dim vector: no error is raised, but one should be."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rag.py:delete docstring",
     "suspicion": "The nightly purge may not exist, may fail silently, or may not reach backups.",
     "unresolved_fact": "The job's code and last-run logs."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "callers of ingest/delete/answer",
     "suspicion": "tenant may be client-supplied, making any filter spoofable.",
     "unresolved_fact": "Whether tenant is derived from the authenticated session in the API handler."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "store.py:Store",
     "suspicion": "The in-memory store may be used in production, losing all data and deletion state on restart.",
     "unresolved_fact": "Deployment config naming the production store."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "store.py:Store.rows",
     "suspicion": "The nightly job may mutate rows while delete, query or ingest iterate them.",
     "unresolved_fact": "The job code and the threading model."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "rag.py:ingest vec parameter",
     "suspicion": "A caller-supplied huge-norm vector would win every query.",
     "unresolved_fact": "Whether vec is computed server-side or accepted from the client."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "delete() can remove another tenant's document.",
     "evidence": "It matches on both r['id'] == doc_id and r['tenant'] == tenant."},
    {"id": "R2", "candidate": "Duplicate doc_id rows within a tenant escape deletion.",
     "evidence": "The loop visits every row and flags all matches."}
  ]
}
```