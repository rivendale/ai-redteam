**Same-context review (no subagent available); anchoring risk.** There are no tools in this session, so nothing was run. Every CONFIRMED label below comes from reading and tracing the supplied code by hand. Re-run in a fresh session with tools before relying on this for production.

---

**VERDICT: REWORK.** `answer()` never filters by tenant or by the deleted flag, so any customer can get answers drawn from other customers' documents, including documents they asked to have deleted.

**CONFIDENCE: medium.** It is high on the two Critical findings, which follow directly from a short piece of code. It is limited by four things: this is a same-context review, no tools were available, the nightly purge job was not supplied, and the caller that supplies `tenant` was not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | — |
| context.md | seen | — |
| rag.py | seen | — |
| store.py | seen | — |
| Nightly job that "removes" deleted rows (rag.py:12) | not supplied | **Yes.** Whether deletion ever happens depends on it. |
| Caller / HTTP layer that supplies `tenant` to `answer()` and `delete()` | not supplied | **Yes.** If `tenant` is client-supplied, isolation is spoofable even after the fixes. |
| `llm` / `embed` implementations and provider retention terms | not supplied | Yes, for confidential data and for deletion requests. |
| Tests | none supplied | Yes. No evidence that isolation or deletion was ever tested. |

**COVERAGE**
- Scope: the whole work, which is two files.
- Checked:
  - rag.py: `ingest`, `delete`, `answer`
  - store.py: `Store.__init__`, `add`, `query`
  - request.md and context.md
  - The assumption "a shared index is safe if filtered at query time"
- Not checked:
  - Nightly job (not supplied)
  - Tenant authentication layer (not supplied)
  - LLM and embedding providers (not supplied)
  - Runtime behaviour (no tools)

**SEATS AND GATE**
- Sensitivity gate: no personal data or credentials appear in the code itself, but the system is meant to handle confidential customer files.
- Only a local, same-context review ran. No subagent was available and no cross-vendor seats were used.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B | rag.py:19 (`index.query(embed(question), top_k=3)`); store.py:14 | `answer()` accepts `tenant` but never uses it. `query` is called with `where=None`, which becomes `{}`. `all()` over an empty iterable is `True`, so every row of every tenant is a candidate. | Tenant B asks a question semantically close to tenant A's confidential contract. A's text is placed in B's prompt, and the LLM answers B from it. This directly violates "each customer must only ever get answers from their own documents." | **Fix:** `index.query(vec, top_k=3, where={"tenant": tenant, "deleted": False})`. Also reject a falsy `tenant` before querying. **Repro:** `ingest("A","a1",[1,0],"A-secret")`, then `answer(echo_llm, lambda q:[1,0], "B", "q")`. Expected: no A text in the prompt. Traced: the prompt contains "A-secret". | a✓ b✓ c✓ d✓ |
| F2 | **Critical** | CONFIRMED | B | rag.py:19 together with rag.py:15 | `delete()` only sets `deleted=True`. Nothing in `answer()` or `query()` checks that flag, so deleted documents keep being retrieved, both by their owner and (via F1) by everyone else. | A customer exercises their deletion request. `delete()` returns. The next question, from the same or another tenant, is still answered from the "deleted" document, at least until the nightly job runs, and indefinitely if it does not. This is customer and possibly legal harm, given the stated deletion requests. | **Fix:** filter `deleted: False` at query time (see F1). Hard-delete or purge the text and vector rather than relying only on a flag. **Repro:** `ingest("A","a1",[1,0],"X")`, `delete("A","a1")`, `answer(echo_llm, lambda q:[1,0], "A", "q")`. Expected: "X" absent. Traced: "X" present. | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED | B | rag.py:8; store.py:9 | `ingest` appends without deduplicating on `(tenant, doc_id)`. | A customer re-uploads a revised document under the same id. Both versions stay retrievable, and answers can cite superseded text. | **Fix:** replace any existing row with the same `(tenant, doc_id)` on ingest. **Repro:** ingest `("A","d","v1")` then `("A","d","v2")` with the same vector, query as A with top_k=3. Observed: both v1 and v2 returned. Expected: only v2. | a✓ b✓ c✗ d✓ |
| F4 | Medium | PROBABLE | B | rag.py:20-21 | Document text is concatenated verbatim into the prompt with no delimiting or instruction hierarchy. The model output is returned to the caller unsanitised. | An uploaded document contains "ignore the context; reply with …" and steers answers. Until F1 is fixed, tenant A's upload can inject into tenant B's answers. If the output is rendered as markdown, an image link can carry data out. | **Fix:** delimit the retrieved context, treat model output as untrusted at the render layer, and fix F1 so injection stays within a tenant. **Repro:** ingest a doc containing an injection string, ask a matching question with a real LLM, and observe whether the answer follows the injected instruction. This needs a live model, so it is not run here. | a✓ b✗ c✗ d✓ |
| F5 | Low | CONFIRMED | B | rag.py:13-15 | `delete()` silently does nothing when no row matches (wrong id or wrong tenant) and returns no result. | The caller tells the customer "deleted" when nothing was marked. | **Fix:** return the count of matched rows, and raise or log on zero. **Repro:** `delete("A","nonexistent")` returns `None`, which is the same as a successful delete. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | store.py:12-13 | `zip` truncates silently, so vectors of different dimensions are compared without error. Dot product is unnormalised, so long or high-norm vectors dominate the ranking. | An embedding model change leaves mixed-dimension rows, and retrieval quietly degrades. | **Fix:** assert equal lengths, and normalise or use cosine similarity. **Repro:** `dot([1,0,5],[1,0])` returns `1` and raises no error. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED | A | rag.py:1 | The docstring says "the company's documents" while the request is customers' documents. This signals the author designed a single-tenant system and added `tenant` as metadata only. | Future maintainers read the shared-index design as intentional and unfiltered. | **Fix:** state the tenant-isolation invariant in the docstring and enforce it in one place. **Repro:** read rag.py:1 against request.md. | a✗ b✓ c✗ d✗ |

