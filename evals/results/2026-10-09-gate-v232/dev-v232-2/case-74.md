VERDICT: **REWORK**. `answer()` never filters by tenant and never filters out deleted rows, so any customer can get answers built from another customer's documents, including documents that customer asked to delete.

CONFIDENCE: **medium**. The two blocking defects are certain from tracing the supplied code. Confidence is limited because:
- I had no tools, so nothing was run and the reproductions below are traced, not executed.
- The caller and authentication layer, the nightly deletion job, `llm` and `embed`, and any tests were not supplied.
- This is a single-reviewer review with no fresh subagent. The work was not authored in this conversation, so it carries no author-context anchoring, but there is no second seat.

INPUTS LEDGER:
- **Seen:** request.md, context.md, rag.py, store.py.
- **Not seen, and it matters:**
  - The code that calls `answer`, `ingest` and `delete`, and where `tenant` comes from (an authenticated session or a client-supplied field).
  - The nightly removal job named in the `delete` docstring.
  - The `llm` and `embed` implementations and their retention terms.
  - Any tests.
- **Not seen, and it does not matter:** none.

COVERAGE:
- **Scope:** the whole work (2 files).
- **Checked:**
  - Documents and files: request.md, context.md, rag.py, store.py.
  - Functions: `rag.ingest`, `rag.delete`, `rag.answer`, `Store.add`, `Store.query`.
  - Assumptions: "each customer only their own documents" and "deletion honoured".
- **Not checked:** the caller and auth layer, the nightly job, `llm`/`embed`, and tests (all `not_supplied`). Runtime behaviour was not checked (`no_tools`).

SEATS AND GATE:
- Seats: a single local reviewer ran. No cross-vendor seats were requested.
- Gate: the code contains no sensitive data, but the context says production customer files will flow through it. Any future review that includes real documents must stay on approved endpoints.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | rag.py `answer`, line `index.query(embed(question), top_k=3)` | The `tenant` argument is accepted but never used. The query runs over the single shared index with no `where`. | Tenants A and B both ingest. B asks a question semantically close to A's document. A's text lands in `context` and is sent to the LLM, which answers B from it. This happens on every query whenever another tenant's vector scores higher, so it is not an edge case. | **Fix:** `index.query(embed(q), top_k=3, where={"tenant": tenant, "deleted": False})`. `Store.query` already supports `where`.<br>**Reproduction:**<br>1. Run `ingest("A","a1",[1,0],"A-secret")` and `ingest("B","b1",[0,1],"B-doc")`.<br>2. Call `answer(llm=lambda p:p, embed=lambda q:[1,0], tenant="B", question="x")`.<br>3. Expected: the prompt lacks "A-secret". Observed (traced): it contains "A-secret". | y/y/y/y |
| F2 | Critical | CONFIRMED | B | rag.py `delete` (sets `deleted=True`) together with `answer` / `Store.query` (no `deleted` filter) | Deletion only sets a flag. Nothing on the read path checks the flag, so deleted documents keep being served until the nightly job runs, and the job was not supplied. | A customer asks for a file to be deleted and gets confirmation. Hours later, they or another tenant (via F1) receive answers quoting it, and its text is sent to the LLM again. This breaks the explicit customer deletion requests in context.md. | **Fix:** filter `deleted: False` in the query, as in F1. Better, also remove the row immediately (`index.rows = [r for r in index.rows if not (...)]`) rather than relying on the nightly job.<br>**Reproduction:**<br>1. Run `ingest("A","a1",[1,0],"gone")` then `delete("A","a1")`.<br>2. Call `answer(lambda p:p, lambda q:[1,0], "A", "x")`.<br>3. Expected: "gone" is absent. Observed (traced): it is present. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | store.py class docstring and `self.rows = []` | The index is a process-local Python list. A restart, crash or deploy empties it, and multiple workers each hold a different index. | After a deploy, every tenant gets answers from empty context, which is silent wrong output. Under multi-worker serving, an ingest on worker 1 is invisible to a query on worker 2, and a `delete` on one worker leaves the row live on another. That compounds F2. | **Fix:** use a persistent store with tenant-filtered queries and real deletes, or document this as a prototype not fit for the production load in context.md.<br>**Reproduction:** ingest, restart the process, call `answer`. Expected: the document is found. Observed: the context is empty. | y/y/n/y |
| F4 | Low | CONFIRMED | B | rag.py `answer`, prompt construction | Retrieved text and the question are concatenated with no delimiting. When retrieval is empty, the model is still called with an empty context. | A tenant's own uploaded file containing "ignore the above…" steers that tenant's answers. Combined with F1, one tenant's document can steer another tenant's answers. With empty context, the model may answer from its own knowledge despite the instruction. | **Fix:** delimit and label untrusted context, and return "no answer found" when `hits` is empty instead of calling the model.<br>**Reproduction:** with an empty index, call `answer(lambda p:p, lambda q:[1], "A", "x")`. The prompt is sent with no context lines. | y/y/n/n |
| F5 | Low | CONFIRMED | B | rag.py `delete` | The function reports nothing. A wrong `doc_id` or `tenant` silently deletes nothing. | A deletion request with a mistyped ID shows the customer success while the document stays live. | **Fix:** return the count marked and raise or return an error on 0.<br>**Reproduction:** run `delete("A","nope")`. It returns `None`, the same result as a successful delete. | y/y/n/n |