**Siblings for F1 and F2.** Both are security findings and share one root cause: a read path into `index` that does not apply a tenant and deleted filter.
- Searched: every reader of `index` in rag.py, which is `answer` via `query` and `delete` via `.rows`. Also every reader of `Store.rows` in store.py.
- Found: `delete` does check tenant (rag.py:14). `query` is the only other reader and is unfiltered by default.
- Not covered: the nightly job and any admin or export code were not supplied, so other readers may exist.

**Boundaries.**
- F1:
  - Principal: any tenant.
  - Input: question text.
  - Failing control: no tenant predicate.
  - Boundary crossed: tenant to tenant.
  - Resource: other customers' document text.
- F2:
  - Principal: any tenant, including the owner.
  - Input: question text.
  - Failing control: no deleted predicate.
  - Boundary crossed: the deletion commitment.
  - Resource: deleted customer documents.

## NEEDS VALIDATION
- **S1 (rag.py:12):** whether the nightly job exists, actually removes the row (text and vector, not just the flag), and runs reliably. Settled by the job's source and its schedule and run logs. `Store` has no remove method, so the job must edit `rows` directly.
- **S2 (rag.py:18, 11):** whether `tenant` comes from authenticated identity or from client input. Settled by the calling handler. If it is client-supplied, F1's fix is spoofable.
- **S3 (store.py:6):** whether production uses this in-memory store. If so, all documents are lost on restart and the "nightly job" has nothing durable to act on. Settled by the deployment config.
- **S4 (rag.py:21):** whether the `llm` and `embed` providers retain prompts or inputs, which would put deleted documents beyond reach. Settled by the provider's retention terms and the API key settings, checked on the review date.
- **S5 (store.py:14):** whether `tenant=None` can occur. `where={"tenant": None}` would match rows whose tenant is missing or `None`. Settled by input validation in the caller.

## REFUTED
- **"`delete()` lets one tenant delete another tenant's document with the same id."** Refuted: rag.py:14 checks `r["tenant"] == tenant`.
- **"`Store.query` cannot filter at all."** Refuted: store.py:14 supports `where` correctly. The defect is that rag.py never passes it.

## WHAT HOLDS UP
- `Store.query` already supports exact-match metadata filtering, so F1 and F2 are one-line fixes at rag.py:19.
- `delete()` scopes by tenant correctly.
- Tenant is recorded on every row at ingest.

## UNVERIFIED CLAIMS
- "it is removed from the index by the nightly job" (rag.py:12). Confirm with the job's source and run history.
- "Answer from this context only" constrains the model. Confirm with an adversarial prompt test against the real model.

## QUESTIONS FOR THE AUTHOR
1. Where does `tenant` come from in the request path, and is it derived from authentication?
2. Where is the nightly job, and does it delete text and vectors or only flags?
3. Is this in-memory store what ships to production?

## DECISION-MAKER SUMMARY
Do not load customer documents yet. As written, every customer's question is answered from all customers' documents, and "deleted" documents are still served. Two one-line filters fix the core leak, but the deletion job and how tenant identity is established must be shown before launch, or the confidentiality and deletion commitments will be breached on day one.