**Siblings for F1 and F2.** I searched every read of `index.rows` and every caller of `index.query` in both files.
- `answer` is the only query caller, so there are no further siblings.
- `delete` does check `r["tenant"] == tenant`. That is a positive control: the author knew the tenant check was needed and applied it on the write path but not the read path.
- `Store.query`'s `where` matching (`r.get(k) == v`) works correctly once a `where` is passed.

**Security and boundary.** Both F1 and F2 are security findings.
- **F1.** Principal: any tenant able to ask a question. Input: the question text. Control that fails: the tenant filter is absent. Boundary crossed: tenant to tenant. Resource: every other tenant's document text.
- **F2.** Principal: any tenant, including the deleting tenant itself. Input: the question. Control that fails: the deleted flag is never checked on read. Boundary crossed: the deletion commitment. Resource: documents the customer asked to delete.

## Needs validation

- **Where `tenant` comes from.** Even with F1 fixed, if callers take `tenant` from the request body rather than the authenticated session, any user can name another tenant. This is settled by the caller and auth code.
- **Whether the nightly job exists and hard-deletes.** Also whether it covers vectors and any copies. This is settled by the job's code and schedule.
- **Whether `llm` or `embed` providers retain prompts.** If they do, deleted document text already sent to them persists outside this system. This is settled by provider retention terms and API configuration (for example zero-retention keys).
- **Tenant value validation.** `tenant=None` or `""` at ingest would put documents into a shared pseudo-tenant that any caller passing the same value can read. This is settled by input validation at the caller.

## Refuted

- **Cross-tenant deletion via a colliding `doc_id`.** Refuted: `delete` requires both `id` and `tenant` to match.
- **`Store.query` lacks filtering, so the fix needs new code.** Refuted: a `where` parameter exists and matches on equality.

## What holds up

- `delete` scopes by tenant correctly.
- `ingest` records the tenant on every row.
- The store already has the filter hook needed for the fix.

## Unverified claims

- The `delete` docstring says documents are "removed from the index by the nightly job". No such job was supplied; confirm by reading it and checking its run logs.
- The work presents itself as question answering for customers, but there are no tests showing isolation. Confirm with a two-tenant test that fails on current code and passes after the fix.

## Questions for the author

1. Is `tenant` derived from the authenticated session, never from client input?
2. Does the nightly job exist, and does it physically remove rows everywhere, including in every worker's index?
3. What is the production store? Is this in-memory list a placeholder?

## Decision-maker summary

Do not load customer documents yet. F1 means any customer can receive another customer's confidential text, and F2 means "deleted" files keep being served. Both are one-line query fixes plus a two-tenant test and a delete test. Proceeding as-is risks a cross-customer data breach on the first day of use.

## Owner summary