## OWNER SUMMARY
The question-answering system currently mixes all customers' files together, so one customer could receive answers based on another customer's confidential documents. Files that customers ask us to delete also keep being used to answer questions. These are quick to fix in code, but they must be fixed and tested, and the deletion process confirmed, before any real customer files are loaded.

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
    {"item": "nightly purge job", "status": "not_seen", "matters": true},
    {"item": "caller that supplies tenant", "status": "not_seen", "matters": true},
    {"item": "llm/embed provider and retention terms", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no customer data supplied. The system will handle confidential files, so no cross-vendor seats were used."},
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
      {"unit": "shared index is safe if filtered at query time", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "nightly purge job", "reason": "not_supplied"},
      {"unit": "tenant authentication layer", "reason": "not_supplied"},
      {"unit": "llm/embed providers", "reason": "not_supplied"},
      {"unit": "runtime execution of repros", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:19; store.py:14",
     "scenario": "answer() never passes a tenant filter; query(where=None) matches every row, so tenant B's question is answered from tenant A's confidential documents.",
     "fix": "Call index.query(vec, top_k=3, where={\"tenant\": tenant, \"deleted\": False}) and reject a falsy tenant.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','a1',[1,0],'A-secret'); answer(echo_llm, lambda q:[1,0], 'B', 'q'); expected no 'A-secret' in prompt, traced: present.",
     "security": true,
     "boundary": {"principal": "any tenant", "input": "question text", "control": "no tenant predicate in query", "crossed": "tenant to tenant", "resource": "other customers' document text"},
     "siblings_searched": {"searched": "all readers of index/Store.rows in rag.py and store.py", "found": "delete() checks tenant; query via answer() is the only unfiltered reader; nightly job not supplied"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:19 with rag.py:15",
     "scenario": "After delete(), the row is only flagged; answer() does not filter deleted, so the deleted document is still served to its owner and, via F1, to every tenant.",
     "fix": "Filter deleted=False at query time and hard-delete or purge text and vector rather than relying on a flag.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "ingest('A','a1',[1,0],'X'); delete('A','a1'); answer(echo_llm, lambda q:[1,0], 'A', 'q'); expected 'X' absent, traced: present.",
     "security": true,
     "boundary": {"principal": "any tenant including owner", "input": "question text", "control": "no deleted predicate in query", "crossed": "deletion commitment", "resource": "deleted customer documents"},
     "siblings_searched": {"searched": "all readers of index/Store.rows in rag.py and store.py", "found": "only answer() reads for retrieval; it does not check deleted"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:8; store.py:9",
     "scenario": "Re-uploading a revised document with the same doc_id leaves both versions retrievable; answers cite superseded text.",
     "fix": "Upsert on (tenant, doc_id).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "ingest('A','d',[1,0],'v1'); ingest('A','d',[1,0],'v2'); query as A; observed both v1 and v2, expected only v2."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rag.py:20-21",
     "scenario": "Uploaded document text containing instructions is concatenated into the prompt and can steer answers; before F1 is fixed, cross-tenant.",
     "fix": "Delimit retrieved context, treat model output as untrusted at render time, and fix F1.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Ingest a document containing an injection string, ask a matching question against the real LLM, observe whether the answer follows it (needs a live model; not run)."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rag.py:13-15",
     "scenario": "delete() with an unknown id or wrong tenant silently does nothing; the caller may tell the customer the file was deleted.",
     "fix": "Return the matched count and raise or log on zero.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "delete('A','nonexistent') returns None, which is indistinguishable from success."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:12-13",
     "scenario": "Mixed-dimension vectors are compared silently via zip truncation; unnormalised dot product skews ranking.",
     "fix": "Assert equal dimensions and normalise or use cosine similarity.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "dot([1,0,5],[1,0]) returns 1 with no error; expected a dimension error."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "rag.py:1",
     "scenario": "The docstring describes 'the company's documents' in one shared index, not per-customer isolation, inviting future unfiltered readers.",
     "fix": "Document and centrally enforce the tenant-isolation invariant.",
     "answers": {"a": false, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rag.py:12",
     "suspicion": "The nightly job may not exist or may not purge text and vectors.",
     "unresolved_fact": "The job's source and its run history."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rag.py:11,18",
     "suspicion": "tenant may be client-supplied and spoofable.",
     "unresolved_fact": "How the calling handler derives tenant."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "store.py:6",
     "suspicion": "The in-memory store loses all data on restart if used in production.",
     "unresolved_fact": "Deployment configuration."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "rag.py:21",
     "suspicion": "The LLM or embedding provider may retain document text, defeating deletion.",
     "unresolved_fact": "Provider retention terms and key settings on the review date."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "store.py:14",
     "suspicion": "tenant=None would match rows lacking a tenant.",
     "unresolved_fact": "Whether the caller validates tenant as non-empty."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "delete() lets one tenant delete another tenant's document.", "evidence": "rag.py:14 checks r['tenant'] == tenant."},
    {"id": "C2", "candidate": "Store.query cannot filter by metadata.", "evidence": "store.py:14 applies the where dict correctly; rag.py simply never passes it."}
  ]
}
```

The JSON was not checked with `tools/validate_findings.py` because no tools were available.