As written, the system can answer one customer's question using another customer's confidential files, and it keeps using files customers have asked to delete. The fix is small: limit every search to the asking customer's own, non-deleted files, and add tests that prove it. Hold off on loading real customer documents until that is done and confirmed.

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
    {"item": "caller/auth code supplying tenant", "status": "not_seen", "matters": true},
    {"item": "nightly deletion job", "status": "not_seen", "matters": true},
    {"item": "llm and embed implementations", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no customer data supplied to the review."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "rag.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "rag.py:ingest", "kind": "function"},
      {"unit": "rag.py:delete", "kind": "function"},
      {"unit": "rag.py:answer", "kind": "function"},
      {"unit": "store.py:Store.add", "kind": "function"},
      {"unit": "store.py:Store.query", "kind": "function"},
      {"unit": "each customer only gets answers from their own documents", "kind": "assumption"},
      {"unit": "deleted documents are no longer used", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "caller/auth code supplying tenant", "reason": "not_supplied"},
      {"unit": "nightly deletion job", "reason": "not_supplied"},
      {"unit": "llm and embed implementations", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime execution of reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:answer (index.query(embed(question), top_k=3))",
     "scenario": "Tenant B asks a question semantically close to tenant A's document; the unfiltered shared-index query returns A's text, which is sent to the LLM and used to answer B.",
     "fix": "Query with where={\"tenant\": tenant, \"deleted\": False}; add a two-tenant isolation test.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','a1',[1,0],'A-secret'); ingest('B','b1',[0,1],'B-doc'); answer(lambda p:p, lambda q:[1,0], 'B', 'x') -> expected prompt without 'A-secret', traced result contains it.",
     "security": true,
     "boundary": {"principal": "any tenant able to ask a question", "input": "the question text", "control": "no tenant filter on index.query; tenant argument unused", "crossed": "tenant to tenant", "resource": "every other tenant's document text"},
     "siblings_searched": {"searched": "all callers of index.query and readers of index.rows in rag.py and store.py", "found": "answer() is the only query caller; delete() correctly checks tenant"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:delete (sets deleted=True) and rag.py:answer / store.py:Store.query (no deleted filter)",
     "scenario": "A customer deletes a file; until an unsupplied nightly job runs, the soft-deleted row still ranks in queries and its text is served in answers and sent to the LLM.",
     "fix": "Filter deleted=False on every query and physically remove the row in delete(); add a delete-then-answer test.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','a1',[1,0],'gone'); delete('A','a1'); answer(lambda p:p, lambda q:[1,0], 'A', 'x') -> expected no 'gone', traced result contains it.",
     "security": true,
     "boundary": {"principal": "any tenant, including the deleting tenant (and others via F1)", "input": "the question text", "control": "deleted flag never checked on read", "crossed": "customer deletion commitment", "resource": "documents customers asked to delete"},
     "siblings_searched": {"searched": "every read path over index.rows in rag.py and store.py", "found": "Store.query is the only read path and has no deleted filter"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:Store.__init__ (self.rows = [])",
     "scenario": "A restart or deploy empties the in-memory index, so answers run on empty context; under multiple workers, ingests and deletes on one worker are invisible to others.",
     "fix": "Use a persistent, shared store with tenant-filtered queries and hard deletes, or mark this as a non-production prototype.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "ingest a document, restart the process, call answer -> expected document found, observed empty context."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:answer (prompt string concatenation)",
     "scenario": "Retrieved document text is concatenated undelimited, so instructions inside a document can steer answers; with no hits the model is still called with empty context and may answer from its own knowledge.",
     "fix": "Delimit and label untrusted context; return 'no answer found' when hits is empty.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With an empty index, answer(lambda p:p, lambda q:[1], 'A', 'x') returns a prompt with no context lines; the model would still be called."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:delete",
     "scenario": "A delete with a wrong doc_id or tenant matches nothing and returns None, indistinguishable from success, so the customer is told the file is deleted.",
     "fix": "Return the number of rows removed and raise or return an error when it is 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "delete('A','nope') returns None, the same as a successful delete."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "callers of rag.answer (not supplied)",
     "suspicion": "tenant may be taken from client input, letting a user name another tenant even after F1 is fixed.",
     "unresolved_fact": "Whether tenant is derived from the authenticated session in the caller code."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "nightly deletion job (not supplied)",
     "suspicion": "The job may not exist or may not hard-delete rows in every worker's index.",
     "unresolved_fact": "The job's code, schedule and run logs."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "llm and embed providers (not supplied)",
     "suspicion": "Providers may retain prompts, so deleted document text persists outside the system.",
     "unresolved_fact": "Provider retention terms and API configuration (for example zero-retention keys)."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rag.py:ingest (tenant argument)",
     "suspicion": "tenant=None or '' would create a shared pseudo-tenant readable by any caller passing the same value.",
     "unresolved_fact": "Whether callers validate tenant before calling ingest and answer."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A colliding doc_id lets one tenant delete another tenant's document.",
     "evidence": "delete() requires both r['id'] == doc_id and r['tenant'] == tenant."},
    {"id": "R2", "candidate": "Store.query lacks filtering, so the fix needs new store code.",
     "evidence": "Store.query already accepts where= and matches on equality."}
  ]
}
```

The JSON follows schema 2.3 and contains `verdict` and `findings` as the output note requests. The `needs_validation` entries carry no severity, as the skill requires. I could not run `tools/validate_findings.py` in this session.